# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-02 22:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0018_cinephile_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cinephile',
            options={'ordering': ['user']},
        ),
    ]
