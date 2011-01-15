import re
import logging
import urlparse

import redis
import MySQLdb
import MySQLdb.cursors

from django.conf import settings
from django.core.management.base import BaseCommand


logging.basicConfig(
        filename="linkypedia.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

log = logging.getLogger()


class Command(BaseCommand):
    help = "builds redis db of top hosts and tlds"

    def handle(self, **options):
        r = redis.Redis()

        for url, article_id in links():
            # TODO: extract as a function for calling from other places
            # TODO: also add an inverse

            # which wikipedia?
            wikipedia = article_id.split(':')[0]

            # what hostname?
            u = urlparse.urlparse(url)
            host = u.netloc
            if not host: # TODO: ignore if numeric IP?
                continue

            # what top level domain
            tld = host.split(".")[-1]
            tld = re.sub(r':\d+$', '', tld) # strip off port numbers

            # increment relevant stuff in redis
            r.zincrby('hosts', host, 1)
            r.zincrby('tlds', tld, 1)
            r.zincrby('wikipedia', wikipedia, 1)
            r.zincrby('hosts:%s' % tld, host, 1)
            r.incrby('links', 1)

            # TODO: ever 100k or so trim the long tail to save on memory
            # TODO: extract as a function as well
            # r.zremrangebyscore('hosts', 0, 2)
            # r.zremrangebyscore('tlds', 0, 2)


def links():
    db = settings.DATABASES['default']
    conn = MySQLdb.connect(db=db['NAME'],
                           host=db['HOST'],
                           user=db['USER'],
                           passwd=db['PASSWORD'],
                           cursorclass=MySQLdb.cursors.SSCursor)
    curs = conn.cursor()
    curs.execute("SELECT url, article_id FROM wikipedia_link")

    for row in curs:
        yield row
