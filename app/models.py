#-*- coding: utf-8 -*-
from django.db.models import URLField, TextField, ImageField, BooleanField, SlugField
from django.db.models import CharField, DateField, DateTimeField, IntegerField
from django.db.models import Model, ForeignKey, ManyToManyField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.forms import ModelForm

from django.core.mail import EmailMultiAlternatives

from email.MIMEText import MIMEText
from email.Header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CHOIX_CATEGORIE = (
        ('D', 'Divertissement'),
        ('C', 'Culture'),
        )


class Film(Model):
    titre = CharField(max_length=200, unique=True)
    respo = ForeignKey(User)
    description = TextField()
    slug = SlugField(unique=True, blank=True)

    categorie = CharField(max_length=1, choices=CHOIX_CATEGORIE, default='D')

    titre_vo = CharField(max_length=200,blank=True, null=True)
    imdb = URLField(blank=True, null=True)
    allocine = URLField(blank=True, null=True)
    realisateur = CharField(max_length=200, null=True, blank=True)
    duree = CharField(max_length=20, null=True, blank=True)

    vu = BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)
        super(Film, self).save(*args, **kwargs)

        # Création des votes & envoi des mails de notif
        N = len(Film.objects.all()) + 1

        subject = u"[CineNim] Film ajouté !"
        mailfrom = u'notifications@cine.saurel.me'

        message_html = u"Hello :) <br /><br />%s a proposé un nouveau film : <a href='http://cine.saurel.me/films#%s'>%s</a>.<br />" % (self.respo.username, self.slug, self.titre )
        message_html += u"Tu peux donc aller actualiser ton <a href='http://cine.saurel.me/votes'>classement</a> \\o/ <br /><br /> @+ !"
        message_txt = u"Hello :)\n\n%s a proposé un nouveau film : %s (http://cine.saurel.me/films#%s' ; " % (self.respo.username, self.titre, self.slug )
        message_txt += u"tu peux donc aller actualiser ton classement (http://cine.saurel.me/votes) \\o/ \n\n @+!"

        for cinephile in User.objects.all():
            try:
                Vote.objects.get(film=self, cinephile=cinephile)
            except Vote.DoesNotExist:
                v = Vote()
                v.choix = N
                v.film = self
                v.cinephile = cinephile
                v.save()

                msg = EmailMultiAlternatives(subject, message_txt, mailfrom, [cinephile.email])
                msg.attach_alternative(message_html, "text/html")
                msg.send()

    def get_categorie(self):
        return dict(CHOIX_CATEGORIE)[self.categorie]

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


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('password', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['last_login'].widget.attrs['readonly'] = True
            self.fields['date_joined'].widget.attrs['readonly'] = True

    def clean_last_login(self):
        return self.instance.last_login

    def clean_date_joined(self):
        return self.instance.date_joined


class Vote(Model):
    film = ForeignKey(Film)
    cinephile = ForeignKey(User)
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

        subject = u'[CineNim] Soirée ajoutée !'
        mailfrom = u'notifications@cine.saurel.me'

        message_html = u'Hello :) <br /><br />Le %s, une soirée %s est proposée ; tu peux donc aller mettre à jour tes <a href="http://cine.saurel.me/dispos">disponibilités</a> \\o/ <br /><br />@+ !' % (self.date, self.get_categorie())
        message_txt = u'Hello :) \n\nLe %s, une soirée %s est proposée ; tu peux donc aller mettre à jour tes disponibilités : http://cine.saurel.me/dispos \\o/ \n\n@+ !' % (self.date, self.get_categorie())

        for cinephile in User.objects.all():
            try:
                Dispo.objects.get(soiree=self, cinephile=cinephile)
            except Dispo.DoesNotExist:
                d = Dispo()
                d.soiree = self
                d.cinephile = cinephile
                d.dispo = 'N'
                d.save()

                msg = EmailMultiAlternatives(subject, message_txt, mailfrom, [cinephile.email])
                msg.attach_alternative(message_html, "text/html")
                msg.send()

    def get_categorie(self):
        return dict(CHOIX_CATEGORIE)[self.categorie]

    def presents(self):
        return ", ".join([ cinephile.cinephile.username for cinephile in self.dispo_set.filter(dispo='O')])

    def pas_surs(self):
        return ", ".join([ cinephile.cinephile.username for cinephile in self.dispo_set.filter(dispo='N')])

    def __unicode__(self):
        return u'%s:%s' % (self.date, self.categorie)


class Dispo(Model):
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


class Commentaire(Model):
    date = DateTimeField(auto_now=True, auto_now_add=True)
    posteur = ForeignKey(User)
    film = ForeignKey(Film)
    commentaire = TextField()

    # TODO: mail \o/


class CommForm(ModelForm):
    class Meta:
        model = Commentaire
        exclude = ('date', 'posteur', 'film')
