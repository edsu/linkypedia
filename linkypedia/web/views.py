import json

from django.db.models import Count
from django.template import RequestContext
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from linkypedia.rfc3339 import rfc3339
from linkypedia.web import models as m
from linkypedia.paginator import DiggPaginator
from linkypedia.settings import CRAWL_CUTOFF, CACHE_TTL_SECS


@cache_page(CACHE_TTL_SECS)
def home(request):
    return render_to_response('home.html', dictionary=locals(),
            context_instance=RequestContext(request))

def lookup(request):
    url = request.REQUEST.get('url', None)
    results = []
    for link in m.ExternalLink.objects.filter(url=url):
        w = link.article
        result = {
            'url': w.url, 
            'title': w.title, 
            }
        results.append(result)
    return HttpResponse(json.dumps(results, indent=2), mimetype='application/json')

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

def robots(request):
    return render_to_response('robots.txt', mimetype='text/plain')

def about(request):
    return render_to_response('about.html')
