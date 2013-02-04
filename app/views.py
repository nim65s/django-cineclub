#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from models import *

import datetime


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
    return previsions(request)


def logout_view(request):
    logout(request)
    return previsions(request)


def previsions(request):
    films = {}
    N = len(Film.objects.all()) * len(User.objects.all()) + 1
    for date in Date.objects.all():
        if Dispo.objects.filter(dispo='O', date=date):
            films[date] = []
            for film in Film.objects.filter(categorie=date.categorie):
                score = N
                for dispo in Dispo.objects.filter(dispo='O', date=date):
                    vote = Vote.objects.get(personne=dispo.personne, film=film)
                    score -= vote.choix
                    if vote.plusse:
                        score += 1
                films[date].append((score, film))
            films[date].sort()
            films[date].reverse()
    c = { 'films': films }
    return render_to_response('home.html', c, context_instance=RequestContext(request))


@login_required
def films(request):
    c = {
            'films': Film.objects.all(),
            'edit': True
            }
    if request.method == 'POST':
        form = FilmForm(request.POST)
        if 'slug' in form.data:
            film = Film.objects.get(slug=form.data['slug'])
            #if film.respo == request.user: TODO
            form = FilmForm(request.POST, instance=film)
        if form.is_valid():
            form.instance.respo = request.user
            form.save()
            c['success'] = u'Film ajouté avec succès :D'
            c['edit'] = false
        else:
            c['error'] = u'Le formulaire n’est pas valide.'
    else:
        if 'edit' in request.GET:
            film = Film.objects.get(slug=request.GET['edit'])
            c['slug'] = film.slug
            form = FilmForm(instance=film)
        else:
            form = FilmForm()
            c['edit'] = False
    c['filmform'] = form
    return render_to_response('films.html', c, context_instance=RequestContext(request))


@login_required
def dispos(request):
    dispos = Dispo.objects.filter(personne=request.user)
    c = { 'dispos': dispos }
    if request.method == 'POST':
        for dispo in dispos:
            dispo.dispo = request.POST[dispo.date.date.strftime('%Y-%m-%d')]
            dispo.save()
    return render_to_response('dispos.html', c, context_instance=RequestContext(request))


@login_required
def votes(request):
    if request.method == 'POST':
        ordre = request.POST['ordre'].split(',')[:-1]
        if ordre:
            i = 1
            for vote in ordre:
                film = Film.objects.get(slug=vote)
                v = Vote.objects.get(film=film, personne=request.user)
                v.choix = i
                v.save()
                i += 1
    c = { 'votes': Vote.objects.filter(personne=request.user).order_by("choix") }
    return render_to_response('votes.html', c, context_instance=RequestContext(request))
