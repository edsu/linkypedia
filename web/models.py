from django.db import models as m

class Link(m.Model):
    created = m.DateTimeField(auto_now=True)
    host = m.TextField()
    source = m.TextField()
    target = m.TextField()
