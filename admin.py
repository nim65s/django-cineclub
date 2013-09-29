#-*- coding: utf-8 -*-

from django.contrib.admin import site, ModelAdmin
from models import *


class SoireeAdmin(ModelAdmin):
    exclude = ('favoris', 'categorie')

site.register(Film)
site.register(Vote)
site.register(Soiree, SoireeAdmin)
site.register(DispoToWatch)
site.register(Commentaire)
