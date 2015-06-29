from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, RedirectView

from .models import Film, Soiree
from .views import ICS, AdressUpdateView, CinephileListView, DTWUpdateView, FilmCreateView, FilmListView, FilmUpdateView, FilmVuView, SoireeCreateView, votes, VetoView

urlpatterns = patterns('',
    url(r'^votes$', votes, name='votes'),
    url(r'^veto/(?P<pk>\d+)$', VetoView.as_view(), name='veto'),

    url(r'^$', ListView.as_view(model=Soiree), name='home'),
    url(r'^soiree/(?P<pk>\d+)/(?P<dispo>[ONP])', DTWUpdateView.as_view(), name='dtw'),
    url(r'^soiree$', SoireeCreateView.as_view(), name='ajout_soiree'),

    url(r'^films$', FilmListView.as_view(), name='films'),
    url(r'^film/ajout$', FilmCreateView.as_view(), name='ajout_film'),
    url(r'^film/maj/(?P<slug>[^/]+)$', FilmUpdateView.as_view(), name='maj_film'),
    url(r'^film/vu/(?P<slug>[^/]+)$', FilmVuView.as_view(), name='film_vu'),
    url(r'^film/(?P<slug>[^/]+)$', DetailView.as_view(model=Film), name='film'),
    url(r'^comms/(?P<slug>[^/]+)$', RedirectView.as_view(permanent=True, pattern_name='film')),

    url(r'^cinephiles$', CinephileListView.as_view(), name='cinephiles'),
    url(r'^adress$', AdressUpdateView.as_view(), name='adress'),

    url(r'^cinenim.ics$', ICS.as_view(), name='ics'),
)
