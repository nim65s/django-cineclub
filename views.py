#-*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext

from models import *

from datetime import date


def logout_view(request):
    logout(request)
    return previsions(request)


def previsions(request):
    c = {}
    films = []
    N = len(Film.objects.filter(vu=False)) * len(User.objects.all()) + 1
    for soiree in Soiree.objects.order_by('date').filter(date__gte=date.today()):
        if DispoToWatch.objects.filter(dispo='O', soiree=soiree):
            films.append((soiree,[]))
            for film in Film.objects.filter(categorie=soiree.categorie, vu=False):
                if film.respo.dispo_set.filter(soiree=soiree, dispo='O'):
                    score = N
                    for dispo in DispoToWatch.objects.filter(dispo='O', soiree=soiree):
                        vote = Vote.objects.get(cinephile=dispo.cinephile, film=film)
                        score -= vote.choix
                        if vote.plusse:
                            score += 1
                    films[-1][1].append((score, film))
            films[-1][1].sort()
            films[-1][1].reverse()
    c['films'] = films
    return render_to_response('home.html', c, context_instance=RequestContext(request))


@login_required
def films(request):
    c = {
            'films': Film.objects.filter(vu=False),
            'films_vu': Film.objects.filter(vu=True),
            'edit': True
            }
    new = True
    if request.method == 'POST':
        form = FilmForm(request.POST)
        if 'slug' in form.data:
            film = Film.objects.get(slug=form.data['slug'])
            if film.respo == request.user:
                form = FilmForm(request.POST, instance=film)
                new = False
            else:
                c['error'] = u"Vous n’êtes pas respo pour ce film…"
        if form.is_valid():
            form.instance.respo = request.user
            form.save()
            form = FilmForm()
            if new:
                c['success'] = u'Film ajouté :D'
            else:
                c['success'] = u'Film modifié'
            c['edit'] = False
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
        if 'respo' in request.GET:
            respo = User.objects.get(username=request.GET['respo'])
            c['films'] = Film.objects.filter(respo=respo,)
    c['filmform'] = form
    return render_to_response('films.html', c, context_instance=RequestContext(request))


@login_required
def comms(request, slug):
    film = get_object_or_404(Film, slug=slug)
    edit = False # Not yet implemented
    if request.method == 'POST':
        form = CommForm(request.POST)
        if form.is_valid():
            form.instance.posteur = request.user
            form.instance.film = film
            form.save()
    c = {
            'film': film,
            'comms': film.commentaire_set.all().order_by('date'),
            'form': CommForm(),
            'edit': edit,
            }
    return render_to_response('comms.html', c, context_instance=RequestContext(request))

@login_required
def dispos(request):
    dispos = DispoToWatch.objects.filter(cinephile=request.user,soiree__date__gte=date.today()).order_by('soiree__date')
    c = { 'dispos': dispos }
    if request.method == 'POST':
        for dispo in dispos:
            strdate = dispo.soiree.date.strftime('%Y-%m-%d')
            if strdate in request.POST:
                dispo.dispo = request.POST[strdate]
                dispo.save()
            else:
                print strdate, 'not in POST:', request.POST
    return render_to_response('dispos.html', c, context_instance=RequestContext(request))


@login_required
def votes(request):
    if request.method == 'POST':
        ordre = request.POST['ordre'].split(',')[:-1]
        if ordre:
            i = 1
            for vote in ordre:
                film = Film.objects.get(slug=vote)
                v = Vote.objects.get(film=film, cinephile=request.user)
                v.choix = i
                v.save()
                i += 1
    c = { 'votes': Vote.objects.filter(cinephile=request.user, film__vu=False).order_by("choix") }
    return render_to_response('votes.html', c, context_instance=RequestContext(request))


@login_required
def cinephiles(request):
    c = { 'cinephiles': User.objects.all() }
    return render_to_response('cinephiles.html', c, context_instance=RequestContext(request))


@login_required
def profil(request):
    form = UserForm(instance=request.user)
    c = {}
    if request.method == 'POST':
        if 'old_username' in request.POST:
            form = UserForm(request.POST, instance=request.user)
            if form.is_valid():
                updated_user = User.objects.get(username=request.POST['old_username'])
                if updated_user == request.user:
                    form.save()
                    c['success'] = u"Profil mis à jour"
                else:
                    c['error'] = u"NAMÉHO, c’est pas ton profil ça !"
        else:
            if request.user.check_password(request.POST['oldpw']):
                if request.POST['newpw'] == request.POST['verpw']:
                    request.user.set_password(request.POST['newpw'])
                    request.user.save()
                    c['success'] = u"Mot de passe mis à jour"
                else:
                    c['error'] = u"Les deux mots de passe entrés ne concordent pas"
            else:
                c['error'] = u"Mauvais «Ancien mot de passe»"
    c['form'] = form
    return render_to_response('profil.html', c, context_instance=RequestContext(request))


def faq(request):
    return render_to_response('faq.html', {}, context_instance=RequestContext(request))


def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))
