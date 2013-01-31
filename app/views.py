#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


from models import *


def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            #TODO: redirect «next»
            return render_to_response('home.html', {}, context_instance=RequestContext(request))
    return render_to_response('login.html', {}, context_instance=RequestContext(request))


@login_required
def films(request):
    c = { 'films': Film.objects.all() }
    return render_to_response('films.html', c, context_instance=RequestContext(request))


@login_required
def dates(request):
    c = { 'dates': Date.objects.all() }
    return render_to_response('dates.html', c, context_instance=RequestContext(request))


@login_required
def votes(request):
    c = { 'votes': Vote.objects.all() }
    return render_to_response('votes.html', c, context_instance=RequestContext(request))
