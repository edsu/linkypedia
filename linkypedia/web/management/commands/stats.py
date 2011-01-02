import re
import pipes
import logging
import urlparse
import cStringIO

from django.core.paginator import Paginator
from django.db import connection
from django.core.management.base import BaseCommand

from linkypedia.web import models as m


logging.basicConfig(
        filename="linkypedia.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

log = logging.getLogger()


class Command(BaseCommand):
    help = "calculates and persists the top hosts and tlds from link data"

    def handle(self, **options):
        # create pipelines to get sorted lists of hosts and tlds 
        # persisted to files
        hosts = counter("/tmp/1")
        tlds = counter("/tmp/2")

        # iterate through all the urls from which we get the host and tld
        # and send them off to the appropriate pipeline
        for url in urls():
            u = urlparse.urlparse(url)
            host = u.netloc

            if not host:
                continue
            hosts.write(host.encode("utf-8")+"\n")

            tld = host.split(".")[-1]
            tld = re.sub(r':\d+$', '', tld) # strip off port numbers
            tlds.write(tld.encode("utf-8")+"\n")

        # close out the pipelines
        hosts.close()
        tlds.close()


def counter(filename):
    """Returns a filehandle to write data through a 
    sort | uniq -c | sort -rn pipeline
    """
    t = pipes.Template()
    t.append("sort", "--")
    t.append("uniq -c", "--")
    t.append("sort -rn", "--")
    out = cStringIO.StringIO()
    f = t.open(filename, "w")
    return f

def urls():
    """a generator that returns all the wikipedia external link urls
    """
    
    # what follows is a bit weird looking, but using the id index to iterate 
    # through all the externallink urls runs faster than using limit and 
    # offset when the offset gets big
    cursor = connection.cursor()

    # get the highest external link id
    cursor.execute("SELECT MAX(id) FROM web_externallink")
    max_id = cursor.fetchone()[0]

    limit = 1000
    i = 0
    while i < max_id: 
        q = """
            SELECT url
            FROM web_externallink
            WHERE id > %s
            AND id <= %s 
            """ % (i, i+limit)
        cursor.execute(q)
        for row in cursor.fetchall():
            yield row[0]
        i += limit
