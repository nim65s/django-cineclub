#-*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMultiAlternatives
from django.db.models import URLField, TextField, ImageField, BooleanField, SlugField
from django.db.models import CharField, DateTimeField, IntegerField
from django.db.models import Model, ForeignKey, ManyToManyField
from django.forms import ModelForm
from django.template.defaultfilters import slugify

from email.MIMEText import MIMEText
from email.Header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging
logger = logging.getLogger(__name__)

CHOIX_CATEGORIE = (
        ('D', 'Divertissement'),
        ('C', 'Culture'),
        )


def get_cinephiles():
    return Group.objects.get_or_create(name='cine')[0].user_set.all()


class Film(Model):
    titre = CharField(max_length=200, unique=True)
    respo = ForeignKey(User)
    description = TextField()
    slug = SlugField(unique=True, blank=True)

    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    titre_vo = CharField(max_length=200, blank=True, null=True)
    imdb = URLField(blank=True, null=True)
    allocine = URLField(blank=True, null=True)
    realisateur = CharField(max_length=200, null=True, blank=True)
    duree = CharField(max_length=20, null=True, blank=True)

    vu = BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)
        super(Film, self).save(*args, **kwargs)

        # Création des votes & envoi des mails de notif
        subject = u"[CineNim] Film ajouté !"
        mailfrom = u'cine@perso.saurel.me'

        message_html = u"Hello :) <br /><br />%s a proposé un nouveau film : <a href='http://perso.saurel.me/cine/films#%s'>%s</a>.<br />" % (
                self.respo.username, self.slug, self.titre)
        message_html += u"Tu peux donc aller actualiser ton <a href='http://perso.saurel.me/cine/votes'>classement</a> \\o/ <br /><br /> @+ !"
        message_txt = u"Hello :)\n\n%s a proposé un nouveau film : %s (http://perso.saurel.me/cine/films#%s' ; " % (
                self.respo.username, self.titre, self.slug)
        message_txt += u"tu peux donc aller actualiser ton classement (http://perso.saurel.me/cine/votes) \\o/ \n\n @+!"

        for cinephile in get_cinephiles():
            vote = Vote.objects.get_or_create(film=self, cinephile=cinephile)
            if vote[1] and not settings.DEBUG:
                try:
                    msg = EmailMultiAlternatives(subject, message_txt, mailfrom, [cinephile.email])
                    msg.attach_alternative(message_html, "text/html")
                    msg.send()
                except:
                    logger.error(u'Le mail de nouveau film %s pour %s n’a pas été envoyé' % (self.titre, cinephile))

    def get_categorie(self):
        return dict(CHOIX_CATEGORIE)[self.categorie]

    def get_description(self):
        return self.description.replace('\r\n','\\n')

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
        exclude = ('respo', 'slug', 'vu')


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


class Soiree(Model):
    date = DateTimeField()
    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')
    favoris = ForeignKey(Film, null=True)

    def save(self, *args, **kwargs):
        super(Soiree, self).save(*args, **kwargs)

        subject = u'[CineNim] Soirée ajoutée !'
        mailfrom = u'cine@perso.saurel.me'

        message_html = u'Hello :) <br /><br />Le %s, une soirée %s est proposée ; ' % (self.date, self.get_categorie())
        message_html += u'tu peux donc aller mettre à jour tes <a href="http://perso.saurel.me/cine/dispos">disponibilités</a> \\o/ <br><br>@+ !'
        message_txt = u'Hello :) \n\nLe %s, une soirée %s est proposée ; ' % (self.date, self.get_categorie())
        message_html += u'tu peux donc aller mettre à jour tes disponibilités : http://perso.saurel.me/cine/dispos \\o/ \n\n@+ !'

        for cinephile in get_cinephiles():
            dtw = DispoToWatch.objects.get_or_create(soiree=self, cinephile=cinephile)
            if not settings.DEBUG and dtw[1]:
                try:
                    msg = EmailMultiAlternatives(subject, message_txt, mailfrom, [cinephile.email])
                    msg.attach_alternative(message_html, "text/html")
                    msg.send()
                except:
                    logger.error(u'Le mail de nouvelle dispotowatch %s n’a pas été envoyée' % dtw[0])

    def get_categorie(self):
        return dict(CHOIX_CATEGORIE)[self.categorie]

    def presents(self):
        return ", ".join([cinephile.cinephile.username for cinephile in self.dispotowatch_set.filter(dispo='O')])

    def pas_surs(self):
        return ", ".join([cinephile.cinephile.username for cinephile in self.dispotowatch_set.filter(dispo='N')])

    def __unicode__(self):
        return u'%s:%s' % (self.date, self.categorie)

    class Meta:
        ordering = ["date"]


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


class Commentaire(Model):
    date = DateTimeField(auto_now=True, auto_now_add=True)
    posteur = ForeignKey(User)
    film = ForeignKey(Film)
    commentaire = TextField()

    def save(self, *args, **kwargs):
        super(Commentaire, self).save(*args, **kwargs)

        if not settings.DEBUG:
            subject = u'[CineNim] Nouveau commentaire sur %s' % self.film.titre
            mailfrom = u'cine@perso.saurel.me'

            message_html = u'Hello :) <br /><br />%s a posté un nouveau commentaire sur %s: ' % (self.posteur.username, self.film.titre)
            message_html += u'vous pouvez aller le voir <a href="http://perso.saurel.me/cine/comms/%s">ici</a> \\o/ <br /><br />@+ !' % self.film.slug
            message_txt = u'Hello :) \n\n%s a posté un nouveau commentaire sur %s: ' % (self.posteur.username, self.film.titre)
            message_html += u'vous pouvez aller le voir sur http://perso.saurel.me/cine/comms/%s \\o/ \n\n@+ !' % self.film.slug

            try:
                msg = EmailMultiAlternatives(subject, message_txt, mailfrom, ['cinenim@list.bde.enseeiht.fr'])
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except:
                logger.error(u'Le mail de commentaire %s n’a pas été envoyée' % self)

    def __unicode__(self):
        return u'Commentaire de %s sur %s le %s: %s' % (self.posteur.username, self.film.titre, self.date, self.commentaire[:20])

    class Meta:
        ordering = ['date']


class CommForm(ModelForm):
    class Meta:
        model = Commentaire
        exclude = ('date', 'posteur', 'film')
