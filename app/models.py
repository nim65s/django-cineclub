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


class Film(Model):
    titre = CharField(max_length=200,primary_key=True)
    respo = ForeignKey(User)
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
        for personne in User.objects.all():
            try:
                Vote.objects.get(film=self, personne=personne)
            except Vote.DoesNotExist:
                v = Vote()
                v.choix = N
                v.film = self
                v.personne = personne
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
    personne = ForeignKey(User)
    choix = IntegerField()
    plusse = BooleanField(default=False)

    unique_together = ("film", "personne")

    def __unicode__(self):
        if self.plusse:
            return u'%s \t %i + \t %s' % (self.film, self.choix, self.personne)
        return u'%s \t %i \t %s' % (self.film, self.choix, self.personne)


class Date(Model):
    date = DateField()
    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    def save(self, *args, **kwargs):
        # Création des Dispos
        for personne in User.objects.all():
            try:
                Dispo.objects.get(date=self, personne=personne)
            except Dispo.DoesNotExist:
                d = Dispo()
                d.date = self
                d.personne = personne
                d.dispo = 'N'
                d.save()
        super(Date, self).save(*args, **kwargs)

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
    date = ForeignKey(Date)
    personne = ForeignKey(User)

    unique_together = ("date", "personne")

    CHOIX_DISPO = (
            ('O', 'Dispo'),
            ('P', 'Pas dispo'),
            ('N', 'Ne sais pas'),
            )

    dispo = CharField(max_length=1, choices=CHOIX_DISPO, default='N')

    def __unicode__(self):
        return u'%s %s %s' % (self.date, self.dispo, self.personne)


class Commentaire(Model):
    date = DateTimeField(auto_now=True, auto_now_add=True)
    posteur = ForeignKey(User)
    film = ForeignKey(Film)
    commentaire = TextField()
