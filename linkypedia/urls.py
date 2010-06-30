from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',

    url(r'^$', 'websites', name='websites'),
    url(r'(?P<format>feed)/$', 'websites', name='websites_feed'),

    url(r'^websites/(?P<website_id>\d+)/$', 'website_summary',
        name='website_summary'),

    url(r'^websites/(?P<website_id>.+)/pages/$', 'website_pages',
        name='website_pages'),

    url(r'^websites/(?P<website_id>.+)/pages/(?P<page_num>\d+)/$', 
        'website_pages', name='website_pages_page'),

    url(r'^websites/(?P<website_id>.+)/categories/$', 'website_categories',
        name='website_categories'),

    url(r'^website/(?P<website_id>.+)/categories/(?P<page_num>\d+)/$',
        'website_categories', name='website_categories_page'),

    url(r'^about/$', 'about', name='about'),

    url(r'robots.txt','robots', name='robots'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

