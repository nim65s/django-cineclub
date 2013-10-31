#-*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import URLField, TextField, ImageField, BooleanField, SlugField
from django.db.models import CharField, DateTimeField, IntegerField
from django.db.models import Model, ForeignKey, ManyToManyField, Manager
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify

import json
import logging
import re
import requests
from datetime import datetime, timedelta
from PIL import Image
from pytz import timezone
from StringIO import StringIO

logger = logging.getLogger(__name__)
tz = timezone(settings.TIME_ZONE)
tzloc = tz.localize


CHOIX_CATEGORIE = (
        ('D', 'Divertissement'),
        ('C', 'Culture'),
        )
CHOIX_CATEGORIE_DICT = dict(CHOIX_CATEGORIE)

CHOIX_ANNEES = [(annee, annee) for annee in range(datetime.now().year + 1, 1900, -1)]

#IMDB_API_URL = 'http://mymovieapi.com/'
IMDB_API_URL = 'http://www.omdbapi.com/'

def get_cinephiles():
    return User.objects.filter(groups__name='cine')


def full_url(path):
    return u'http://%s%s' % (Site.objects.get_current().domain, path)


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

    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')
    annee_sortie = IntegerField(max_length=4, choices=CHOIX_ANNEES, blank=True, null=True, verbose_name=u"Année de sortie")

    titre_vo = CharField(max_length=200, blank=True, null=True, verbose_name=u"Titre en VO")
    imdb = URLField(blank=True, null=True, verbose_name="IMDB")
    allocine = URLField(blank=True, null=True, verbose_name=u"Allociné")
    realisateur = CharField(max_length=200, null=True, blank=True, verbose_name=u"Réalisateur")
    duree = CharField(max_length=20, null=True, blank=True, verbose_name=u"Durée")
    duree_min = IntegerField(u"Durée en minutes", null=True)

    vu = BooleanField(default=False)

    imdb_id = CharField(max_length=10, verbose_name=u"id IMDB", null=True, blank=True)

    imdb_poster_url = URLField(blank=True, null=True, verbose_name=u"URL du poster")
    imdb_poster = ImageField(upload_to='cine/posters', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)
        img = requests.get(self.imdb_poster_url)
        if img.status_code == requests.codes.ok:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(img.content)
            img_temp.flush()
            self.imdb_poster.save(self.slug, File(img_temp), save=False)
            img_temp.close()
        super(Film, self).save(*args, **kwargs)

        # Création des votes & envoi des mails de notif
        film_url = self.get_full_url()
        vote_url = full_url(reverse('cine:votes'))

        message = u"Hello :)\n\n%s a proposé un nouveau film : %s (%s)' ; " % ( self.respo, self.titre, film_url)
        message += u"tu peux donc aller actualiser ton classement (%s) \\o/ \n\n @+!" % vote_url

        for cinephile in get_cinephiles():
            vote = Vote.objects.get_or_create(film=self, cinephile=cinephile)
            if vote[1] and not settings.DEBUG:
                cinephine.email_user(u'[CinéNim] Film ajouté !', message)

    def get_absolute_url(self):
        return reverse('cine:film', kwargs={'slug': self.slug})

    def get_full_url(self):
        return full_url(self.get_absolute_url())

    def get_categorie(self):
        return CHOIX_CATEGORIE_DICT[self.categorie]

    def get_description(self):
        return self.description.replace('\r\n','\\n')

    def score_absolu(self):
        score = 0
        for vote in self.vote_set.all():
            score -= vote.choix
            if vote.plusse:
                score += 1
        return score

    @staticmethod
    def get_imdb_dict(imdb_id):
        try:
            imdb_infos = requests.get(IMDB_API_URL, params={'i': imdb_id}).json()
            return {
                    'realisateur': imdb_infos['Director'],
                    'description': imdb_infos['Plot'],
                    'imdb_poster_url': imdb_infos['Poster'],
                    'annee_sortie': imdb_infos['Year'],
                    'titre': imdb_infos['Title'],
                    'titre_vo': imdb_infos['Title'],
                    'duree_min': timedelta(**dict([(key, int(value) if value else 0) for key, value in re.search(r'((?P<hours>\d+) h )?(?P<minutes>\d+) min', imdb_infos['Runtime']).groupdict().items()])).seconds / 60,  # TGCM
                    'imdb_id': imdb_id,
                    }
        except:
            return {}

    def __unicode__(self):
        return self.titre


class Vote(Model):
    film = ForeignKey(Film)
    cinephile = ForeignKey(User)
    choix = IntegerField(default=9999)
    plusse = BooleanField(default=False)  # TODO: NYI

    unique_together = ("film", "cinephile")

    def __unicode__(self):
        if self.plusse:
            return u'%s \t %i + \t %s' % (self.film, self.choix, self.cinephile)
        return u'%s \t %i \t %s' % (self.film, self.choix, self.cinephile)

    class Meta:
        ordering = ['choix', 'film']


class SoireeAVenirManager(Manager):
    def get_query_set(self):
        return super(SoireeAVenirManager, self).get_query_set().filter(date__gte=tzloc(datetime.now() - timedelta(hours=5)))


class Soiree(Model):
    date = DateTimeField()
    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D', blank=True)
    favoris = ForeignKey(Film, null=True)

    objects = Manager()
    a_venir = SoireeAVenirManager()

    def save(self, *args, **kwargs):
        if not self.id:
            try:
                if Soiree.objects.latest().categorie == 'C':
                    self.categorie = 'D'
                else:
                    self.categorie = 'C'
            except:
                self.categorie = 'D'  # Si c’est la première soirée
        super(Soiree, self).save(*args, **kwargs)

        dispos_url = full_url(reverse('cine:dispos'))

        message = u'Hello :) \n\nLe %s, une soirée %s est proposée ; ' % (self.date, self.get_categorie())
        message += u'tu peux donc aller mettre à jour tes disponibilités (%s) \\o/ \n\n@+ !' % dispos_url

        for cinephile in get_cinephiles():
            dtw = DispoToWatch.objects.get_or_create(soiree=self, cinephile=cinephile)
            if not settings.DEBUG and dtw[1]:
                cinephile.email_user(u'[CinéNim] Soirée Ajoutée !', message)

    def get_categorie(self):
        return CHOIX_CATEGORIE_DICT[self.categorie]

    def presents(self):
        return ", ".join([cinephile.cinephile.username for cinephile in self.dispotowatch_set.filter(dispo='O')])

    def pas_surs(self):
        return ", ".join([cinephile.cinephile.username for cinephile in self.dispotowatch_set.filter(dispo='N')])

    def __unicode__(self):
        return u'%s:%s' % (self.date, self.categorie)

    class Meta:
        ordering = ["date"]
        get_latest_by = 'date'


class DispoToWatch(Model):
    soiree = ForeignKey(Soiree)
    cinephile = ForeignKey(User)

    unique_together = ("soiree", "cinephile")

    CHOIX_DISPO = (
            ('O', 'Dispo'),
            ('P', 'Pas dispo'),
            ('N', 'Ne sais pas'),
            )

    dispo = CharField(max_length=1, choices=CHOIX_DISPO, default='N')

    def __unicode__(self):
        return u'%s %s %s' % (self.soiree, self.dispo, self.cinephile)

    class Meta:
        ordering = ['soiree__date']
