"""
Functions for getting info from wikipedia.
"""

import re
import sys
import json
import time
import urllib
import logging
import urllib2

import BeautifulSoup

retries_between_api_errors = 5

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
         'titles': title.encode('utf-8'),
         }
    return _first(_api(q))

def categories(title):
    logging.info("wkipedia look up for page categories: %s" % title)
    q = {'action': 'query',
         'prop': 'categories',
         'titles': title.encode('utf-8'),
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

def _fetch(url, params=None, retries=retries_between_api_errors):
    if params:
        req = urllib2.Request(url, data=urllib.urlencode(params))
        req.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
    else:
        req = urllib2.Request(url)
    req.add_header('User-agent', 'linkpyediabot v0.1: http://github.com/edsu/linkypedia')

    try:
        return urllib2.urlopen(req).read()
    except urllib2.URLError, e:
        logging.warn("caught error when talking to wikipedia: %s" % e)
        retries -= 1
        if retries == 0:
            logging.info("no more tries left")
            raise e
        else: 
            # should back off 10, 20, 30, 40, 50 seconds
            sleep_seconds = (retries_between_api_errors - retries) * 10
            logging.info("sleeping %i seconds then trying again %i times" %
                    (sleep_seconds, retries))
            time.sleep(sleep_seconds)
            return _fetch(url, params, retries)
