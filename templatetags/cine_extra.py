#-*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def films_url(request, key, value):
    get = request.GET.copy()
    get[key] = value
    return "%s?%s" % (reverse('cine:films'), get.urlencode())
