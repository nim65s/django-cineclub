#-*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import get_object_or_404

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from cine.models import *

from datetime import datetime


@dajaxice_register
def dispo(request, date, dispo):
    print 'test dispo pour le %s : %s' % (date, dispo)
    dajax = Dajax()
    dtw = get_object_or_404(DispoToWatch, cinephile=request.user, soiree__date=datetime.strptime(date, '%Y-%m-%d_%H-%M'))
    if dispo in 'OPN':
        dtw.dispo = dispo
    else:
        messages.error(request, u"Euh la dispo «%s» n’est pas dans OPN…" % dispo)
    dtw.save()
    dajax.assign('#presents-%s' % date, 'innerHTML', dtw.soiree.presents())
    print u"#presents-%s: %s" % (date, dtw.soiree.presents())
    dajax.assign('#pas_surs-%s' % date, 'innerHTML', dtw.soiree.pas_surs())
    return dajax.json()
