# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cine.models import DispoToWatch
from django import template
from django.core.urlresolvers import reverse
from perso.templatetags.perso_extra import url_get

register = template.Library()


@register.simple_tag
def films_url(request, key, value):
    return "%s%s" % (reverse('cine:films'), url_get(request, key, value))


@register.simple_tag
def dispo_buttons(user, soiree):
    if not user.groups.filter(name='cine').exists():
        return ''
    dispo = DispoToWatch.objects.get(soiree=soiree, cinephile=user).dispo
    return """
    <div class="btn-group" data-toggle="buttons">
        <label class="btn %(O)s btn-success" onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'O'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-O">Présent</label>
        <label class="btn %(P)s btn-danger " onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'P'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-P">Absent</label>
        <label class="btn %(N)s btn-primary" onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'N'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-N">Ne sais pas</label>
    </div>
    """ % {
            'date': soiree.date.strftime('%Y-%m-%d_%H-%M'),
            'O': 'active' if dispo == 'O' else '',
            'P': 'active' if dispo == 'P' else '',
            'N': 'active' if dispo == 'N' else '',
            }
