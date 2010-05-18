"""
Functions for getting info from wikipedia.
"""

import re
import sys
import json
import urllib
import logging
import urllib2

import BeautifulSoup

def url_to_title(url):
    match = re.match(r'http://.+/wiki/(.+)$', url)
    if match:
        return match.group(1)
    else:
        return None

def info(title):
    logging.info("looking up info for %s at wikipedia" % title)
    q = {'action': 'query', 
         'prop': 'info', 
         'titles': title,
         }
    return _api(q)

def categories(title):
    logging.info("looking up categories for %s" % title)
    q = {'action': 'query',
         'prop': 'categories',
         'titles': title,
         }
    try:
        return _api(q)['categories']
    except KeyError:
        return []
    

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
    response = _fetch(url + '?' + urllib.urlencode(params))
    data = json.loads(response)
    first_page_key = data['query']['pages'].keys()[0]
    return data['query']['pages'][first_page_key]

def _fetch(url):
    req = urllib2.Request(url)
    req.add_header('User-agent', 'linkpyediabot v0.1: http://github.com/edsu/linkypedia')
    return urllib2.urlopen(req).read()
