#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from cine.models import *

class Command(BaseCommand):
    args = ''
    help = u'Crée les votes et dispos manquant(e)s'

    def handle(self, *args, **options):
        N = len(Film.objects.all()) + 1
        for cinephile in User.objects.all():
            for film in Film.objects.all():
                try:
                    Vote.objects.get(film=film, cinephile=cinephile)
                except Vote.DoesNotExist:
                    v = Vote()
                    v.choix = N
                    v.film = film
                    v.cinephile = cinephile
                    v.save()
                    self.stdout.write("Nouveau Vote: %s" % v)
            for soiree in Soiree.objects.all():
                try:
                    DispoToWatch.objects.get(soiree=soiree, cinephile=cinephile)
                except DispoToWatch.DoesNotExist:
                    d = DispoToWatch()
                    d.dispo = 'N'
                    d.soiree = soiree
                    d.cinephile = cinephile
                    d.save()
                    self.stdout.write("Nouvelle Dispo: %s" % d)
