import re
from datetime import datetime, time, timedelta

import requests
from pytz import timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db.models import (BooleanField, CharField, DateField, ForeignKey, ImageField, IntegerField, Model, OneToOneField, QuerySet, SlugField, TextField,
                              TimeField, URLField)
from django.template.defaultfilters import slugify

tzloc = timezone(settings.TIME_ZONE).localize


CHOIX_ANNEES = [(annee, annee) for annee in range(datetime.now().year + 2, 1900, -1)]

IMDB_API_URL = 'http://www.omdbapi.com/'


def get_cinephiles():
    return User.objects.filter(groups__name='cine')


def full_url(path):
    return 'https://%s%s' % (Site.objects.get_current().domain, path)


def get_verbose_name(model, name):
    try:
        return model._meta.get_field(name).verbose_name
    except:
        return None


class Film(Model):
    titre = CharField(max_length=200, unique=True)
    respo = ForeignKey(User)
    description = TextField()
    slug = SlugField(unique=True, blank=True)
    annee_sortie = IntegerField(choices=CHOIX_ANNEES, blank=True, null=True, verbose_name="Année de sortie")

    titre_vo = CharField(max_length=200, blank=True, null=True, verbose_name="Titre en VO")
    imdb = URLField(blank=True, null=True, verbose_name="IMDB")
    allocine = URLField(blank=True, null=True, verbose_name="Allociné")
    realisateur = CharField(max_length=200, null=True, blank=True, verbose_name="Réalisateur")
    duree = CharField(max_length=20, null=True, blank=True, verbose_name="Durée")
    duree_min = IntegerField("Durée en minutes", null=True)

    vu = BooleanField(default=False)

    imdb_id = CharField(max_length=10, verbose_name="id IMDB", null=True, blank=True)

    imdb_poster_url = URLField(blank=True, null=True, verbose_name="URL du poster")
    imdb_poster = ImageField(upload_to='cine/posters', blank=True, null=True)

    def save(self, *args, **kwargs):
        update = self.pk is None
        if not update:
            orig = Film.objects.get(pk=self.pk)
            if orig.slug != self.slug or orig.imdb_poster_url != self.imdb_poster_url:
                update = True
        if update:
            self.slug = slugify(self.titre)
            img = requests.get(self.imdb_poster_url)
            if img.status_code == requests.codes.ok:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(img.content)
                img_temp.flush()
                self.imdb_poster.save(self.slug, File(img_temp), save=False)
                img_temp.close()
        super(Film, self).save(*args, **kwargs)

        if update:
            self.nouveau()

    def nouveau(self):
        # Création des votes & envoi des mails de notif
        film_url = self.get_full_url()
        vote_url = full_url(reverse('cine:votes'))

        message = "Hello :)\n\n%s a proposé un nouveau film : %s (%s)' ; " % (self.respo, self.titre, film_url)
        message += "tu peux donc aller actualiser ton classement (%s) \\o/ \n\n @+!" % vote_url

        for cinephile in get_cinephiles():
            vote = Vote.objects.get_or_create(film=self, cinephile=cinephile)
            if vote[1] and settings.PROD:
                cinephile.email_user('[CinéNim] Film ajouté !', message)

    def get_absolute_url(self):
        return reverse('cine:film', kwargs={'slug': self.slug})

    def get_full_url(self):
        return full_url(self.get_absolute_url())

    def get_description(self):
        return self.description.replace('\r\n', '\\n')

    def score_absolu(self):
        score = 0
        for vote in self.vote_set.all():
            score -= vote.choix
        return score

    @staticmethod
    def get_imdb_dict(imdb_id):
        try:
            imdb_id = re.search(r'tt\d+', imdb_id).group()
            imdb_infos = requests.get(IMDB_API_URL, params={'i': imdb_id}).json()
            try:
                duree = int(timedelta(**dict([
                            (key, int(value) if value else 0) for key, value in
                            re.search(r'((?P<hours>\d+) h )?(?P<minutes>\d+) min', imdb_infos['Runtime']).groupdict().items()
                            ])).seconds / 60)  # TGCM
            except:
                duree = 0
            return {
                    'realisateur': imdb_infos['Director'],
                    'description': imdb_infos['Plot'],
                    'imdb_poster_url': imdb_infos['Poster'],
                    'annee_sortie': imdb_infos['Year'],
                    'titre': imdb_infos['Title'],
                    'titre_vo': imdb_infos['Title'],
                    'duree_min': duree,
                    'imdb_id': imdb_id,
                    'imdb': 'http://www.imdb.com/title/%s/' % imdb_id,
                    }
        except:
            return {}

    def __str__(self):
        return self.titre


class VoteQuerySet(QuerySet):
    def veto(self):
        return self.filter(veto=True)


class Vote(Model):
    film = ForeignKey(Film)
    cinephile = ForeignKey(User)
    choix = IntegerField(default=9999)
    veto = BooleanField(default=False)

    objects = VoteQuerySet.as_manager()

    def __str__(self):
        return '%i \t %s \t %s' % (self.choix, self.cinephile, self.film)

    class Meta:
        ordering = ['choix', 'film']
        unique_together = ("film", "cinephile")


class SoireeQuerySet(QuerySet):
    def a_venir(self):
        return self.filter(date__gte=tzloc(datetime.now() - timedelta(hours=5)))


class Soiree(Model):
    date = DateField()
    time = TimeField('heure', default=time(20, 30))
    hote = ForeignKey(User)
    favoris = ForeignKey(Film, null=True)

    objects = SoireeQuerySet.as_manager()

    def save(self, *args, **kwargs):
        nouvelle = self.pk is None
        super(Soiree, self).save(*args, **kwargs)
        if nouvelle:
            self.nouvelle()

    def nouvelle(self):
        dispos_url = full_url(reverse('cine:home'))

        message = 'Hello :) \n\n%s a proposé une soirée %s à %s; tu peux donc aller mettre à jour tes disponibilités (%s) \\o/\n\n@+!'
        message %= (self.hote, self.date.strftime('%A %d %B'), self.time.strftime('%H:%M'), dispos_url)
        for cinephile in get_cinephiles():
            dtw, created = DispoToWatch.objects.get_or_create(soiree=self, cinephile=cinephile)
            if cinephile == self.hote:
                dtw.dispo = 'O'
                dtw.save()
            if not settings.DEBUG and not settings.INTEGRATION and created:
                cinephile.email_user('[CinéNim] Soirée Ajoutée !', message)

    def datetime(self, time=None):
        if time is None:
            time = self.time
        return datetime.combine(self.date, time)

    def dtstart(self, time=None):
        return tzloc(self.datetime(time)).astimezone(timezone('utc')).strftime('%Y%m%dT%H%M%SZ')

    def dtend(self):
        return self.dtstart(time(23, 59))

    def dispos(self, dispo='O'):
        return [dtw.cinephile for dtw in self.dispotowatch_set.filter(dispo=dispo)]

    def dispos_str(self, dispo):
        return ", ".join([cinephile.username for cinephile in self.dispos(dispo)])

    def presents(self):
        return self.dispos_str('O')

    def pas_surs(self):
        return self.dispos_str('N')

    def score_films(self):
        films = []
        n = Film.objects.filter(vu=False).count() * self.dispotowatch_set.filter(dispo='O').count() + 1
        for film in Film.objects.filter(vu=False):
            score = n
            for dispo in self.dispotowatch_set.filter(dispo='O'):
                vote = film.vote_set.get(cinephile=dispo.cinephile)
                if vote.veto:
                    break
                score -= vote.choix + dispo.cinephile.vote_set.filter(veto=True).count()
            else:
                films.append((score, film, film.respo.dispotowatch_set.a_venir().get(soiree=self).dispo == 'O'))
        films.sort(key=lambda x: x[0])
        films.reverse()
        return films

    def update_favori(self):
        if self.dispotowatch_set.filter(dispo='O').exists():
            scores = self.score_films()
            if scores:
                self.favoris = scores[0][1]
                self.save()

    def has_adress(self):
        return Adress.objects.filter(user=self.hote).exists()

    def adress_ics(self):
        return self.hote.adress.adresse.replace('\n', ' ').replace('\r', '')

    def adress_query(self):
        return self.adress_ics().replace(' ', '+')

    def __str__(self):
        return 'soirée du %s' % self.date

    class Meta:
        ordering = ["date"]
        get_latest_by = 'date'


class DispoQuerySet(QuerySet):
    def a_venir(self):
        return self.filter(soiree__date__gte=tzloc(datetime.now() - timedelta(hours=5)))


class DispoToWatch(Model):
    soiree = ForeignKey(Soiree)
    cinephile = ForeignKey(User)

    objects = DispoQuerySet.as_manager()

    CHOIX_DISPO = (
            ('O', 'Dispo'),
            ('P', 'Pas dispo'),
            ('N', 'Ne sais pas'),
            )

    dispo = CharField(max_length=1, choices=CHOIX_DISPO, default='N')

    def __str__(self):
        return '%s %s %s' % (self.soiree, self.dispo, self.cinephile)

    class Meta:
        ordering = ['soiree__date']
        unique_together = ("soiree", "cinephile")


class Adress(Model):
    user = OneToOneField(User)
    adresse = TextField()

    def __str__(self):
        return 'Adresse de %s' % self.user

    class Meta:
        verbose_name_plural = 'Adresses'
