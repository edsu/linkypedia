from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',
    url(r'^$', 'websites', name='websites'),

    url(r'^websites/(?P<website_id>\d+)/$', 'website_summary',
        name='website_summary'),

    url(r'^websites/(?P<website_id>.+)/links/$', 'website_links',
        name='website_links'),

    url(r'^websites/(?P<website_id>.+)/links/(?P<page_num>\d+)/$', 
        'website_links', name='website_links_page'),

    url(r'^websites/(?P<website_id>.+)/categories/$', 'website_categories',
        name='website_categories'),

    url(r'^website/(?P<website_id>.+)/categories/(?P<page_num>\d+)/$',
        'website_categories', name='website_categories_page'),

    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)

