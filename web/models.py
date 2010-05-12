from django.db import models as m

class Link(m.Model):
    created = m.DateTimeField(auto_now=True)
    source = m.TextField()
    target = m.TextField()
    host = m.ForeignKey('Host', related_name='links')

class Host(m.Model):
    name = m.TextField(primary_key=True)
    created = m.DateTimeField(auto_now=True)

class Crawl(m.Model):
    host = m.ForeignKey('Host', related_name='crawls')
    created = m.DateTimeField(auto_now=True)
