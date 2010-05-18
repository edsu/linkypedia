import urllib2
import urlparse

from lxml import etree

from django.db.models import Count
from django.template import RequestContext
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from linkypedia.web import models as m

def websites(request):
    # create the website instance if one was submitted and
    # redirect to the new website view
    new_website_url = request.POST.get('new_website_url', None)
    if new_website_url:
        website = _setup_new_website(new_website_url)
        return HttpResponseRedirect('/')
    
    websites = m.Website.objects.all().order_by('name')
    return render_to_response('websites.html', dictionary=locals(),
            context_instance=RequestContext(request))

def website_summary(request, website_id):
    website = get_object_or_404(m.Website, id=website_id)
    tab = 'summary'
    tab_summary = "Summary Information for %s" % website.name
    title = "website: %s" % website.url
    return render_to_response('website_summary.html', dictionary=locals())

def website_links(request, website_id, page_num=1):
    website = m.Website.objects.get(id=website_id)
    links = m.Link.objects.filter(website=website)
    paginator = Paginator(links, 100)
    page = paginator.page(int(page_num))
    links = page.object_list
    tab = 'links'
    tab_summary = "Links for %s" % website.name 
    title = "website: %s" % website.url
    return render_to_response('website_links.html', dictionary=locals())

def website_categories(request, website_id, page_num=1):
    website = get_object_or_404(m.Website, id=website_id)
    categories = website.categories().order_by('-pages__count')
    paginator = Paginator(categories, 100)
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

    try:
        host = urlparse.urlparse(url).netloc
        parser = etree.HTMLParser()
        doc = etree.parse(urllib2.urlopen(url), parser)
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
