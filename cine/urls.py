from django.urls import path
from django.views.generic import DetailView

from . import views
from .models import Film, Soiree

app_name = 'cine'
urlpatterns = [
    path(r'', views.SoireeListView.as_view(), name='home'),
    path(r'soiree/<int:pk>', DetailView.as_view(queryset=Soiree.objects.a_venir()), name='soiree'),
    path(r'soiree/<int:pk>/delete', views.SoireeDeleteView.as_view(), name='delete_soiree'),
    path(r'soiree/<int:pk>/<int:dispo>', views.DTWUpdateView.as_view(), name='dtw'),
    path(r'soiree', views.SoireeCreateView.as_view(), name='ajout_soiree'),

    path(r'films', views.FilmListView.as_view(), name='films'),
    path(r'film/ajout', views.FilmCreateView.as_view(), name='ajout_film'),
    path(r'film/maj/<str:slug>', views.FilmUpdateView.as_view(), name='maj_film'),
    path(r'film/vu/<str:slug>', views.FilmVuView.as_view(), name='film_vu'),
    path(r'film/<str:slug>', DetailView.as_view(model=Film), name='film'),

    path(r'cinephiles', views.CinephileListView.as_view(), name='cinephiles'),
    path(r'rajquit', views.RajQuitView.as_view(), name='rajquit'),
    path(r'adress', views.AdressUpdateView.as_view(), name='adress'),
]
