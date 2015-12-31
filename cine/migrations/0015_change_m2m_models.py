# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 08:48
from __future__ import unicode_literals

from django.db import migrations


def update_cinephile_data(apps, schema_editor):
    Cinephile, Adress, Film, Vote, Soiree, DispoToWatch = (apps.get_model("cine", x) for x in [
            'Cinephile', 'Adress', 'Film', 'Vote', 'Soiree', 'DispoToWatch'])
    User = apps.get_model('auth', 'User')
    for user in User.objects.filter(groups__name='cine'):
        adress, created = Adress.objects.get_or_create(user=user)
        adress = 'Bag End, Bagshot Row, Hobbiton' if created else adress.adresse
        cinephile = Cinephile(user=user, adresse=adress)
        cinephile.save()
        for vote in user.vote_set.all():
            if not vote.film.vu:
                if vote.veto:
                    cinephile.vetos.add(vote.film)
                else:
                    cinephile.votes.add(vote.film)
        for dtw in user.dispotowatch_set.filter(dispo='O'):
            cinephile.soirees.add(dtw.soiree)
        cinephile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0014_cinephile'),
    ]

    operations = [
            migrations.RunPython(update_cinephile_data),
    ]