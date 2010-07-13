from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',

    url(r'^$', 'websites', name='websites'),
    url(r'^(?P<format>feed)/$', 'websites', name='websites_feed'),

    url(r'^websites/(?P<website_id>\d+)/$', 'website_summary',
        name='website_summary'),

    url(r'^websites/(?P<website_id>\d+)/pages/$', 'website_pages',
        name='website_pages'),

    url(r'^websites/(?P<website_id>\d+)/pages/(?P<page_num>\d+)/$', 
        'website_pages', name='website_pages_page'),

    url(r'^websites/(?P<website_id>\d+)/links/(?P<page_id>\d+)/$',
        'website_page_links', name='website_page_links'),

    url(r'^websites/(?P<website_id>\d+)/pages/feed/$', 'website_pages_feed',
        name='website_pages_feed'),

    url(r'^websites/(?P<website_id>\d+)/pages/feed/(?P<page_num>\d+)/$', 
        'website_pages_feed', name='website_pages_feed_page'),

    url(r'^websites/(?P<website_id>\d+)/categories/$', 'website_categories',
        name='website_categories'),

    url(r'^website/(?P<website_id>\d+)/categories/(?P<page_num>\d+)/$',
        'website_categories', name='website_categories_page'),

    url(r'^about/$', 'about', name='about'),

    url(r'^lookup/$', 'lookup', name='lookup'),

    url(r'robots.txt','robots', name='robots'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

