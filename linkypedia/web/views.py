import os
import re
import json
import time
import urllib
import datetime
import urlparse
import cStringIO

from lxml import etree

import rdflib

from django.db.models import Count, Max
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404

from linkypedia.rfc3339 import rfc3339
from linkypedia.web import models as m
from linkypedia.paginator import DiggPaginator
from linkypedia.settings import CRAWL_CUTOFF, CACHE_TTL_SECS

def about(request):
    return render_to_response('about.html')

@cache_page(CACHE_TTL_SECS)
def websites(request):
    websites = m.Website.objects.all()
    websites = websites.annotate(Count('links'))
    websites = websites.order_by('-links__count')
    host = request.get_host()

    return render_to_response('websites.html', dictionary=locals(),
            context_instance=RequestContext(request))

def websites_feed(request):
    websites = m.Website.objects.all()
    websites = websites.order_by('-created')
    host = request.get_host()

    # figure out the last time the feed changed based on the
    # most recently crawled site
    feed_updated = datetime.datetime.now()
    if websites.count() > 0:
        feed_updated = websites[0].created

    return render_to_response('websites.atom', dictionary=locals(),
            context_instance=RequestContext(request),
            mimetype='application/json; charset=utf-8')

def website_summary(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)
    tab = 'summary'
    title = "website: %s" % website.url
    if website.links.count() == CRAWL_CUTOFF:
        cutoff = CRAWL_CUTOFF
    return render_to_response('website_summary.html', dictionary=locals())

def website_data(request, website_id):
    """stream website link data as tab separated values
    """
    website = get_object_or_404(m.Website, id=website_id)

    def tsv():
        # use a paginator since django/mysql wants to pull the entire
        # results back into memory on the mysql client side 
        paginator = Paginator(website.links.all(), 500)
        page_num = 0
        while page_num < paginator.num_pages:
            page_num += 1
            page = paginator.page(page_num)
            for link in page.object_list:
                row = [link.wikipedia_page.url, link.target]
                yield "\t".join(row) + "\n"

    filename = "linkypedia-" + slugify(website.name) + ".tsv"
    response = HttpResponse(tsv())
    response['Content-Type'] = 'text/tab-separated-values'
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def website_pages(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)

    page_num = request.GET.get('page', 1)
    page_num = int(page_num)

    # make sure we support the order
    order = request.GET.get('order', 'links')
    direction = request.GET.get('direction', 'desc')
    other_direction = 'asc' if direction == 'desc' else 'desc'

    if order == 'update' and direction =='asc':
        sort_order = 'links__created__max'
    elif order == 'update' and direction == 'desc':
        sort_order = '-links__created__max'
    elif order == 'views' and direction == 'desc':
        sort_order = '-views'
    elif order == 'views' and direction == 'asc':
        sort_order = 'views'
    elif order == 'links' and direction == 'asc':
        sort_order = 'links__count'
    else:
        sort_order = '-links__count'

    wikipedia_pages = m.WikipediaPage.objects.filter(links__website=website)
    wikipedia_pages = wikipedia_pages.annotate(Count('links'))
    wikipedia_pages = wikipedia_pages.annotate(Max('links__created'))
    wikipedia_pages = wikipedia_pages.order_by(sort_order)
    wikipedia_pages = wikipedia_pages.distinct()

    paginator = DiggPaginator(wikipedia_pages, 100)
    page = paginator.page(page_num)
    wikipedia_pages = page.object_list

    tab = 'pages'
    tab_summary = "wikipedia pages %s" % website.name 
    title = "website: %s" % website.url
    stats_date = time.strftime("%Y%m")

    if request.GET.get('format') == 'json':
        data = []
        for page in wikipedia_pages:
            data.append({'url': page.url, 
                         'title': page.title,
                         'views': page.views,
                         'links': page.links__count})
        return HttpResponse(json.dumps(data, indent=2),
                            mimetype='application/json')


    return render_to_response('website_pages.html', dictionary=locals())

def website_pages_feed(request, website_id, page_num=1):
    website = get_object_or_404(m.Website, id=website_id)
    wikipedia_pages = m.WikipediaPage.objects.filter(links__website=website)
    wikipedia_pages = wikipedia_pages.annotate(Count('links'))
    wikipedia_pages = wikipedia_pages.annotate(Max('links__created'))
    wikipedia_pages = wikipedia_pages.order_by('-links__created__max')
    wikipedia_pages = wikipedia_pages.distinct()

    feed_updated = datetime.datetime.now()
    if wikipedia_pages.count() > 0:
        feed_updated = wikipedia_pages[0].last_modified

    host = request.get_host()
    paginator = Paginator(wikipedia_pages, 100)
    page = paginator.page(int(page_num))
    wikipedia_pages = page.object_list
    
    return render_to_response('website_pages_feed.atom', 
            mimetype="application/atom+xml", dictionary=locals())

def website_links(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)
    page_num = request.GET.get('page', 1)
    page_num = int(page_num)

    # make sure we support the order
    order = request.GET.get('order', 'pages')
    direction = request.GET.get('direction', 'desc')
    other_direction = 'asc' if direction == 'desc' else 'desc'

    if order == 'target' and direction =='asc':
        sort_order = 'target'
    elif order == 'target' and direction == 'desc':
        sort_order = '-target'
    elif order == 'pages' and direction == 'asc':
        sort_order = 'wikipedia_page__count'
    else:
        sort_order = '-wikipedia_page__count'


    links = m.Link.objects.filter(website=website)
    links = links.values("target")
    links = links.annotate(Count('wikipedia_page'))
    links = links.order_by(sort_order)

    paginator = DiggPaginator(links, 100)
    page = paginator.page(page_num)
    links = page.object_list

    tab = 'links'
    title = "website: %s" % website.url

    return render_to_response('website_links.html', dictionary=locals())


def website_categories(request, website_id, page_num=1):
    website = get_object_or_404(m.Website, id=website_id)
    categories = website.categories().order_by('-pages__count')
    paginator = DiggPaginator(categories, 100)
    page = paginator.page(int(page_num))
    categories = page.object_list
    tab = 'categories'
    tab_summary = "Categories for %s" % website.name 
    title = "website: %s" % website.url
    return render_to_response('website_categories.html', dictionary=locals())

def website_users(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)
    users = m.WikipediaUser.objects.filter(wikipedia_pages__links__website=website)
    users = users.distinct()
    users = users.order_by('username')
    tab = 'users'
    title = "website: %s" % website.url
    return render_to_response('website_users.html', dictionary=locals())

def lookup(request):
    url = request.REQUEST.get('url', None)
    results = []
    for link in m.Link.objects.filter(target=url):
        w = link.wikipedia_page
        result = {
            'url': w.url, 
            'title': w.title, 
            'last_modified': rfc3339(w.last_modified)
            }
        results.append(result)
    return HttpResponse(json.dumps(results, indent=2), mimetype='application/json')

def robots(request):
    return render_to_response('robots.txt', mimetype='text/plain')

def status(request):
    link = m.Link.objects.all().order_by('-created')[0]
    update = {
        'wikipedia_url': link.wikipedia_page.url,
        'wikipedia_page_title': link.wikipedia_page.title,
        'target': link.target,
        'website_name': link.website.name,
        'website_url': link.website.url,
        'created': rfc3339(link.created),
        'linkypedia_url': 'http://' + request.get_host() + reverse("website_summary", args=[link.website.id])
    }

    crawls = m.Crawl.objects.filter(finished=None).order_by('-started')
    if crawls.count() > 0:
        website = crawls[0].website
        crawl = {'name': website.name, 'url': website.url, 
                'link': website.get_absolute_url()}
        update['current_crawl'] = crawl

    return HttpResponse(json.dumps(update, indent=2), mimetype='application/json')

def page(request, page_id):
    wikipedia_page = get_object_or_404(m.WikipediaPage, id=page_id)
    links = m.Link.objects.filter(wikipedia_page=wikipedia_page)
    links = links.order_by('website__name')
    json_url = reverse("page_json", args=(page_id,))
    return render_to_response('page.html', dictionary=locals())

def url(request):
    url = request.GET.get("url")
    if not url:
        return HttpResponseNotFound("you need to supply the url query parameter")

    if re.match('^http:/[^/]', url):
        url = url.replace('http:/', 'http://')
    links = m.Link.objects.filter(target=url)
    links = links.order_by('website__name')
    return render_to_response('url.html', dictionary=locals())

def page_json(request, page_id):
    wikipedia_page = get_object_or_404(m.WikipediaPage, id=page_id)
    t = urllib.quote(wikipedia_page.title.replace(' ', '_'))

    g = rdflib.Graph()
    rdf_url = 'http://dbpedia.org/data/%s' % t
    g.parse(rdf_url)
    dbpedia = rdflib.Namespace('http://dbpedia.org/ontology/')
    foaf = rdflib.Namespace('http://xmlns.com/foaf/0.1/')

    s = rdflib.URIRef('http://dbpedia.org/resource/%s' % t)
    page = {}
    page['dbpedia_url'] = rdf_url
    page['wikipedia_url'] = wikipedia_page.url
    page['abstract'] = abstract(g, s)
    page['thumbnail'] = g.value(s, foaf['depiction'])
    page['thumbnail'] = g.value(s, dbpedia['thumbnail'])
    page['links'] = [l.target for l in wikipedia_page.links.all()]
    return HttpResponse(json.dumps(page, indent=2), mimetype='application/json; charset=utf8')

def abstract(g, s):
    dbpedia = rdflib.Namespace('http://dbpedia.org/ontology/')
    text = None
    for o in g.objects(s, rdflib.RDFS['comment']):
        if type(o) == rdflib.Literal and o.language == 'en':
            text = unicode(o)
    for o in g.objects(s, dbpedia['abstract']):
        if type(o) == rdflib.Literal and o.language == 'en':
            text = unicode(o)
    if text:
        words = text.split(" ")
        if len(words) > 100:
            text = " ".join(words[0:100]) + " ..."
    return text

