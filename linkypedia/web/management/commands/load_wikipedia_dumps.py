import re
import codecs
import urlparse

from django.db import reset_queries
from django.core.management.base import BaseCommand

from linkypedia import wikipedia
from linkypedia.web import models as m


class Command(BaseCommand):
    help = "Load in pages and externallinks dump files from wikipedia"

    def handle(self, pages_filename, links_filename, **options):
        load_pages_dump(pages_filename)
        load_links_dump(links_filename)


def load_pages_dump(filename): #(10,0,'AccessibleComputing','',0,1,0,0.33167112649574,'20100727152717',133452289,57)
    pattern = r"\((\d+),(\d+),'(.+?)','.*?',\d+,\d+,\d+,\d\.\d+,'.+?',\d+,\d+\)"
    parse_sql(filename, pattern, process_page_row)


def load_links_dump(filename):
    pattern = r"\((\d+),'(.+?)','(.+?)'\)"
    parse_sql(filename, pattern, process_externallink_row)


def parse_sql(filename, pattern, func):
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
                func(row.groups())
            except Exception, e:
                print "uhoh: %s" % e

        if len(rows) > 0:
            line = line[rows[-1].end():]

        # when DEBUG=True we don't want to gobble up all the memory
        count += 1
        if count % 1000 == 0:
            reset_queries()


def process_externallink_row(row):
    page_id, url, reversed_url = row
    parts = urlparse.urlparse(url)
    host = parts.netloc
    tld = host.split('.')[-1]

    try:
        article = m.Article.objects.get(id=page_id)
        link = m.ExternalLink(article=article, url=url, host=host, tld=tld)
        link.clean()
        link.save()
        print "created: %s" % link

    except m.Article.DoesNotExist:
        # this ok since we ignore links from non articles: user pages, etc
        pass


def process_page_row(row):
    # ignore non-article pages
    if row[1] != '0':
        return
    a = m.Article(id=row[0], title=row[2])
    a.save()
    print "created: %s" % a
