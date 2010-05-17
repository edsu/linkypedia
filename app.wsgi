import os, sys

home = os.path.abspath(os.curdir)

sys.path.append(home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'linkypedia.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
