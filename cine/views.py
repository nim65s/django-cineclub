from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import RedirectView

from .forms import SoireeForm
from .models import Cinephile, Film, Soiree


class CinephileRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated():
            return False
        if Cinephile.objects.filter(user=self.request.user, actif=True).exists():
            return True
        messages.error(self.request, 'Vous ne faites pas partie du cinéclub :(')
        return False


# TODO: this is a PoC… clean it.
class VotesView(CinephileRequiredMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        ordre = request.POST['ordre'].split(',')
        if ordre:
            request.user.cinephile.votes.clear()
            films = [get_object_or_404(Film, slug=slug, vu=False) for slug in ordre if slug]
            for film in films:
                request.user.cinephile.votes.add(film)
                request.user.cinephile.save()
                Soiree.update_scores(request.user.cinephile)
            return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'cine/votes.html', {
            'films': request.user.cinephile.votes.all(),
            'vetos': request.user.cinephile.vetos.all(),
            'pas_classes': request.user.cinephile.pas_classes(),
        })


class ICS(ListView):
    template_name = 'cine/cinenim.ics'
    content_type = "text/calendar; charset=UTF-8"
    queryset = Soiree.objects.a_venir()


class FilmActionMixin(CinephileRequiredMixin):
    model = Film
    fields = ('titre', 'description', 'annee_sortie', 'titre_vo', 'realisateur', 'imdb', 'allocine',
              'duree', 'imdb_poster_url', 'imdb_id')

    def form_valid(self, form):
        messages.info(self.request, "Film %s" % self.action)
        return super(FilmActionMixin, self).form_valid(form)


class FilmCreateView(FilmActionMixin, CreateView):
    action = "créé"

    def form_valid(self, form):
        form.instance.respo = self.request.user
        Soiree.update_scores()
        return super(FilmCreateView, self).form_valid(form)

    def get_initial(self):
        return Film.get_imdb_dict(self.request.GET.get('imdb_id'))


class FilmUpdateView(FilmActionMixin, UpdateView):
    action = "modifié"

    def form_valid(self, form):
        if form.instance.respo == self.request.user or self.request.user.is_superuser:
            return super(FilmUpdateView, self).form_valid(form)
        messages.error(self.request, 'Vous n’avez pas le droit de modifier ce film')
        return redirect('cine:films')


class FilmListView(ListView):
    model = Film


class FilmVuView(UserPassesTestMixin, RedirectView):
    def test_func(self):
        return self.request.user.is_superuser

    def get_redirect_url(self, *args, **kwargs):
        film = get_object_or_404(Film, slug=kwargs['slug'])
        film.vu = True
        film.save()
        for cinephile in Cinephile.objects.all():
            cinephile.votes.remove(film)
            cinephile.vetos.remove(film)
        Soiree.update_scores()
        return reverse('cine:films')


class VetoView(CinephileRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        film = get_object_or_404(Film, pk=kwargs['pk'])
        self.request.user.cinephile.votes.remove(film)
        self.request.user.cinephile.vetos.add(film)
        return reverse('cine:votes')


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
        messages.info(self.request, "Soirée Créée")
        return super(SoireeCreateView, self).form_valid(form)

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
            raise PermissionDenied()
        return obj


class DTWUpdateView(CinephileRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        soiree = get_object_or_404(Soiree, pk=kwargs['pk'])
        if int(kwargs['dispo']):
            request.user.cinephile.soirees.add(soiree)
        else:
            if soiree.hote == request.user:
                messages.error(request, "Oui, mais non. Si tu hébèrges une soirée, tu y vas.")
                return redirect('cine:home')
            request.user.cinephile.soirees.remove(soiree)
        soiree.score_films(update=True)
        messages.info(request, "Disponibilité mise à jour !")
        return redirect(soiree)


class AdressUpdateView(CinephileRequiredMixin, UpdateView):
    fields = ['adresse']
    success_url = reverse_lazy('cine:home')

    def get_object(self, queryset=None):
        return self.request.user.cinephile

    def form_valid(self, form):
        messages.info(self.request, "Adresse mise à jour")
        return super(AdressUpdateView, self).form_valid(form)
