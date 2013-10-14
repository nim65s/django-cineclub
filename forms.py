#-*- coding: utf-8 -*-

from django.forms import ModelForm

from .models import Film


class FilmForm(ModelForm):
    class Meta:
        model = Film
        exclude = ('respo', 'slug', 'vu', 'duree', 'imdb_poster_url', 'imdb_poster')
