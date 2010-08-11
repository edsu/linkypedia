import json
import urllib2
import datetime
import urlparse
import cStringIO

from lxml import etree

from django.db.models import Count
from django.template import RequestContext
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page

from linkypedia.web import models as m
from linkypedia.rfc3339 import rfc3339
from linkypedia.paginator import DiggPaginator
from linkypedia.wikipedia import _fetch
from linkypedia.settings import CRAWL_CUTOFF, CACHE_TTL_SECS

def about(request):
    return render_to_response('about.html')

@cache_page(CACHE_TTL_SECS)
def websites(request):
    # create the website instance if one was submitted and
    # redirect to the new website view
    new_website_url = request.POST.get('new_website_url', None)
    if new_website_url:
        website = _setup_new_website(new_website_url)
        return HttpResponseRedirect(website.get_absolute_url())
    
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
    tab_summary = "Summary Information for %s" % website.name
    title = "website: %s" % website.url
    if website.links.count() == CRAWL_CUTOFF:
        cutoff = CRAWL_CUTOFF
    return render_to_response('website_summary.html', dictionary=locals())

def website_pages(request, website_id):
    website = m.Website.objects.get(id=website_id)

    page_num = request.GET.get('page', 1)
    page_num = int(page_num)

    # make sure we support the order
    order = request.GET.get('order', 'links')
    direction = request.GET.get('direction', 'desc')
    other_direction = 'asc' if direction == 'desc' else 'desc'

    if order == 'update' and direction =='asc':
        sort_order = 'last_modified'
    elif order == 'update' and direction == 'desc':
        sort_order = '-last_modified'
    elif order == 'links' and direction == 'asc':
        sort_order = 'links__count'
    else:
        sort_order = '-links__count'

    wikipedia_pages = m.WikipediaPage.objects.filter(links__website=website)
    wikipedia_pages = wikipedia_pages.annotate(Count('links'))
    wikipedia_pages = wikipedia_pages.order_by(sort_order)
    wikipedia_pages = wikipedia_pages.distinct()

    paginator = DiggPaginator(wikipedia_pages, 100)
    page = paginator.page(page_num)
    wikipedia_pages = page.object_list

    tab = 'pages'
    tab_summary = "wikipedia pages %s" % website.name 
    title = "website: %s" % website.url

    return render_to_response('website_pages.html', dictionary=locals())

def website_page_links(request, website_id, page_id):
    website = m.Website.objects.get(id=website_id)
    wikipedia_page = m.WikipediaPage.objects.get(id=page_id)
    links = m.Link.objects.filter(wikipedia_page=wikipedia_page,
            website=website)

    return render_to_response('website_page_links.html', dictionary=locals())


def website_pages_feed(request, website_id, page_num=1):
    website = m.Website.objects.get(id=website_id)
    wikipedia_pages = m.WikipediaPage.objects.filter(links__website=website)
    wikipedia_pages = wikipedia_pages.annotate(Count('links'))
    wikipedia_pages = wikipedia_pages.order_by('-last_modified')
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

def _setup_new_website(url):
    websites = m.Website.objects.filter(url=url)
    if websites.count() > 0:
        return websites[0]

    website = None
    try:
        if not url.startswith('http://'):
            url = "http://" + url
        host = urlparse.urlparse(url).netloc
        parser = etree.HTMLParser()
        html = cStringIO.StringIO(_fetch(url))
        doc = etree.parse(html, parser)
        title = doc.xpath('/html/head/title')
        if len(title) > 0:
            name = title[0].text
            if ' - ' in name:
                name = name.split(' - ')[0]
        else:
            name = host
        website = m.Website.objects.create(url=url, name=name)

        # try to get the favicon
        favicon_url = 'http://%s/favicon.ico' % host
        urllib2.urlopen(favicon_url)
        website.favicon_url = favicon_url
        website.save()

    except urllib2.HTTPError, e:
        # can't get URL
        pass

    except ValueError, e:
        # bad URL
        pass

    return website

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
    }

    crawls = m.Crawl.objects.filter(finished=None).order_by('-started')
    if crawls.count() > 0:
        website = crawls[0].website
        crawl = {'name': website.name, 'url': website.url, 
                'link': website.get_absolute_url()}
        update['current_crawl'] = crawl

    return HttpResponse(json.dumps(update, indent=2), mimetype='application/json')
