import datetime

from django.test import TestCase

from linkypedia.wikipedia import api
from linkypedia.web import models as m
import linkdb

class WikipediaTest(TestCase):

    def test_info(self):
        info = api.info('Pierre-Charles_Le_Sueur', 'en')
        self.assertEqual(info['pageid'], 842462)
        self.assertEqual(info['title'], 'Pierre-Charles Le Sueur')

    def test_extlinks(self):
        extlinks = api.extlinks('BagIt', 'en')
        self.assertEqual(extlinks['page_id'], 29172924)
        self.assertEqual(extlinks['namespace_id'], 0)
        self.assertTrue(len(extlinks['urls']) > 10)
        for link in extlinks['urls']:
            self.assertTrue(link.startswith('http'))

class LinkdbTests(TestCase):

    def test_update_links(self):
        # set up an article with some links
        linkdb.init(reset_stats=False)
        import time
        time.sleep(3)
        linkdb.add_article('en', 1, 'Linked_Data')
        links = [
                    "http://www.w3.org/DesignIssues/LinkedData.html",
                    "http://linkddata.org",
                    "http://esw.w3.org/LinkedData",
                    "http://richard.cyganiak.de/2007/10/lod/"
                ]
        for url in links:
            linkdb.add_link('en', 1, url)
       
        # there ought to be four links now
        self.assertEqual(len(linkdb.article_links('en', 1)), 4)

        # now update the links: add a couple new links and remove one
        links = [
                    "http://linkddata.org",
                    "http://www.w3.org/DesignIssues/LinkedData.html",
                    "http://richard.cyganiak.de/2007/10/lod/",
                    "http://www.ted.com/talks/tim_berners_lee_on_the_next_web.html",
                    "http://blog.iandavis.com/2010/12/06/back-to-basics/",
                ]
        created, deleted = linkdb.update_article_links('en', 1, links)
        self.assertEqual(created, 2)
        self.assertEqual(deleted, 1)

        # now there should be 5 links
        self.assertEqual(len(linkdb.article_links('en', 1)), 5)

        # make sure the new links are in there
        new_links = [l[0] for l in linkdb.article_links('en', 1)]
        for link in links:
            self.assertTrue(link in new_links)

        # and that the deleted one is gone
        self.assertTrue("http://esw.w3.org/LinkedData" not in new_links)

    def test_article_id(self):
        self.assertEqual(linkdb.make_article_id("en", 1), "en:0000000001")
        self.assertEqual(linkdb.make_article_id("en", "1"), "en:0000000001")
