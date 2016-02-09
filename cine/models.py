import re
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import (Q, BooleanField, CharField, DateField, ForeignKey, ImageField,
                              IntegerField, ManyToManyField, Model, OneToOneField, QuerySet,
                              SlugField, TextField, TimeField, URLField)
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.utils.safestring import mark_safe

import requests
from pytz import timezone
from sortedm2m.fields import SortedManyToManyField

tzloc = timezone(settings.TIME_ZONE).localize


CHOIX_ANNEES = [(annee, annee) for annee in range(datetime.now().year + 2, 1900, -1)]

IMDB_API_URL = 'http://www.omdbapi.com/'


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
    duree = IntegerField("Durée en minutes", null=True)

    vu = BooleanField(default=False)

    imdb_id = CharField(max_length=10, verbose_name="id IMDB", null=True, blank=True)

    imdb_poster_url = URLField(blank=True, null=True, verbose_name="URL du poster")
    imdb_poster = ImageField(upload_to='cine/posters', blank=True, null=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['vu', 'titre']

    def save(self, *args, **kwargs):
        update = self.pk is None
        if not update:
            orig = Film.objects.get(pk=self.pk)
            if orig.slug != self.slug or orig.imdb_poster_url != self.imdb_poster_url:
                update = True
        if update:
            self.slug = slugify(self.titre)[:48]
            img = requests.get(self.imdb_poster_url)
            if img.status_code == requests.codes.ok:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(img.content)
                img_temp.flush()
                self.imdb_poster.save(self.slug, File(img_temp), save=False)
                img_temp.close()
        super(Film, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cine:film', kwargs={'slug': self.slug})

    def get_link(self):
        return mark_safe('<a href="%s">%s</a>' % (self.get_absolute_url(), self.titre))

    def get_full_url(self):
        return full_url(self.get_absolute_url())

    def get_description(self):
        return self.description.replace('\r\n', '\\n')

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
                duree = None
            return {
                'realisateur': imdb_infos['Director'],
                'description': imdb_infos['Plot'],
                'imdb_poster_url': imdb_infos['Poster'],
                'annee_sortie': imdb_infos['Year'],
                'titre': imdb_infos['Title'],
                'titre_vo': imdb_infos['Title'],
                'duree': duree,
                'imdb_id': imdb_id,
                'imdb': 'http://www.imdb.com/title/%s/' % imdb_id,
            }
        except:
            return {}


class SoireeQuerySet(QuerySet):
    def a_venir(self):
        return self.filter(date__gte=tzloc(datetime.now() - timedelta(hours=5)))


class Soiree(Model):
    date = DateField()
    time = TimeField('heure', default=time(20, 30))
    hote = ForeignKey(User)
    favoris = ForeignKey(Film, null=True)

    objects = SoireeQuerySet.as_manager()

    def __str__(self):
        return 'soirée du %s' % self.date

    class Meta:
        ordering = ["date"]
        get_latest_by = 'date'

    def get_absolute_url(self):
        return reverse('cine:soiree', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        nouvelle = self.pk is None
        super(Soiree, self).save(*args, **kwargs)
        self.hote.cinephile.soirees.add(self)
        if nouvelle:
            ctx = {'hote': self.hote, 'date': self.date, 'time': self.time,
                   'lien': full_url(reverse('cine:dtw', args=(self.pk, 1)))}
            text, html = (get_template('cine/mail.%s' % alt).render(ctx) for alt in ['txt', 'html'])
            emails = [cinephile.user.email for cinephile in Cinephile.objects.filter(actif=True)]
            msg = EmailMultiAlternatives('Soirée Ajoutée !', text, settings.DEFAULT_FROM_EMAIL, emails)
            msg.attach_alternative(html, 'text/html')
            if not settings.DEBUG:
                msg.send()

    def datetime(self, time=None):
        return datetime.combine(self.date, self.time if time is None else time)

    def dtstart(self, time=None):
        return tzloc(self.datetime(time)).astimezone(timezone('utc')).strftime('%Y%m%dT%H%M%SZ')

    def dtend(self):
        return self.dtstart(time(23, 59))

    def presents(self):
        return ", ".join([cinephile.user.username for cinephile in self.cinephile_set.all()])

    def cache_name(self):
        return 'soiree_%i' % self.pk

    def score_films_short(self):
        return self.score_films()[:5]

    def score_films(self, update=False):
        films = None if update else cache.get(self.cache_name())
        if films is None:
            films = self.compute_score_films()
        cache.set(self.cache_name(), films, 3600 * 24 * 30)
        return films

    def compute_score_films(self):
        films = Film.objects.filter(vu=False).exclude(vetos__soirees=self)
        n = len(films) * self.cinephile_set.count()
        scores = {film: n for film in films}
        for cinephile in self.cinephile_set.all():
            for score, film in enumerate(cinephile.votes.all()):
                if film in scores:
                    scores[film] -= score
            for film in cinephile.pas_classes():
                if film in scores:
                    scores[film] -= n
        films = sorted([(score, film) for film, score in scores.items()], key=lambda x: -x[0])
        if films and self.favoris != films[0][1]:
            self.favoris = films[0][1]
            self.save()
        return films

    def has_adress(self):
        return bool(self.hote.cinephile.adresse)

    @staticmethod
    def update_scores(cinephile=None):
        soirees = Soiree.objects if cinephile is None else cinephile.soirees
        for soiree in soirees.a_venir():
            soiree.score_films(update=True)

    def adress_ics(self):
        return self.hote.cinephile.adresse.replace('\n', ' ').replace('\r', '')

    def adress_query(self):
        return self.adress_ics().replace(' ', '+')


class Cinephile(Model):
    user = OneToOneField(User)
    adresse = TextField(blank=True)
    votes = SortedManyToManyField(Film, blank=True)
    vetos = ManyToManyField(Film, blank=True, related_name='vetos')
    soirees = ManyToManyField(Soiree, blank=True)
    actif = BooleanField(default=True)

    def __str__(self):
        return '%s' % self.user

    class Meta:
        ordering = ["user__username"]

    def pas_classes(self):
        query = Q(vu=True) | Q(pk__in=self.votes.all()) | Q(pk__in=self.vetos.all())
        return Film.objects.exclude(query)
