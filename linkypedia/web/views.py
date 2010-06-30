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

from linkypedia.web import models as m
from linkypedia.paginator import DiggPaginator
from linkypedia.wikipedia import _fetch
from linkypedia.settings import CRAWL_CUTOFF

def about(request):
    return render_to_response('about.html')

def websites(request, format='html'):
    # create the website instance if one was submitted and
    # redirect to the new website view
    new_website_url = request.POST.get('new_website_url', None)
    if new_website_url:
        website = _setup_new_website(new_website_url)
        return HttpResponseRedirect(website.get_absolute_url())
    
    websites = m.Website.objects.all()
    websites = websites.annotate(Count('links'))
    websites = websites.order_by('-links__count')

    if format == 'feed':
        template = 'websites.atom'
        mimetype = 'applicaton/atom+xml; charset=utf-8'
        # figure out the last time the feed changed based on the
        # most recently crawled site
        now = datetime.datetime.now()
        for website in websites:
            if website.last_checked():
                now = website.last_checked()
                break
    else:
        template = 'websites.html'
        mimetype = 'text/html; charset=utf-8'

    return render_to_response(template, dictionary=locals(),
            context_instance=RequestContext(request),
            mimetype=mimetype)

def website_summary(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)
    tab = 'summary'
    tab_summary = "Summary Information for %s" % website.name
    title = "website: %s" % website.url
    if website.links.count() == CRAWL_CUTOFF:
        cutoff = CRAWL_CUTOFF
    return render_to_response('website_summary.html', dictionary=locals())

def website_pages(request, website_id, page_num=1):
    website = m.Website.objects.get(id=website_id)

    wikipedia_pages = m.WikipediaPage.objects.filter(links__website=website)
    wikipedia_pages = wikipedia_pages.annotate(Count('links'))
    wikipedia_pages = wikipedia_pages.order_by('-links__count')
    wikipedia_pages = wikipedia_pages.distinct()

    paginator = DiggPaginator(wikipedia_pages, 100)
    page = paginator.page(int(page_num))
    wikipedia_pages = page.object_list

    tab = 'pages'
    tab_summary = "wikipedia pages %s" % website.name 
    title = "website: %s" % website.url

    return render_to_response('website_pages.html', dictionary=locals())

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

def robots(request):
    return render_to_response('robots.txt', mimetype='text/plain')
