# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0005_auto_20150514_1638'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='film',
            name='categorie',
        ),
        migrations.RemoveField(
            model_name='soiree',
            name='categorie',
        ),
    ]
