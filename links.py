#!/usr/bin/env python

"""
A module for extracting links from wikipedia using wikipedia's External links
search: http://en.wikipedia.org/w/index.php?title=Special:LinkSearch
"""

import sys
import urllib2

import BeautifulSoup

url = 'http://%s.wikipedia.org/w/index.php?title=Special:LinkSearch&target=%s&limit=%s&offset=%s'

def links(site, lang='en', page_size=500, offset=0):
    """
    a generator that returns a source, target tuples where source is the
    url for a document at wikipedia and target is a url for a document at 
    a given site
    """
    wikipedia_host = 'http://%s.wikipedia.org' % lang
    while True:
        req = urllib2.Request(url % (lang, site, page_size, offset))
        req.add_header('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)')
        html = urllib2.urlopen(req).read()

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

if __name__ == '__main__':
    host = sys.argv[1]
    for source, target in links(host):
        print source, target
