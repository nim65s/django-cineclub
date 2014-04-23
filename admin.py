# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin import ModelAdmin, site
from models import *


class SoireeAdmin(ModelAdmin):
    exclude = ('favoris', 'categorie')

site.register(Film)
site.register(Vote)
site.register(Soiree, SoireeAdmin)
site.register(DispoToWatch)
