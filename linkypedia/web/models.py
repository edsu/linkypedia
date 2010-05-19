import re
import logging
import datetime
import urlparse

from django.db import models as m
from django.db.models import Count

from linkypedia import wikipedia

class WikipediaCategory(m.Model):
    title = m.CharField(primary_key=True, max_length=255)

    def __unicode__(self):
        return self.title

class WikipediaPage(m.Model):
    url = m.CharField(max_length=500)
    title = m.TextField()
    created = m.DateTimeField(null=True)
    categories = m.ManyToManyField(WikipediaCategory, related_name='pages')

    def populate_from_wikipedia(self, force=False):
        if not force and self.title:
            return
        title_escaped = wikipedia.url_to_title(self.url)
        info = wikipedia.info(title_escaped)
        self.title = info['title']
        for cat in wikipedia.categories(self.title):
            title = cat['title'].lstrip('Category:')
            category, created = WikipediaCategory.objects.get_or_create(title=title)
            logging.info("adding category %s to wikipedia page %s" %
                    (category.title, self.title))
            self.categories.add(category)
        self.save()

class Link(m.Model):
    created = m.DateTimeField(auto_now=True)
    wikipedia_page = m.ForeignKey('WikipediaPage', related_name='links')
    target = m.TextField()
    website = m.ForeignKey('Website', related_name='links')

class Website(m.Model):
    url = m.TextField()
    name = m.TextField()
    favicon_url = m.TextField()
    created = m.DateTimeField(auto_now=True)

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

    def categories(self):
        return WikipediaCategory.objects.filter(pages__links__website=self).distinct().annotate(Count('pages'))

    def wikipedia_pages(self):
        return WikipediaPage.objects.filter(links__website=self).distinct()

class Crawl(m.Model):
    started = m.DateTimeField(null=True)
    finished = m.DateTimeField(null=True)
    website = m.ForeignKey('Website', related_name='crawls')

    class Meta:
        ordering = ['-started', '-finished']
