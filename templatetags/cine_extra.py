#-*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, key, value):
    get = request.GET.copy()
    get[key] = value
    return get.urlencode()
