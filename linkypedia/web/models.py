import re
import logging
import datetime
import urlparse

from django.db import models as m

class Foo(m.Model):
    bar = m.IntegerField()
