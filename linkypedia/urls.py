from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',

    url(r'^$', 'websites', name='websites'),
    url(r'^feed/$', 'websites_feed', name='websites_feed'),

    url(r'^websites/(?P<website_id>\d+)/$', 'website_summary',
        name='website_summary'),

    url(r'^websites/(?P<website_id>\d+)/data/$', 'website_data',
        name='website_data'),

    url(r'^websites/(?P<website_id>\d+)/pages/$', 'website_pages',
        name='website_pages'),

    url(r'^websites/(?P<website_id>\d+)/pages/feed/$', 'website_pages_feed',
        name='website_pages_feed'),

    url(r'^websites/(?P<website_id>\d+)/pages/feed/(?P<page_num>\d+)/$', 
        'website_pages_feed', name='website_pages_feed_page'),

    url(r'^websites/(?P<website_id>\d+)/links/$', 'website_links',
        name='website_links'),

    url(r'^websites/(?P<website_id>\d+)/categories/$', 'website_categories',
        name='website_categories'),

    url(r'^websites/(?P<website_id>\d+)/categories/(?P<page_num>\d+)/$',
        'website_categories', name='website_categories_page'),

    url(r'^websites/(?P<website_id>\d+)/users/$', 'website_users', 
        name='website_users'),
        
    url(r'^page/(?P<page_id>\d+)/$', 'page', name='page'),
    url(r'^page/(?P<page_id>\d+)\.json$', 'page_json', name='page_json'),

    url(r'^url/(?P<url>.+)$', 'url', name='url'),
    
    url(r'^about/$', 'about', name='about'),

    url(r'^lookup/$', 'lookup', name='lookup'),
    url(r'^status.json$', 'status', name='status'),

    url(r'robots.txt','robots', name='robots'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

