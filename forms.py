# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms import ModelForm

from .models import Film


class FilmForm(ModelForm):
    class Meta:
        model = Film
        exclude = ('respo', 'slug', 'vu', 'duree', 'imdb_poster', 'imdb')
