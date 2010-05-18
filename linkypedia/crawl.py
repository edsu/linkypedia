import logging
import datetime

from django.db import reset_queries

from linkypedia.web import models as m
from linkypedia import wikipedia

def crawl(website):
    """
    Execute a crawl, but only if it hasn't been started already.
    """
    logging.info("starting crawl for %s" % website.url)

    crawl = m.Crawl(website=website)
    crawl.started = datetime.datetime.now()
    crawl.save()

    # look at all wikipedia pages that reference a particular website
    for source, target in wikipedia.links(website.url):

        # get the wikipedia page
        page, created = m.WikipediaPage.objects.get_or_create(url=source)
        if created: 
            logging.info("created wikipedia page for %s" % source)
            page.populate_from_wikipedia()

        # create the link
        link, created = m.Link.objects.get_or_create(
                website=website, 
                wikipedia_page=page,
                target=target)

        if created:
            logging.info("created link: %s -> %s" % (source, target))
        else:
            logging.info("updated link: %s -> %s" % (source, target))

        link.last_checked = datetime.datetime.now()
        link.save()
        reset_queries()

    crawl.finished = datetime.datetime.now()
    crawl.save()

    logging.info("finished crawl for %s" % crawl.website.url)
    return crawl
