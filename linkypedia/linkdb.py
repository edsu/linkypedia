"""
This module provides an abstraction for working with the links db.
The thought being that the internals could be swapped out as need
be if necessary...and also to accomodate different data stores under
the hood: relational db for some things, redis for other things, etc
"""

import re
import json
import urlparse

import redis
from django.db import connection

from linkylog import log


stats = redis.Redis()

def article_links(wp_lang, wp_article_id):
    article_id = make_article_id(wp_lang, wp_article_id)
    sql = """
        SELECT url, created 
        FROM wikipedia_link
        WHERE article_id = %s
        """
    cursor = connection.cursor()
    cursor.execute(sql, [article_id])
    return cursor.fetchall()


def article_links_by_host(hostname, limit=25, offset=0):
    sql = """
        SELECT article_id, title, url, created
        FROM wikipedia_link, wikipedia_article
        WHERE wikipedia_link.host = %s
        AND wikipedia_link.article_id = wikipedia_article.id
        ORDER BY created
        LIMIT %s 
        OFFSET %s
        """
    cursor = connection.cursor()
    cursor.execute(sql, [hostname, limit, offset])
    return cursor.fetchall()


def host_stats(tld=None, limit=50, offset=0):
    key = 'hosts:%s' % tld if tld else 'hosts'
    hosts = stats.zrevrange(key, offset, offset+limit-1, True)
    return [(h[0], int(h[1])) for h in hosts]


def tld_stats(limit=50, offset=0):
    tlds = stats.zrevrange('tlds', offset, offset+limit-1, True)
    return [(t[0], int(t[1])) for t in tlds]


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
    cursor = connection.cursor()
    return cursor.execute(sql, [article_id, title])


def add_link(wp_lang, wp_article_id, url):
    """add a link to the link database, using the wikipedia language, 
    the wikipedia article id and the target url.
    """
    # don't add links for things we don't know about already
    article_title = get_article_title(wp_lang, wp_article_id)
    if not article_title:
        return 0

    # if the url doesn't parse don't bother storing it
    host = _hostname(url)
    if not host:
        return 0

    article_id = make_article_id(wp_lang, wp_article_id)
    sql = """
        INSERT INTO wikipedia_link (article_id, url, host, created)
        VALUES (%s, %s, %s, now());
        """
    cursor = connection.cursor()
    added = cursor.execute(sql, [article_id, url, host])
    _update_stats(article_id, url)

    # keep track of the last link added for real-time status display
    last_link = {
            'url': url, 
            'lang': wp_lang, 
            'article_id': wp_article_id, 
            'title': article_title}
    stats['last_link'] = json.dumps(last_link)

    return added


def delete_link(wp_lang, wp_article_id, url):
    article_id = make_article_id(wp_lang, wp_article_id)
    sql = """
        DELETE FROM wikipedia_link
        WHERE article_id = %s
        AND url = %s
        """
    cursor = connection.cursor()
    deleted = cursor.execute(sql, [article_id, url])
    _update_stats(article_id, url)
    return deleted


def get_article_title(wp_lang, wp_article_id):
    article_id = make_article_id(wp_lang, wp_article_id)
    sql = "SELECT title FROM wikipedia_article WHERE ID = %s"
    cursor = connection.cursor()
    cursor.execute(sql, [article_id])
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def update_article_links(wp_lang, wp_article_id, urls):
    """"takes a list of urls that are the current set of external links
    for the given Wikipedia article, and updates the links appropriately.
    """
    # create two sets of urls to do the logic
    current_urls = set(urls)
    old_urls = set([l[0] for l in article_links(wp_lang, wp_article_id)])

    # create any new links
    created =  0
    for url in current_urls - old_urls:
        created += add_link(wp_lang, wp_article_id, url)

    # delete any links that have been removed
    deleted = 0
    for url in old_urls - current_urls:
        deleted += delete_link(wp_lang, wp_article_id, url)

    return created, deleted


def make_article_id(wp_lang, wp_article_id):
    "makes a linkypedia article id from the wikipedia instance and article id"
    return "%s:%010i" % (wp_lang, int(wp_article_id))


def init(reset_stats=True):
    "initializes the link database!"
    cursor = connection.cursor()
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
            host char(100),
            created datetime
        ) ENGINE=myisam CHARACTER SET utf8
        """)
    if reset_stats:
        log.info("resetting redis")
        stats.flushall()
    log.info("finished initializing link database")


def _update_stats(article_id, url):
    # which wikipedia?
    wikipedia = article_id.split(':')[0]

    host = _hostname(url)
    tld = host.split(".")[-1]

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
    cursor = connection.cursor()
    cursor.execute(sql)
    log.info("finished adding wikipedia_article primary key")


def _add_link_indexes():
    log.info("adding wikipedia_link_url index")
    sql = """
        ALTER TABLE wikipedia_link
        ADD INDEX wikipedia_link_url (url(30))
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    log.info("finished adding wikipedia_link_url index")
    log.info("adding wikpedia_link_article_id index")
    sql = """
        ALTER TABLE wikipedia_link
        ADD INDEX wikipedia_link_article_id (article_id)
        """
    cursor.execute(sql)
    log.info("finished adding wikpedia_link_article_id index")
    log.info("adding wikipedia_link_host index")
    sql = """
        ALTER TABLE wikipedia_link
        ADD INDEX wikipedia_link_host (host)
        """
    cursor.execute(sql)
    log.info("finished adding wikipedia_link_host index")
    log.info("finished add wikipedia_link indexes")


def _trim_stats():
    """
    removes the long tail of hosts & tlds that have only appeared once
    which should lower the redis memory footprint
    """
    hosts_removed = stats.zremrangebyscore('hosts', 0, 1)
    tlds_removed = stats.zremrangebyscore('tlds', 0, 1)
    for k in stats.keys('hosts:*'):
        stats.zremrangebyscore(k, 0, 1)
    log.info("trimmed %s hosts and %s tlds" % (hosts_removed, tlds_removed))
    return hosts_removed, tlds_removed


def _hostname(url):
    u = urlparse.urlparse(url)
    if u:
        host = u.netloc
        host = re.sub(r':\d+$', '', host)
        return host
    return None
