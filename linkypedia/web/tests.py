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
        self.assertTrue(len(extlinks) > 10)
        for link in extlinks:
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
