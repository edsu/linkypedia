"""
This module contains functions for extracting information from wikipedia and 
persisting facts to the database.
"""

import re
import logging
import datetime

from django.db import reset_queries

from linkypedia.web import models as m
from linkypedia import wikipedia
from linkypedia.settings import CRAWL_CUTOFF
from linkypedia.rfc3339 import rfc3339_parse

def crawl(website):
    """
    Execute a crawl, but only if it hasn't been started already.
    """
    logging.info("starting crawl for %s" % website.url)

    crawl = m.Crawl(website=website)
    crawl.started = datetime.datetime.now()
    crawl.save()

    # look at all wikipedia pages that reference a particular website
    count = 0
    for source, target in wikipedia.links(website.url):

        # get the wikipedia page
        page, created = m.WikipediaPage.new_from_wikipedia(url=source)
        if created: 
            logging.info("created wikipedia page for %s" % source)

        # create the link
        link, created = m.Link.objects.get_or_create(
                website=website, 
                wikipedia_page=page,
                target=target)

        if created:
            logging.info("created link: %s -> %s" % (source, target))

        link.last_checked = datetime.datetime.now()
        link.save()
        reset_queries()
        count += 1

        if CRAWL_CUTOFF and count > CRAWL_CUTOFF:
            logging.info("stopping crawl at crawl cutoff: %s" % CRAWL_CUTOFF)
            break

    crawl.finished = datetime.datetime.now()
    crawl.save()

    logging.info("finished crawl for %s" % crawl.website.url)
    return crawl

def load_users():
    """
    Trawls through WikipediPages looking for usernames, then looks
    up the user information at wikipedia and persists to WikipediaUser models
    """
    logging.info("starting to look for new user information")
    created_count, updated_count = 0, 0
    for u in _user_info():
        user, created = _create_user(u)
        if created:
            created_count += 1
        else:
            updated_count += 1
    return created_count, updated_count

def _user_info():
    # TODO: any need to make these configurable?
    wikipedia_chunk_size = 20
    pages = []

    for page in _user_pages():
        pages.append(page)

        if len(pages) > wikipedia_chunk_size:
            for user_info in _wikipedia_users(pages):
                yield user_info
            pages = []

    # any remaining ones that haven't been checked?
    for user_info in _wikipedia_users(pages):
        yield user_info

def _user_pages():
    # instead of pulling back all pages (django pulls into memory)
    # we look for a chunk at a time
    q = m.WikipediaPage.objects.filter(title__startswith='User').distinct()
    db_chunk_size = 1000
    start = 0
    total = q.count()

    while start < total:
        for p in q[start : start + db_chunk_size]:
            if p.associated_username():
                yield p
        start += db_chunk_size

def _wikipedia_users(user_pages):
    username_page_map = dict([[p.associated_username(), p] for p in user_pages])
    usernames = username_page_map.keys()
    for info in wikipedia.users(usernames):
        info['page'] = username_page_map[info['name']]
        yield info

def _create_user(user_info):
    user, created = m.WikipediaUser.objects.get_or_create(username=user_info['name'])
    if created:
        logging.info("created user %s" % user.username)

    if user_info.get('registration', None) != None:
        user.registration = rfc3339_parse(user_info['registration'])
    user.gender = user_info.get('gender', None)
    user.edit_count = user_info.get('editcount', 0)

    if user_info['page'] not in user.wikipedia_pages.all():
        user.wikipedia_pages.add(user_info['page'])

    if user_info.get('emailable', None) == '':
        user.emailable = True

    for group_name in user_info.get('groups', []):
        group, created = m.WikipediaGroup.objects.get_or_create(name=group_name)
        if created:
            logging.info("created group %s" % group.name)

        user.groups.add(group)

    user.save()
    return user, created
