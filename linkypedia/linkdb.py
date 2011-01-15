"""
This module provides an abstraction for working with the links db.
The thought being that the internals could be swapped out as need
be if necessary...and also to accomodate different data stores under
the hood: relational db for some things, redis for other things, etc
"""

import re
import urlparse

import redis
from django.db import connection

from linkylog import log


cursor = connection.cursor()
stats = redis.Redis()


def add_article(wp_lang, wp_article_id, title):
    """adds an article to the link database using the wikipedia language
    that the link came from, the wikipedia article id, and the title of the
    wikipedia article.
    """
    article_id = make_article_id(wp_lang, wp_article_id)
    sql = """ 
        INSERT INTO wikipedia_article (id, title)
        VALUES (%s, %s)
        """
    return cursor.execute(sql, [article_id, title])


def add_link(wp_lang, wp_article_id, url):
    article_id = make_article_id(wp_lang, wp_article_id)
    article_title = get_article_title(article_id)

    # don't add links for things we don't know about already
    if not article_title:
        return

    sql = """
        INSERT INTO wikipedia_link (article_id, url, created)
        VALUES (%s, %s, now());
        """
    cursor.execute(sql, [article_id, url])
    _update_stats(article_id, url)


def get_article_title(article_id):
    sql = "SELECT title FROM wikipedia_article WHERE ID = %s"
    cursor.execute(sql, [article_id])
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def make_article_id(wp_lang, wp_article_id):
    "makes a linkypedia article id from the wikipedia instance and article id"
    return "%s:%010i" % (wp_lang, int(wp_article_id))


def init():
    "resets the link database!"
    log.info("initializing link database!")
    log.info("creating mysql link tables")
    cursor.execute("DROP TABLE IF EXISTS wikipedia_article")
    cursor.execute("""
        CREATE TABLE wikipedia_article (
            id char(15),
            title varbinary(255)
        ) ENGINE=myisam CHARACTER SET utf8
        """)
    cursor.execute("DROP TABLE IF EXISTS wikipedia_link")
    cursor.execute("""
        CREATE TABLE wikipedia_link (
            article_id char(15),
            url blob,
            created datetime
        ) ENGINE=myisam CHARACTER SET utf8
        """)
    log.info("resetting redis")
    stats.flushall()
    log.info("finished initializing link database")


def _update_stats(article_id, url):
        # which wikipedia?
        wikipedia = article_id.split(':')[0]

        # what hostname?
        u = urlparse.urlparse(url)
        host = u.netloc
        if not host: # TODO: ignore if numeric IP?
            return

        # what top level domain
        tld = host.split(".")[-1]
        tld = re.sub(r':\d+$', '', tld) # strip off port numbers

        # increment relevant stuff in redis
        stats.zincrby('hosts', host, 1)
        stats.zincrby('tlds', tld, 1)
        stats.zincrby('wikipedia', wikipedia, 1)
        stats.zincrby('hosts:%s' % tld, host, 1)
        stats.incr('links')
        return True


# the following functions definitely fall into the leaky abstraction 
# category but that can't be helped for now ... ideas welcome :)

def _add_article_primary_key():
    log.info("adding wikipedia_article primary key")
    sql = "ALTER TABLE wikipedia_article ADD PRIMARY KEY(id)"
    cursor.execute(sql)
    log.info("finished adding wikipedia_article primary key")


def _add_link_indexes():
    log.info("adding wikipedia_link_url index")
    sql = """
        ALTER TABLE wikipedia_link
        ADD INDEX wikipedia_link_url (url(30))
        """
    cursor.execute(sql)
    log.info("finished adding wikipedia_link_url index")
    log.info("adding wikpedia_link_article_id index")
    sql = """
        ALTER TABLE wikipedia_link
        ADD INDEX wikipedia_link_article_id (article_id)
        """
    log.info("finished adding wikpedia_link_article_id index")


def _trim_stats():
    """
    removes the long tail of hosts & tlds that have only appeared once
    which should lower the redis memory footprint
    """
    hosts_removed = stats.zremrangebyscore('hosts', 0, 1)
    tlds_removed = stats.zremrangebyscore('tlds', 0, 1)
    for k in stats.keys('hosts:*'):
        stats.zremrangebyscore(k, 0, 1)
    log.info("trimmed %s hosts and %s tlds" % (hosts_removed, tlds_removed)
    return hosts_removed, tlds_removed
