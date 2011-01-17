import os
import re
import gzip
import codecs

from django.conf import settings
from django.db import reset_queries
from django.core.management.base import BaseCommand

import linkdb
from linkylog import log


class Command(BaseCommand):
    help = "Load in pages and externallinks dump files from wikipedia"

    def handle(self, **options):
        log.info("starting wikipedia dump loading")
        linkdb.init()

        for lang in settings.WIKIPEDIA_LANGUAGES:
            filename = "%swiki-latest-page.sql.gz" % lang
            log.info("loading articles from %s" % filename)
            path = os.path.join(settings.WIKIPEDIA_DUMPS_DIR, filename)
            #load_pages_dump(path, lang)

        linkdb._add_article_primary_key()

        for lang in settings.WIKIPEDIA_LANGUAGES:
            log.info("loading links from %s" % filename)
            filename = "%swiki-latest-externallinks.sql.gz" % lang
            path = os.path.join(settings.WIKIPEDIA_DUMPS_DIR, filename)
            load_links_dump(path, lang)

        linkdb._add_link_indexes()


def load_pages_dump(filename, lang): 
    pattern = r"\((\d+),(\d+),'(.+?)','.*?',\d+,\d+,\d+,\d\.\d+,'.+?',\d+,\d+\)"
    parse_sql(filename, pattern, process_page_row, lang)


def load_links_dump(filename, lang):
    pattern = r"\((\d+),'(.+?)','(.+?)'\)"
    parse_sql(filename, pattern, process_externallink_row, lang)


def process_page_row(row, lang):
    # ignore non-article pages
    if row[1] != '0':
        return
    wp_article_id = row[0]
    title = row[2]
    linkdb.add_article(lang, wp_article_id, title)


def process_externallink_row(row, lang):
    article_id, url, reversed_url = row
    linkdb.add_link(lang, article_id, url)


def parse_sql(filename, pattern, func, lang):
    "Rips columns specified with the regex out of the sql"
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
                count += 1
                func(row.groups(), lang)

                # to keep memory of this process low when DEBUG=True
                if count % 10000 == 0:
                    log.info(count)
                    reset_queries()

                # to keep memory footprint of redis-server from growing too big
                if count % 100000 == 0 and func == process_externallink_row:
                    linkdb._trim_stats()

            except Exception, e:
                print "uhoh: %s: %s w/ %s" % (func, e, row.groups())
                log.fatal("%s %s: w/ %s" % (func, e, row.groups()))

        # don't forget unconsumed bytes, need them for the next match
        if len(rows) > 0:
            line = line[rows[-1].end():]
