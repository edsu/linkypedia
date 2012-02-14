import anydbm
import urllib
import datetime

from django.core.paginator import Paginator
from django.core.management.base import BaseCommand

from linkypedia.web import models

import requests


class Command(BaseCommand):

    def handle(self, **options):
        # create lookup of page titles and their ids
        page_ids = anydbm.open("stats.db", "n")
        paginator = Paginator(models.WikipediaPage.objects.all(), 100)
        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            for wp in page.object_list:
                title = wp.url.split("/")[-1].encode('utf-8')
                page_ids[title] = str(wp.id)

        # start time defaults to the latest stats seen or the beginning of 2012
        start = models.WikipediaPage.objects.all().order_by('-views_last')[0].views_last
        if not start:
            start = datetime.datetime(2012, 1, 1, 0)

        now = datetime.datetime.now()
        while start < now:
            url = "http://dumps.wikimedia.org/other/pagecounts-raw/%(year)i/%(year)i-%(month)02i/pagecounts-%(year)i%(month)02i%(day)02i-%(hour)02i0000.gz" % {"year": start.year, "month": start.month, "day": start.day, "hour": start.hour}
            r = requests.get(url)
            r.headers['content-encoding'] = 'gzip'
            for line in r.iter_lines():
                cols = line.split(" ")
                if cols[0] == "en":
                    page = urllib.unquote(cols[1])
                    if page_ids.has_key(page):
                        p = models.WikipediaPage.objects.get(id=int(page_ids[page]))
                        if p.views_last == None or start > p.views_last:
                            p.views += int(cols[2])
                            p.views_last = start
                            p.save()
                            print p.title, p.views, p.views_last
            start += datetime.timedelta(hours=1)
