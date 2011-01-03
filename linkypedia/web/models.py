import re
import logging
import datetime
import urlparse

from django.db import models as m
from django.db.models import Count

from linkypedia.rfc3339 import rfc3339_parse
from linkypedia.wikipedia import api


class Website(m.Model):
    url = m.TextField()
    name = m.TextField()
    favicon_url = m.TextField()
    created = m.DateTimeField(auto_now_add=True)
    added_by = m.CharField(max_length=255)

    @m.permalink
    def get_absolute_url(self):
        return ('website_summary', (), {'website_id': str(self.id)})

    def last_checked(self):
        last_crawl = self.last_crawl()
        if last_crawl:
            return last_crawl.finished
        else:
            return None

    def last_crawl(self):
        if self.crawls.filter(finished__isnull=False).count() > 0:
            return self.crawls.all()[0]
        return None

    def __unicode__(self):
        return "%s <%s> (%s)" % (self.name, self.url, self.id)


class Crawl(m.Model):
    started = m.DateTimeField(null=True)
    finished = m.DateTimeField(null=True)
    website = m.ForeignKey('Website', related_name='crawls')

    class Meta:
        ordering = ['-started', '-finished']


class Article(m.Model):
    id = m.CharField(max_length=12, primary_key=True)
    title = m.CharField(max_length=255, null=False)

    @property
    def url(self):
        return "http://%s.wikipedia.org/wiki/%s" % (self.language, self.title)

    def clean(self):
        if len(self.title) > 255:
            self.title = self.title[0:255]

    def update_links(self, urls):
        """"takes a list of urls that are the current set of external links
        for the given Wikipedia article, and updates the ExternaLinks
        appropriately.
        """
        # create two sets of urls to do the logic
        current_urls = set(urls)
        old_urls = set([l.url for l in self.links.all()])

        created = deleted = 0

        # create any new links
        for url in current_urls - old_urls:
            l, c = ExternalLink.objects.get_or_create(article=self, url=url)
            if c:
                created += 1

        # delete any links that have been removed
        for url in old_urls - current_urls:
            try:
                # sometimes the same url can appear twice in the same article
                # but we flatten these
                for l in ExternalLink.objects.filter(article=self, url=url):
                    l.delete()
                    deleted += 1
            except ExternalLink.DoesNotExist:
                # might not be in there, but that's ok since we want to delete
                pass

        return created, deleted

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.id)


class ExternalLink(m.Model):
    article = m.ForeignKey(Article, related_name='links')
    url = m.TextField(null=False)
    created = m.DateTimeField(auto_now_add=True, null=False)

    def __unicode__(self):
        return u"%s -> %s" % (self.article.id, self.url)


class Host(m.Model):
    name = m.CharField(max_length=255, primary_key=True)
    tld = m.CharField(max_length=100, db_index=True)
    urls = m.IntegerField()
    lang = m.CharField(max_length=2)


class TLD(m.Model):
    name = m.CharField(max_length=25, primary_key=True)
    urls = m.IntegerField()
