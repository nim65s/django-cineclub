# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from cine.models import Soiree, Vote
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Affiche les gens qui ont pas voté (c’est pas bien ! :P)'

    def handle(self, *args, **options):
        dispos = Soiree.objects.a_venir.first().dispotowatch_set.filter(dispo='O').values_list('cinephile', flat=True)
        for vote in Vote.objects.filter(choix=9999, film__vu=False, cinephile__in=dispos):
            print('%s n’a pas voté pour %s' % (vote.cinephile, vote.film))
