from django.conf.urls.defaults import *
from django.views.static import serve

urlpatterns = patterns(
    'linkypedia.web.views',
    url(r'^$', 'home', name='home'),
    url(r'^status.json$', 'status', name='status'),
    url(r'robots.txt$','robots', name='robots'),
    url(r'host/(?P<host>.+)/$', 'host', name='host'),
    url(r'host/(?P<host>.+)/favicon.ico$', 'host_favicon', name='host_favicon'),
    url(r'article/(?P<wp_lang>.+)/(?P<wp_article_id>.+)/$', 'article', 
        name="article"),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': 'static'}),
)
