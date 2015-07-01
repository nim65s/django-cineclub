# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cine.models import Soiree
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Update les favoris des soirées à venir'

    def handle(self, *args, **options):
        for soiree in Soiree.objets.a_venir.all():
            soiree.update_favori()
