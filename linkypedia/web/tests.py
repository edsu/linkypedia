import datetime

from django.test import TestCase

from linkypedia.wikipedia import api
from linkypedia.web import models as m

class WikipediaTest(TestCase):

    def test_info(self):
        info = api.info('Pierre-Charles_Le_Sueur')
        self.assertEqual(info['pageid'], 842462)
        self.assertEqual(info['title'], 'Pierre-Charles Le Sueur')

    def test_extlinks(self):
        extlinks = api.extlinks('BagIt')
        self.assertEqual(extlinks['page_id'], 29172924)
        self.assertEqual(extlinks['namespace_id'], 0)
        self.assertTrue(len(extlinks['urls']) > 10)
        for link in extlinks['urls']:
            self.assertTrue(link.startswith('http'))

class LinkypediaTests(TestCase):

    def test_update_links(self):
        # set up an article with some links
        article = m.Article(title="Linked_Data")
        article.save()

        links = [
                    "http://www.w3.org/DesignIssues/LinkedData.html",
                    "http://linkddata.org",
                    "http://esw.w3.org/LinkedData",
                    "http://richard.cyganiak.de/2007/10/lod/"
                ]

        for l in links:
            m.ExternalLink.objects.create(url=l, article=article)
       
        # tld, host and created should be populated automatically
        l = article.links.all()[0]
        self.assertEqual(l.url,
                "http://www.w3.org/DesignIssues/LinkedData.html")
        self.assertEqual(l.tld, 'org')
        self.assertEqual(l.host, 'www.w3.org')
        self.assertTrue(isinstance(l.created, datetime.datetime))

        # there ought to be four links now
        self.assertEqual(article.links.all().count(), 4)

        # now update the links: add a couple new links and remove one
        links = [
                    "http://linkddata.org",
                    "http://www.w3.org/DesignIssues/LinkedData.html",
                    "http://richard.cyganiak.de/2007/10/lod/",
                    "http://www.ted.com/talks/tim_berners_lee_on_the_next_web.html",
                    "http://blog.iandavis.com/2010/12/06/back-to-basics/",
                ]
        created, deleted = article.update_links(links)
        self.assertEqual(created, 2)
        self.assertEqual(deleted, 1)

        # now there should be 5 links
        self.assertEqual(article.links.all().count(), 5)

        # make sure the new links are in there
        new_links = [l.url for l in article.links.all()]
        for link in links:
            self.assertTrue(link in new_links)

        # and that the deleted one is gone
        self.assertTrue("http://esw.w3.org/LinkedData" not in new_links)
