#-*- coding: utf-8 -*-

from datetime import datetime

from pytz import timezone

from cine.models import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

tz = timezone(settings.TIME_ZONE)
tzloc = tz.localize


class Command(BaseCommand):
    args = ''
    help = u'Affiche les gens qui ont pas voté (c’est pas bien ! :P)'

    def handle(self, *args, **options):
        soiree = Soiree.objects.filter(date__gte=tzloc(datetime.now()))[0]
        for film in Film.objects.filter(categorie=soiree.categorie, vu=False):
            for dispo in DispoToWatch.objects.filter(dispo='O', soiree=soiree):
                vote = Vote.objects.get(cinephile=dispo.cinephile, film=film)
                if vote.choix == 9999:
                    print u'%s n’a pas voté pour %s' % (dispo.cinephile, film)
