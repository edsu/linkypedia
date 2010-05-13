from django.core.paginator import Paginator
from django.shortcuts import render_to_response

from linkypedia.web import models as m

def hosts(request):
    hosts = m.Host.objects.all().order_by('name')
    return render_to_response('hosts.html', dictionary=locals())

def links(request, host, page_num=1):
    try:
        host = m.Host.objects.get(name=host)
        links = m.Link.objects.filter(host=host)
        paginator = Paginator(links, 100)
        page = paginator.page(int(page_num))
        links = page.object_list
        return render_to_response('links.html', dictionary=locals())
    except m.Host.DoesNotExist:
        return render_to_response('wait.html', dictionary=locals())
