#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
    for date in Date.objects.filter(date__gte=datetime.date.today()):
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
    c = { 'films': Film.objects.all() }
    print request.user
    return render_to_response('films.html', c, context_instance=RequestContext(request))


@login_required
def dates(request):
    c = { 'dates': Date.objects.filter(date__gte=datetime.date.today()) }
    return render_to_response('dates.html', c, context_instance=RequestContext(request))


@login_required
def votes(request):
    c = { 'votes': Vote.objects.filter(personne=request.user).order_by("choix") }
    return render_to_response('votes.html', c, context_instance=RequestContext(request))


@login_required
def voter(request):
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
    return votes(request)
