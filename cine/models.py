import re
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.safestring import mark_safe

import requests
from ndh.models import Links, NamedModel, TimeStampedModel
from ndh.utils import full_url

CHOIX_ANNEES = [(annee, annee) for annee in range(date.today().year + 2, 1900, -1)]

IMDB_API_URL = "http://www.omdbapi.com/"


class Film(Links, NamedModel):
    respo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    annee_sortie = models.IntegerField(
        choices=CHOIX_ANNEES, blank=True, null=True, verbose_name="Année de sortie"
    )

    titre_vo = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Titre en VO"
    )
    allocine = models.URLField(blank=True, null=True, verbose_name="Allociné")
    realisateur = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Réalisateur"
    )
    duree = models.IntegerField("Durée en minutes", null=True)

    vu = models.BooleanField(default=False)

    imdb_id = models.CharField(
        max_length=10, verbose_name="id IMDB", null=True, blank=True
    )

    imdb_poster_url = models.URLField(
        blank=True, null=True, verbose_name="URL du poster"
    )
    imdb_poster = models.ImageField(upload_to="cine/posters", blank=True, null=True)

    class Meta:
        ordering = ["vu", "name"]

    def save(self, *args, **kwargs):
        if (
            self.pk is None
            or Film.objects.get(pk=self.pk).imdb_poster_url != self.imdb_poster_url
        ):
            img = requests.get(self.imdb_poster_url)
            if img.status_code == requests.codes.ok:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(img.content)
                img_temp.flush()
                self.imdb_poster.save(self.slug, File(img_temp), save=False)
                img_temp.close()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("cine:film", kwargs={"slug": self.slug})

    @staticmethod
    def get_imdb_dict(imdb_id):
        try:
            imdb_id = re.search(r"tt\d+", imdb_id).group()
            imdb_infos = requests.get(
                IMDB_API_URL, params={"i": imdb_id, "apikey": settings.OMDB_API_KEY}
            ).json()
            try:
                search = re.search(
                    r"((?P<hours>\d+) h )?(?P<minutes>\d+) min", imdb_infos["Runtime"]
                )
                hours_min = {
                    key: int(value) if value else 0
                    for key, value in search.groupdict().items()
                }
                duree = int(timedelta(**hours_min).seconds / 60)
            except:
                duree = None
            return {
                "realisateur": imdb_infos["Director"],
                "description": imdb_infos["Plot"],
                "imdb_poster_url": imdb_infos["Poster"],
                "annee_sortie": imdb_infos["Year"],
                "name": imdb_infos["Title"],
                "titre_vo": imdb_infos["Title"],
                "duree": duree,
                "imdb_id": imdb_id,
            }
        except:
            return {}


class SoireeQuerySet(models.QuerySet):
    def a_venir(self):
        return self.filter(moment__gte=timezone.now() - timedelta(days=1))


class Soiree(TimeStampedModel):
    moment = models.DateTimeField()
    hote = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    favoris = models.ForeignKey(Film, null=True, on_delete=models.SET_NULL)

    objects = SoireeQuerySet.as_manager()

    class Meta:
        ordering = ["moment"]
        get_latest_by = "moment"

    def __str__(self):
        return f"Soirée du {self.moment:%c}"

    def save(self, *args, **kwargs):
        nouvelle = self.pk is None
        super(Soiree, self).save(*args, **kwargs)
        self.hote.cinephile.soirees.add(self)
        if nouvelle and not settings.DEBUG:
            ctx = {
                "hote": self.hote,
                "moment": self.moment,
                "lien": full_url(reverse("cine:dtw", args=(self.pk, 1))),
            }
            text, html = (
                get_template(f"cine/mail.{alt}").render(ctx) for alt in ["txt", "html"]
            )
            emails = [
                cinephile.user.email
                for cinephile in Cinephile.objects.filter(actif=True)
            ]
            msg = EmailMultiAlternatives(
                "Soirée Ajoutée !", text, settings.DEFAULT_FROM_EMAIL, emails
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

    def get_absolute_url(self):
        return reverse("cine:soiree", kwargs={"pk": self.pk})

    def presents(self):
        presents = ", ".join(
            [cinephile.user.username for cinephile in self.cinephile_set.all()]
        )
        mails = ",".join(
            [cinephile.user.email for cinephile in self.cinephile_set.all()]
        )

        subject = urlquote(f"[CinéNim] {self} chez {self.hote}")
        return mark_safe(
            f'{presents} – <a href="mailto:{mails}?subject={subject}">Leur envoyer un mail</a>'
        )

    def has_adress(self):
        return bool(self.hote.cinephile.adresse)

    def adress_query(self):
        return self.hote.cinephile.adresse.replace("\n", "+").replace("\r", "")


class Cinephile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.TextField(blank=True)
    soirees = models.ManyToManyField(Soiree, blank=True)
    actif = models.BooleanField(default=True)
    should_vote = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return str(self.user)
