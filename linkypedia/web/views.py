import os
import re
import json
import urllib2

from django.conf import settings
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from pygooglechart import PieChart3D

from linkypedia import linkdb
from linkypedia.web import models as m
from linkypedia.settings import CACHE_TTL_SECS


@cache_page(CACHE_TTL_SECS)
def home(request):
    host_stats = linkdb.host_stats(limit=50)
    return render_to_response('home.html', dictionary=locals(),
            context_instance=RequestContext(request))

@cache_page(CACHE_TTL_SECS)
def host(request, host):
    links = linkdb.article_links_by_host(host)
    return render_to_response('host.html', dictionary=locals(),
            context_instance=RequestContext(request))

@cache_page(CACHE_TTL_SECS)
def article(request, wp_lang, wp_article_id):
    links = linkdb.article_links(wp_lang, wp_article_id)
    article_title = linkdb.get_article_title(wp_lang, wp_article_id)
    return render_to_response('article.html', dictionary=locals(),
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
    req = urllib2.Request("http://%s/favicon.ico" % host, headers={"User-Agent": "ozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13"})
    res = urllib2.urlopen(req)
    if res.code == 200:
        ico = res.read()
    if (ico and re.match(r"[a-z]{5}", ico)) or not ico:
        ico = open(os.path.join(settings.MEDIA_ROOT, "question.ico")).read()
    return HttpResponse(ico, mimetype="image/x-icon")

def robots(request):
    return render_to_response('robots.txt', mimetype='text/plain')

def about(request):
    return render_to_response('about.html')
