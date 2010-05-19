from django import template

from linkypedia.rfc3339 import rfc3339

register = template.Library()

@register.filter(name='rfc3339')
def rfc3339_filter(d):
    return rfc3339(d)
