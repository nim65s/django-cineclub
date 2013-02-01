#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from models import *


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
    for date in Date.objects.all():
        films[date] = {}
        for film in Film.objects.filter(categorie=date.categorie):
            films[date][film] = 0
            for dispo in Dispo.objects.filter(dispo='O', date=date):
                vote = Vote.objects.get(personne=dispo.personne, film=film)
                films[date][film] -= vote.choix
                if vote.plusse:
                    films[date][film] += 1
    c = { 'films': films }
    return render_to_response('home.html', c, context_instance=RequestContext(request))


@login_required
def films(request):
    c = { 'films': Film.objects.all() }
    print request.user
    return render_to_response('films.html', c, context_instance=RequestContext(request))


@login_required
def dates(request):
    c = { 'dates': Date.objects.all() }
    return render_to_response('dates.html', c, context_instance=RequestContext(request))


@login_required
def votes(request):
    c = { 'votes': Vote.objects.all() }
    return render_to_response('votes.html', c, context_instance=RequestContext(request))
