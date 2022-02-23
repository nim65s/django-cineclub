from django.urls import path
from django.views.generic import DetailView

from . import views
from .models import Film, Soiree

app_name = "cine"
urlpatterns = [
    path("", views.SoireeListView.as_view(), name="home"),
    path(
        "soiree/<int:pk>",
        DetailView.as_view(queryset=Soiree.objects.a_venir()),
        name="soiree",
    ),
    path(
        "soiree/<int:pk>/delete", views.SoireeDeleteView.as_view(), name="delete_soiree"
    ),
    path("soiree/<int:pk>/<int:dispo>", views.DTWUpdateView.as_view(), name="dtw"),
    path("soiree", views.SoireeCreateView.as_view(), name="ajout_soiree"),
    path("films", views.FilmListView.as_view(), name="films"),
    path("film/ajout", views.FilmCreateView.as_view(), name="ajout_film"),
    path("film/<slug:slug>/maj", views.FilmUpdateView.as_view(), name="maj_film"),
    path("film/<slug:slug>/vu", views.FilmVuView.as_view(), name="film_vu"),
    path("film/<slug:slug>", DetailView.as_view(model=Film), name="film"),
    path("cinephiles", views.CinephileListView.as_view(), name="cinephiles"),
    path("rajquit", views.RajQuitView.as_view(), name="rajquit"),
    path("adress", views.AdressUpdateView.as_view(), name="adress"),
    path("cinenim.ics", views.ics, name="ics"),
]
