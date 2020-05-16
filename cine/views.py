from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import RedirectView
from icalendar import Calendar, Event

from .forms import SoireeForm
from .models import Cinephile, Film, Soiree


class CinephileRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if Cinephile.objects.filter(user=self.request.user, actif=True).exists():
            return True
        messages.error(self.request, 'Vous ne faites pas partie du cinéclub… Parlez-en à Nim :)')
        return False


def ics(request):
    cal = Calendar()
    domain = get_current_site(request).domain
    cal.add('prodid', '-//cinenim//saurel.me//')
    cal.add('version', '2.0')
    cal.add('summary', 'CinéNim')
    cal.add('x-wr-calname', f'CinéNim {domain}')
    cal.add('x-wr-timezone', settings.TIME_ZONE)
    cal.add('calscale', 'GREGORIAN')

    for soiree in Soiree.objects.all():
        event = Event()
        event.add('uid', f'cinenim{soiree.id}@{domain}')
        event.add('dtstart', soiree.moment)
        event.add('dtend', soiree.moment + timedelta(hours=2))
        event.add('dtstamp', soiree.updated)
        if soiree.favoris:
            event.add('summary', soiree.favoris)
            event.add('description', soiree.favoris.description)
        else:
            event.add('summary', 'CinéNim')
        if soiree.hote is not None:
            event.add('organizer', f'CN={soiree.hote}:mailto:{soiree.hote.email}')
            event.add('location', soiree.hote.cinephile.adresse)
        cal.add_component(event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = 'attachement; filename=cinenim.ics'
    return response


class FilmActionMixin(CinephileRequiredMixin):
    model = Film
    fields = ('name', 'description', 'annee_sortie', 'titre_vo', 'realisateur', 'allocine',
              'duree', 'imdb_poster_url', 'imdb_id')

    def form_valid(self, form):
        messages.info(self.request, f'Film {self.action}')
        return super(FilmActionMixin, self).form_valid(form)


class FilmCreateView(FilmActionMixin, CreateView):
    action = 'créé'

    def form_valid(self, form):
        form.instance.respo = self.request.user
        Cinephile.objects.filter(actif=True).update(should_vote=True)
        return super().form_valid(form)

    def get_initial(self):
        return Film.get_imdb_dict(self.request.GET.get('imdb_id'))


class FilmUpdateView(FilmActionMixin, UpdateView):
    action = 'modifié'

    def form_valid(self, form):
        if form.instance.respo == self.request.user or self.request.user.is_superuser:
            return super().form_valid(form)
        raise PermissionDenied


class FilmListView(ListView):
    model = Film


class FilmVuView(UserPassesTestMixin, RedirectView):
    def test_func(self):
        return self.request.user.is_superuser

    def get_redirect_url(self, *args, **kwargs):
        film = get_object_or_404(Film, slug=kwargs['slug'])
        film.vu = True
        film.save()
        messages.success(self.request, 'Film vu !')
        return reverse('cine:films')


class CinephileListView(CinephileRequiredMixin, ListView):
    queryset = Cinephile.objects.filter(actif=True)


class RajQuitView(CinephileRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.request.user.cinephile.actif = False
        self.request.user.cinephile.save()
        messages.error(self.request, 'Vous ne faites plus partie du Ciné Club.')
        return reverse('cine:home')


class SoireeCreateView(CinephileRequiredMixin, CreateView):
    model = Soiree
    form_class = SoireeForm

    def form_valid(self, form):
        form.instance.hote = self.request.user
        messages.info(self.request, 'Soirée Créée')
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.has_adress():
            return reverse('cine:home')
        return reverse('cine:adress')


class SoireeDeleteView(CinephileRequiredMixin, DeleteView):
    model = Soiree
    success_url = reverse_lazy('cine:home')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if not self.request.user.is_superuser and obj.hote != self.request.user:
            raise PermissionDenied
        return obj


class DTWUpdateView(CinephileRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        soiree = get_object_or_404(Soiree, pk=kwargs['pk'])
        if int(kwargs['dispo']):
            request.user.cinephile.soirees.add(soiree)
        else:
            if soiree.hote == request.user:
                messages.error(request, 'Si tu hébèrges une soirée, tu y vas… Supprime la soirée, ou contacte Nim.')
                return redirect('cine:home')
            request.user.cinephile.soirees.remove(soiree)
        messages.info(request, 'Disponibilité mise à jour !')
        return redirect(soiree)


class AdressUpdateView(CinephileRequiredMixin, UpdateView):
    fields = ['adresse']
    success_url = reverse_lazy('cine:home')

    def get_object(self, queryset=None):
        return self.request.user.cinephile

    def form_valid(self, form):
        messages.info(self.request, 'Adresse mise à jour')
        return super().form_valid(form)


class SoireeListView(ListView):
    queryset = Soiree.objects.a_venir
    template_name = 'cine/soiree_list.html'
