# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='soiree',
            name='time',
            field=models.TimeField(default=datetime.time(20, 30)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='soiree',
            name='date',
            field=models.DateField(),
            preserve_default=True,
        ),
    ]
