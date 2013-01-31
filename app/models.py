from django.db.models import CharField, DateField, DateTimeField, IntegerField
from django.db.models import URLField, TextField, ImageField, BooleanField
from django.db.models import Model, ForeignKey, ManyToManyField
from django.contrib.auth.models import User


class Film(Model):
    titre = CharField(max_length=200,primary_key=True)
    respo = ForeignKey(User)
    description = TextField()

    CHOIX_CATEGORIE = (
            ('D', 'Divertissement'),
            ('C', 'Culture'),
            )

    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    titre_vo = CharField(max_length=200,blank=True, null=True)
    imdb = URLField(blank=True, null=True)
    allocine = URLField(blank=True, null=True)

    def score(self):
        score = 0
        for vote in self.vote_set.all():
            score -= vote.choix
            if vote.plusse:
                score += 1
        return score

    def __unicode__(self):
        return self.titre


class Vote(Model):
    film = ForeignKey(Film)
    personne = ForeignKey(User)
    choix = IntegerField()
    plusse = BooleanField(default=False)

    unique_together = (("film", "personne"), ("personne", "choix"))

    def __unicode__(self):
        if self.plusse:
            return u'%s \t %i + \t %s' % (self.film, self.choix, self.personne)
        return u'%s \t %i \t %s' % (self.film, self.choix, self.personne)


class Date(Model):
    date = DateField()
    personne = ForeignKey(User)

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
