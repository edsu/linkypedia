from django.core.paginator import Paginator
from django.shortcuts import render_to_response

from linkypedia.web import models as m

def links(request, page_num=1):
    links = m.Link.objects.all()
    paginator = Paginator(links, 100)
    page = paginator.page(int(page_num))
    links = page.object_list
    return render_to_response('links.html', dictionary=locals())
