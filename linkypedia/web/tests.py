from django.test import TestCase

from linkypedia import wikipedia

class WikipediaTest(TestCase):

    def test_info(self):
        info = wikipedia.info('Pierre-Charles_Le_Sueur')
        self.assertEqual(info['pageid'], 842462)
        self.assertEqual(info['title'], 'Pierre-Charles Le Sueur')
