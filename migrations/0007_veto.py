# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0006_no_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='veto',
            field=models.BooleanField(default=False),
        ),
    ]
