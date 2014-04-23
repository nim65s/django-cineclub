# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from .models import DispoToWatch, tzloc


@dajaxice_register
def dispo(request, date, dispo):
    cache.delete('films')
    dajax = Dajax()
    dtw = get_object_or_404(DispoToWatch, cinephile=request.user, soiree__date=tzloc(datetime.strptime(date, '%Y-%m-%d_%H-%M')))
    dtw.dispo = dispo
    dtw.save()
    dajax.assign('#presents-%s' % date, 'innerHTML', dtw.soiree.presents())
    dajax.assign('#pas_surs-%s' % date, 'innerHTML', dtw.soiree.pas_surs())
    return dajax.json()
