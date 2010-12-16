"""
module for interacting with wikipedia
"""

import re
import sys
import json
import time
import urllib
import getpass
import logging
import urllib2

import irclib
import BeautifulSoup

from web import tasks

RETRIES_BETWEEN_API_ERRORS = 5
IRC_MESSAGE_PATTERN = re.compile('\[\[(.+?)\]\] (.+)? (http:.+?)? (?:\* (.+?) \*)? (?:\(([+-]\d+)\))? (.+)?')

log = logging.getLogger()

class WikipediaUpdatesClient(irclib.SimpleIRCClient):
    """Fetch live update feed from irc://irc.wikimedia.org/en.wikipedia
    """

    def on_error(self, connection, event):
        log.error("encountered an irc error: %s" % event)

    def on_created(self, connection, event):
        log.info("joining #en.wikipedia")
        connection.join("#en.wikipedia")

    def on_pubmsg(self, connection, event):
        msg = self._strip_color(event.arguments()[0])
        msg = msg.decode("utf-8")
        log.debug(msg)
        match = IRC_MESSAGE_PATTERN.search(msg)
        if match:
            page, status, diff_url, user, bytes_changed, msg = match.groups()

            # ignore what look like non-articles
            if ':' not in page:
                # add the page to the external link celery queue
                result = tasks.get_external_links.delay(page)
                # wait till we get the response
                page_id, created, deleted = result.get()
                log.info("%s (%s) links created=%s, links deleted=%s" % 
                        (page, page_id, created, deleted))
        else:
            # should never happen
            log.fatal("irc message didn't match regex: %s" % msg)
            connection.close()
            sys.exit(-1)


    def _strip_color(self, msg):
        # should remove irc color coding
        return re.sub(r"(\x03|\x02)([0-9]{1,2}(,[0-9]{1,2})?)?", "", msg)


def start_update_stream(username):
    irc = WikipediaUpdatesClient()
    irc.connect("irc.wikimedia.org", 6667, username)
    irc.start()


def url_to_title(url):
    url = str(url)
    match = re.match(r'http://.+/wiki/(.+)$', url)
    if match:
        return urllib.unquote(match.group(1)).decode('utf-8')
    else:
        return None


def info(title):
    logging.info("wikipedia lookup for page: %s " % title)
    q = {'action': 'query', 
         'prop': 'info', 
         'titles': title,
         }
    return _first(_api(q))


def categories(title):
    logging.info("wkipedia look up for page categories: %s" % title)
    q = {'action': 'query',
         'prop': 'categories',
         'titles': title,
         }
    try:
        return _first(_api(q))['categories']
    except KeyError:
        logging.error("uhoh, unable to find categories key!")
        return []

    
def users(usernames):
    usernames = [u.encode('utf-8') for u in usernames]
    logging.info("wikipedia look up for users: %s" % usernames)
    q = {'action': 'query',
         'list': 'users',
         'ususers': '|'.join(usernames),
         'usprop': 'blockinfo|groups|editcount|registration|emailable|gender',
        }
    return _api(q)['query']['users']


def extlinks(page_title, limit=100, offset=0):
    """returns a dictionary of information about external links for a 
    wikipedia page with a given title. The dictionary should include keys for
    page_id, namespace_id and urls. The page_id is the id for the wikipedia
    page, the namespace_id typically 0 for wikipedia articles), and urls is a 
    list of urls that the particular wikipedia page links to outside of 
    wikipedia.
    """
    page_title = page_title.replace(' ', '_')
    q = {'action': 'query',
         'prop': 'extlinks',
         'titles': page_title,
         'ellimit': limit,
         'eloffset': offset,
        }
    response = _first(_api(q))

    if response.has_key('extlinks'):
        # strip out just the urls from the json response
        urls = [l[u"*"] for l in response['extlinks']]
    else:
        # no links
        urls = []

    # get more if it looks like we might not have gotten them all
    if len(urls) == limit:
        urls.extend(extlinks(page_title, limit, offset + limit))

    return {'page_id': response['pageid'], 'namespace_id': response['ns'], 
            'urls': urls}


def links(site, lang='en', page_size=500, offset=0):
    """
    a generator that returns a source, target tuples where source is the
    url for a document at wikipedia and target is a url for a document at 
    a given site
    """
    links_url = 'http://%s.wikipedia.org/w/index.php?title=Special:LinkSearch&target=%s&limit=%s&offset=%s'
    wikipedia_host = 'http://%s.wikipedia.org' % lang
    while True:
        url = links_url % (lang, site, page_size, offset)
        html = _fetch(url)

        soup = BeautifulSoup.BeautifulSoup(html)
        found = 0
        for li in soup.findAll('li'): 
            a = li.findAll('a')
            if len(a) == 2: 
                found += 1
                yield wikipedia_host + a[1]['href'], a[0]['href']

        if found == page_size:
            offset += page_size
        else:
            break



def _api(params):
    params['format'] = 'json'
    url = 'http://en.wikipedia.org/w/api.php'
    response = _fetch(url, params)
    data = json.loads(response)
    return data


def _first(data):
    # some queries can take a list of things but we are only sending
    # one at a time, and this helper just looks for the first (and only)
    # page in the response and returns it
    first_page_key = data['query']['pages'].keys()[0]
    return data['query']['pages'][first_page_key]


def _fetch(url, params=None, retries=RETRIES_BETWEEN_API_ERRORS):
    if params:
        # not sure why urlencode doesn't handle encoding as utf-8... 
        utf8_params = {}
        for k, v in params.items():
            if type(v) == unicode:
                utf8_params[k] = v.encode('utf-8')
            else:
                utf8_params[k] = v

        req = urllib2.Request(url, data=urllib.urlencode(utf8_params))
        req.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
    else:
        req = urllib2.Request(url)
    req.add_header('User-agent', 'linkpyediabot v0.1: http://github.com/edsu/linkypedia')

    try:
        return urllib2.urlopen(req).read()
    except urllib2.URLError, e:
        return _fetch_again(e, url, params, retries)
    except urllib2.HTTPError, e:
        return _fetch_again(e, url, params, retries)


def _fetch_again(e, url, params, retries):
        logging.warn("caught error when talking to wikipedia: %s" % e)
        retries -= 1
        if retries == 0:
            logging.info("no more tries left")
            raise e
        else: 
            # should back off 10, 20, 30, 40, 50 seconds
            sleep_seconds = (RETRIES_BETWEEN_API_ERRORS - retries) * 10
            logging.info("sleeping %i seconds then trying again %i times" %
                    (sleep_seconds, retries))
            time.sleep(sleep_seconds)
            return _fetch(url, params, retries)
