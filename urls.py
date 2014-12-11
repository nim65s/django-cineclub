from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import *

urlpatterns = patterns('',
    url(r'^votes$', votes, name='votes'),

    url(r'^$', SoireeListView.as_view(), name='home'),
    url(r'^soiree$', SoireeCreateView.as_view(), name='ajout_soiree'),

    url(r'^films$', FilmListView.as_view(), name='films'),
    url(r'^film/ajout$', FilmCreateView.as_view(), name='ajout_film'),
    url(r'^film/maj/(?P<slug>[^/]+)$', FilmUpdateView.as_view(), name='maj_film'),
    url(r'^film/vu/(?P<slug>[^/]+)$', FilmVuView.as_view(), name='film_vu'),
    url(r'^film/(?P<slug>[^/]+)$', FilmDetailView.as_view(), name='film'),
    url(r'^comms/(?P<slug>[^/]+)$', LegacyCommsRedirectView.as_view()),

    url(r'^dispos$', DispoListView.as_view(), name='dispos'),
    url(r'^cinephiles$', CinephileListView.as_view(), name='cinephiles'),

    url(r'^cinenim.ics$', ics, name='ics'),
)
