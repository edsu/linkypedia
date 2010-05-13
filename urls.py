from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',
    url(r'^$', 'hosts', name='hosts'),
    url(r'^(?P<host>.+)/(?P<page_num>\d+)/$', 'links', name='links_page'),
    url(r'^(?P<host>.+)/$', 'links', name='links'),

    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

