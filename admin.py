# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin import ModelAdmin, site
from models import Adress, DispoToWatch, Film, Soiree, Vote


class SoireeAdmin(ModelAdmin):
    exclude = ('favoris',)

site.register(Adress)
site.register(Film)
site.register(Vote)
site.register(Soiree, SoireeAdmin)
site.register(DispoToWatch)
