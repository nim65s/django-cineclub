from django.conf.urls import url
from django.views.generic import DetailView, ListView

from .models import Film, Soiree
from .views import (ICS, AdressUpdateView, CinephileListView, DTWUpdateView, FilmCreateView,
                    FilmListView, FilmUpdateView, FilmVuView, RajQuitView, SoireeCreateView,
                    VetoView, VotesView)

A_VENIR = Soiree.objects.a_venir()

app_name = 'cine'
urlpatterns = [
        url(r'^votes$', VotesView.as_view(), name='votes'),
        url(r'^veto/(?P<pk>\d+)$', VetoView.as_view(), name='veto'),

        url(r'^$', ListView.as_view(queryset=A_VENIR), name='home'),
        url(r'^soiree/(?P<pk>\d+)$', DetailView.as_view(queryset=A_VENIR), name='soiree'),
        url(r'^soiree/(?P<pk>\d+)/(?P<dispo>[01])$', DTWUpdateView.as_view(), name='dtw'),
        url(r'^soiree$', SoireeCreateView.as_view(), name='ajout_soiree'),

        url(r'^films$', FilmListView.as_view(), name='films'),
        url(r'^film/ajout$', FilmCreateView.as_view(), name='ajout_film'),
        url(r'^film/maj/(?P<slug>[^/]+)$', FilmUpdateView.as_view(), name='maj_film'),
        url(r'^film/vu/(?P<slug>[^/]+)$', FilmVuView.as_view(), name='film_vu'),
        url(r'^film/(?P<slug>[^/]+)$', DetailView.as_view(model=Film), name='film'),

        url(r'^cinephiles$', CinephileListView.as_view(), name='cinephiles'),
        url(r'^rajquit$', RajQuitView.as_view(), name='rajquit'),
        url(r'^adress$', AdressUpdateView.as_view(), name='adress'),

        url(r'^cinenim.ics$', ICS.as_view(), name='ics'),
        ]
