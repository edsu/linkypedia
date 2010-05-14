from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',
    url(r'^$', 'websites', name='websites'),
    url(r'^websites/(?P<website_id>.+)/(?P<page_num>\d+)/$', 'website',
        name='website_page'),
    url(r'^websites/(?P<website_id>.+)/$', 'website', name='website'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

