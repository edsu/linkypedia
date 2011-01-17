import json
import urllib

from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from linkypedia import linkdb
from linkypedia.rfc3339 import rfc3339
from linkypedia.web import models as m
from linkypedia.paginator import DiggPaginator
from linkypedia.settings import CRAWL_CUTOFF, CACHE_TTL_SECS


@cache_page(CACHE_TTL_SECS)
def home(request):
    host_stats = linkdb.host_stats()
    return render_to_response('home.html', dictionary=locals(),
            context_instance=RequestContext(request))

def status(request):
    link = m.ExternalLink.objects.all().order_by('-id')[0]
    update = {
        'wikipedia_url': link.article.url,
        'wikipedia_page_title': link.article.title,
        'target': link.url,
        'host': link.host,
        'created': rfc3339(link.created),
    }

    return HttpResponse(json.dumps(update, indent=2), 
                        mimetype='application/json')

@cache_page(60*60)
def host_favicon(request, host):
    r = urllib.urlopen('http://%s/favicon.ico' % host)
    return HttpResponse(r.read(), mimetype=r.headers["content-type"])

def robots(request):
    return render_to_response('robots.txt', mimetype='text/plain')

def about(request):
    return render_to_response('about.html')
