#-*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.base import RedirectView

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from .forms import FilmForm
from .models import get_cinephiles, Film, Vote, Soiree, DispoToWatch

CACHE_LIMIT = 7 * 24 * 3600  # Une semaine…


def check_votes(request):
    if request.user in get_cinephiles() and Vote.objects.filter(choix=9999, cinephile=request.user, film__vu=False).exists():
        messages.warning(request, mark_safe(u'<a href="%s">Tu n’as pas classé certains films !</a>' % reverse('cine:votes')))


def home(request):
    check_votes(request)
    c = {}
    films = cache.get('films')
    if films is None:
        films = []
        N = Film.objects.filter(vu=False).count() * User.objects.filter(groups__name='cine').count() + 1
        for soiree in Soiree.a_venir.all():
            if DispoToWatch.objects.filter(dispo='O', soiree=soiree):
                films.append((soiree, [], []))
                for film in Film.objects.filter(categorie=soiree.categorie, vu=False):
                    score = N
                    for dispo in DispoToWatch.objects.filter(dispo='O', soiree=soiree):
                        vote = Vote.objects.get(cinephile=dispo.cinephile, film=film)
                        score -= vote.choix
                        if vote.plusse:
                            score += 1
                    if film.respo.dispotowatch_set.filter(soiree=soiree, dispo='O'):
                        films[-1][1].append((score, film))
                    else:
                        films[-1][2].append((score, film))
                films[-1][1].sort()
                films[-1][1].reverse()
                films[-1][2].sort()
                films[-1][2].reverse()
                if len(films[-1][1]) > 0:
                    soiree.favoris = films[-1][1][0][1]
                    soiree.save()
        cache.set('films', films, CACHE_LIMIT)
    c['films'] = films
    c['nombre_films_c'] = Film.objects.filter(vu=False, categorie='C').count()
    c['nombre_films_d'] = Film.objects.filter(vu=False, categorie='D').count()
    c['nombre_films_vus'] = Film.objects.filter(vu=True).count()
    return render(request, 'cine/home.html', c)


@login_required
def votes(request):
    if request.method == 'POST':
        cache.delete('films')
        ordre = request.POST['ordre'].split(',')[:-1]
        if ordre:
            i = 1
            for vote in ordre:
                film = Film.objects.get(slug=vote)
                v = Vote.objects.get(film=film, cinephile=request.user)
                v.choix = i
                v.save()
                i += 1
    c = {'votes': Vote.objects.filter(cinephile=request.user, film__vu=False)}
    return render(request, 'cine/votes.html', c)


def ics(request):
    return render(request, 'cine/cinenim.ics', {'soirees': Soiree.a_venir.all()}, content_type="text/calendar; charset=UTF-8")


class CheckVotesMixin(object):
    def get(self, request, *args, **kwargs):
        if request.user in get_cinephiles() and Vote.objects.filter(choix=9999, cinephile=request.user, film__vu=False).exists():
            messages.warning(request, mark_safe(u'<a href="%s">Tu n’as pas classé certains films !</a>' % reverse('cine:votes')))
        return super(CheckVotesMixin, self).get(request, *args, **kwargs)


class FilmActionMixin(CheckVotesMixin):
    model = Film
    form_class = FilmForm
    # TODO 1.6: fields à la place de form_class

    def form_valid(self, form):
        messages.info(self.request, u"Film %s" % self.action)
        return super(FilmActionMixin, self).form_valid(form)


class FiltreCategorieMixin(object):
    def get_queryset(self):
        queryset = super(FiltreCategorieMixin, self).get_queryset()
        cat = self.request.GET.get("cat")
        if cat:
            return queryset.filter(categorie=cat)
        return queryset


class FilmCreateView(GroupRequiredMixin, FilmActionMixin, CreateView):
    group_required = u'cine'
    action = u"Créé"

    def form_valid(self, form):
        cache.delete('films')
        form.instance.respo = self.request.user
        return super(FilmCreateView, self).form_valid(form)


class FilmUpdateView(GroupRequiredMixin, FilmActionMixin, UpdateView):
    group_required = u'cine'
    action = u"modifié"

    def form_valid(self, form):
        if form.instance.respo == self.request.user or self.request.user.is_superuser():
            return super(FilmUpdateView, self).form_valid(form)
        messages.error(self.request, u'Vous n’avez pas le droit de modifier ce film')
        return redirect('cine:films')


class FilmDetailView(CheckVotesMixin, DetailView):
    model = Film


class FilmListView(CheckVotesMixin, FiltreCategorieMixin, ListView):
    queryset = Film.objects.filter(vu=False)


class FilmVuListView(CheckVotesMixin, FiltreCategorieMixin, ListView):
    queryset = Film.objects.filter(vu=True)


class FilmDeListView(CheckVotesMixin, FiltreCategorieMixin, ListView):
    def get_queryset(self):
        return Film.objects.filter(respo__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super(FilmDeListView, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return context


class FilmVuView(SuperuserRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        cache.delete('films')
        film = get_object_or_404(Film, slug=kwargs['slug'])
        film.vu = True
        film.save()
        return reverse('cine:films')


class CinephileListView(GroupRequiredMixin, CheckVotesMixin, ListView):
    group_required = u'cine'
    queryset = User.objects.filter(groups__name='cine')
    template_name = 'cine/cinephile_list.html'


class DispoListView(GroupRequiredMixin, CheckVotesMixin, ListView):
    group_required = u'cine'

    def get_queryset(self):
        return DispoToWatch.objects.filter(cinephile=self.request.user, soiree__in=Soiree.a_venir.all())
