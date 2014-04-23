# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.core.urlresolvers import reverse
from perso.templatetags.perso_extra import url_get

register = template.Library()


@register.simple_tag
def films_url(request, key, value):
    return "%s%s" % (reverse('cine:films'), url_get(request, key, value))
