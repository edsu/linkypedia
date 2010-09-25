import urllib2
import urlparse
import cStringIO

from django.core.management.base import BaseCommand
from lxml import etree

from linkypedia.crawl import crawl
from linkypedia.wikipedia import _fetch
from linkypedia.web import models as m

class Command(BaseCommand):

    def handle(self, url, **options):
        websites = m.Website.objects.filter(url=url)
        if websites.count() > 0:
            print "website for %s already exists"
        else:
            website = self._setup_new_website(url)
            print "created new website %s" % website

    def _setup_new_website(self, url):
        if not url.startswith('http://'):
            url = "http://" + url

        host = urlparse.urlparse(url).netloc

        # try to get the title from the html
        parser = etree.HTMLParser()
        html = cStringIO.StringIO(_fetch(url))
        doc = etree.parse(html, parser)
        title = doc.xpath('/html/head/title')
        if len(title) > 0:
            name = title[0].text
            if ' - ' in name:
                name = name.split(' - ')[0]
        else:
            name = host

        website = m.Website.objects.create(url=url, name=name)

        # try to get the favicon
        favicon_url = 'http://%s/favicon.ico' % host
        try: 
            urllib2.urlopen(favicon_url)
            website.favicon_url = favicon_url
        except:
            pass # no favicon url i guess

        website.save()
        return website
