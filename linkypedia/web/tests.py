import datetime

from django.test import TestCase

from linkypedia import wikipedia
from linkypedia.web import models as m
from linkypedia.crawl import crawl, load_users

class WikipediaTest(TestCase):

    def test_info(self):
        info = wikipedia.info('Pierre-Charles_Le_Sueur')
        self.assertEqual(info['pageid'], 842462)
        self.assertEqual(info['title'], 'Pierre-Charles Le Sueur')

    def test_extlinks(self):
        extlinks = wikipedia.extlinks('BagIt')
        self.assertEqual(extlinks['page_id'], 29172924)
        self.assertEqual(extlinks['namespace_id'], 0)
        self.assertTrue(len(extlinks['urls']) > 10)
        for link in extlinks['urls']:
            self.assertTrue(link.startswith('http'))

    def test_users(self):
        users = wikipedia.users(['edsu', 'nichtich'])
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['name'], 'Edsu')
        self.assertTrue(users[0]['editcount'] > 0)
        self.assertTrue(users[0].has_key('gender'))
        self.assertTrue(users[0].has_key('registration'))
        self.assertEqual(users[1]['name'], 'Nichtich')

    def test_categories(self):
        info = wikipedia.categories('Skull_and_Bones')
        self.assertTrue(len(info) > 1)

class LinkypediaTests(TestCase):

    def test_harvest(self):
        # get a website with some user pages
        website = m.Website(name='Europeana', url='http://www.europeana.eu')
        website.save()
        crawl(website)

        self.assertTrue(m.WikipediaCategory.objects.all().count() > 0)

        created, updated = load_users()
        self.assertTrue(created > 0)
        self.assertEqual(updated, 0)

        self.assertTrue(m.WikipediaUser.objects.all().count() > 1)
        u = m.WikipediaUser.objects.all()[0]
        self.assertTrue(u.edit_count > 0)

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
