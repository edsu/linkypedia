import re
import urlparse

from django.core.management.base import BaseCommand

from linkypedia import wikipedia


class Command(BaseCommand):
    help = "Load in pages and externallinks dump files from wikipedia"

    def handle(self, pages_filename, links_filename, **options):
        load_pages_dump(pages_filename)
        load_links_dump(links_filename)


def load_pages_dump(filename):
    #(10,0,'AccessibleComputing','',0,1,0,0.33167112649574,'20100727152717',133452289,57)
    pattern = r"\((\d+),(\d+),'(.+?)','.*?',\d+,\d+,\d+,\d\.\d+,'.+?',\d+,\d+\)"
    parse_sql(filename, pattern, process_page_row)


def load_links_dump(filename):
    pattern = r"\((\d+),'(.+?)','(.+?)'\)"
    parse_sql(filename, pattern, process_externallink_row)


def parse_sql(filename, pattern, func):
    fh = open(filename)

    line = ""
    while True:
        buff = fh.read(1024)
        if not buff:
            break

        line += buff

        rows = list(re.finditer(pattern, line))
        for row in rows:
            func(row.groups())

        if len(rows) > 0:
            line = line[rows[-1].end():]

        print line



def process_externallink_row(row):
    page_id, url, reversed_url = row
    parts = urlparse.urlparse(url)
    host = parts.netloc
    print host

    
def process_page_row(row):
    print row[0:4]

