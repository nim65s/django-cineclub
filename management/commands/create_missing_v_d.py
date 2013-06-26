#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from cine.models import *

class Command(BaseCommand):
    args = ''
    help = u'Crée les votes et dispos manquant(e)s et supprime ceux des non-cinéphiles'

    def handle(self, *args, **options):
        N = len(Film.objects.all()) + 1
        groupe_cine = Group.objects.get_or_create(name='cine')[0]
        for cinephile in User.objects.all():
            if groupe_cine in cinephile.groups.all():
                for film in Film.objects.all():
                    try:
                        Vote.objects.get(film=film, cinephile=cinephile)
                    except Vote.DoesNotExist:
                        v = Vote()
                        v.choix = N
                        v.film = film
                        v.cinephile = cinephile
                        v.save()
                        self.stdout.write(u"Nouveau Vote: %s" % v)
                for soiree in Soiree.objects.all():
                    try:
                        DispoToWatch.objects.get(soiree=soiree, cinephile=cinephile)
                    except DispoToWatch.DoesNotExist:
                        d = DispoToWatch()
                        d.dispo = 'N'
                        d.soiree = soiree
                        d.cinephile = cinephile
                        d.save()
                        self.stdout.write(u"Nouvelle Dispo: %s" % d)
            else:
                for dtw in cinephile.dispotowatch_set.all():
                    self.stdout.write(u"suppression de la dtw: %s" % dtw)
                    dtw.delete()
                for vote in cinephile.vote_set.all():
                    self.stdout.write(u"suppression du vote: %s" % vote)
                    vote.delete()
