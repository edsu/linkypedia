import os
import sys

from django.core.management.base import BaseCommand

from django.conf import settings

class Command(BaseCommand):
    help = "download wikipedia dump files needed for initial loading"

    def handle(self, **kwargs):
        if not os.path.isdir(settings.WIKIPEDIA_DUMPS_DIR):
            sys.mkdir(settings.WIKIPEDIA_DUMPS_DIR)

        for lang in settings.WIKIPEDIA_LANGUAGES:
            fetch("http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-page.sql.gz" % (lang, lang))
            fetch("http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-externallinks.sql.gz" % (lang, lang))

def fetch(url):
    filename = os.path.basename(url)
    path = os.path.join(settings.WIKIPEDIA_DUMPS_DIR, filename)
    if not os.path.isfile(path):
        print "saving %s as %s" % (url, path)
        os.system("wget --quiet --output-document %s %s" % (path, url))
