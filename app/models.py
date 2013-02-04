#-*- coding: utf-8 -*-
from django.db.models import URLField, TextField, ImageField, BooleanField, SlugField
from django.db.models import CharField, DateField, DateTimeField, IntegerField
from django.db.models import Model, ForeignKey, ManyToManyField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.forms import ModelForm

CHOIX_CATEGORIE = (
        ('D', 'Divertissement'),
        ('C', 'Culture'),
        )


class Cinephile(User):
    def save(self, *args, **kwargs):
        # Création des votes
        N = len(Film.objects.all()) + 1
        for film in Film.objects.all():
            try:
                Vote.objects.get(film=film, cinephile=self)
            except Vote.DoesNotExist:
                v = Vote()
                v.choix = N
                v.film = film
                v.cinephile = self
                v.save()
        for soiree in Soiree.objects.all():
            try:
                Dispo.objects.get(soiree=soiree, cinephile=self)
            except Dispo.DoesNotExist:
                d = Dispo()
                d.dispo = 'N'
                d.soiree = soiree
                d.cinephile = self
                d.save()
        super(Cinephile, self).save(*args, **kwargs)



class Film(Model):
    titre = CharField(max_length=200,primary_key=True)
    respo = ForeignKey(Cinephile)
    description = TextField()
    slug = SlugField(unique=True, blank=True)

    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    titre_vo = CharField(max_length=200,blank=True, null=True)
    imdb = URLField(blank=True, null=True)
    allocine = URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)

        # Création des votes
        N = len(Film.objects.all()) + 1
        for cinephile in Cinephile.objects.all():
            try:
                Vote.objects.get(film=self, cinephile=cinephile)
            except Vote.DoesNotExist:
                v = Vote()
                v.choix = N
                v.film = self
                v.cinephile = cinephile
                v.save()
        super(Film, self).save(*args, **kwargs)

    def get_categorie(self):
        if self.categorie == 'D':
            return 'Divertissement'
        return 'Culture'

    def score_absolu(self):
        score = 0
        for vote in self.vote_set.all():
            score -= vote.choix
            if vote.plusse:
                score += 1
        return score

    def __unicode__(self):
        return self.titre


class FilmForm(ModelForm):
    class Meta:
        model = Film
        exclude = ('respo', 'slug')


class Vote(Model):
    film = ForeignKey(Film)
    cinephile = ForeignKey(Cinephile)
    choix = IntegerField()
    plusse = BooleanField(default=False)

    unique_together = ("film", "cinephile")

    def __unicode__(self):
        if self.plusse:
            return u'%s \t %i + \t %s' % (self.film, self.choix, self.cinephile)
        return u'%s \t %i \t %s' % (self.film, self.choix, self.cinephile)


class Soiree(Model):
    date = DateField()
    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    def save(self, *args, **kwargs):
        super(Soiree, self).save(*args, **kwargs)
        # Création des Dispos
        for cinephile in Cinephile.objects.all():
            try:
                Dispo.objects.get(soiree=self, cinephile=cinephile)
            except Dispo.DoesNotExist:
                d = Dispo()
                d.soiree = self
                d.cinephile = cinephile
                d.dispo = 'N'
                d.save()

    def get_categorie(self):
        if self.categorie == 'D':
            return 'Divertissement'
        return 'Culture'

    def presents(self):
        return self.dispo_set.filter(dispo='O')

    def pas_surs(self):
        return self.dispo_set.filter(dispo='N')

    def __unicode__(self):
        return u'%s:%s' % (self.date, self.categorie)


class Dispo(Model):
    soiree = ForeignKey(Soiree)
    cinephile = ForeignKey(Cinephile)

    unique_together = ("soiree", "cinephile")

    CHOIX_DISPO = (
            ('O', 'Dispo'),
            ('P', 'Pas dispo'),
            ('N', 'Ne sais pas'),
            )

    dispo = CharField(max_length=1, choices=CHOIX_DISPO, default='N')

    def __unicode__(self):
        return u'%s %s %s' % (self.soiree, self.dispo, self.cinephile)


class Commentaire(Model):
    date = DateTimeField(auto_now=True, auto_now_add=True)
    posteur = ForeignKey(Cinephile)
    film = ForeignKey(Film)
    commentaire = TextField()
