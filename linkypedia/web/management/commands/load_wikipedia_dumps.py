import os
import re
import gzip
import codecs
import urlparse

from django.conf import settings
from django.db import reset_queries
from django.core.management.base import BaseCommand

from linkypedia.web import models as m


class Command(BaseCommand):
    help = "Load in pages and externallinks dump files from wikipedia"

    def handle(self, **options):
        for lang in settings.WIKIPEDIA_LANGUAGES:
            
            # load pages
            filename = "%swiki-latest-page.sql.gz" % lang
            path = os.path.join(settings.WIKIPEDIA_DUMPS_DIR, filename)
            load_pages_dump(path, lang)

            # load links
            filename = "%swiki-latest-externallinks.sql.gz" % lang
            path = os.path.join(settings.WIKIPEDIA_DUMPS_DIR, filename)
            load_links_dump(path, lang)


def load_pages_dump(filename, lang): 
    pattern = r"\((\d+),(\d+),'(.+?)','.*?',\d+,\d+,\d+,\d\.\d+,'.+?',\d+,\d+\)"
    parse_sql(filename, pattern, process_page_row, lang)


def load_links_dump(filename, lang):
    pattern = r"\((\d+),'(.+?)','(.+?)'\)"
    parse_sql(filename, pattern, process_externallink_row, lang)


def parse_sql(filename, pattern, func, lang):
    if filename.endswith('.gz'):
        fh = codecs.EncodedFile(gzip.open(filename), data_encoding="utf-8")
    else:
        fh = codecs.open(filename, encoding="utf-8")

    line = ""
    count = 0
    while True:
        buff = fh.read(1024)
        if not buff:
            break

        line += buff

        rows = list(re.finditer(pattern, line))
        for row in rows:
            try:
                func(row.groups(), lang)
            except Exception, e:
                print "uhoh: %s" % e

        if len(rows) > 0:
            line = line[rows[-1].end():]

        # when DEBUG=True we don't want to gobble up all the memory
        count += 1
        if count % 1000 == 0:
            reset_queries()


def process_page_row(row, lang):
    # ignore non-article pages
    if row[1] != '0':
        return
    # article id has language pre-prended to it
    article_id = m.article_id(row[0], lang)
    a = m.Article(id=article_id, title=row[2])
    a.save()
    print "created: %s" % a.id


def process_externallink_row(row, lang):
    page_id, url, reversed_url = row

    # page id gets a language prefix
    article_id = m.article_id(page_id, lang)

    try:
        article = m.Article.objects.get(id=article_id)
        link = m.ExternalLink(article=article, url=url)
        link.save()
        print "created: %s" % link

    except m.Article.DoesNotExist:
        # this ok since we ignore links from non articles: user pages, etc
        pass
