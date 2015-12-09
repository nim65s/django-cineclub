# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0008_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adress',
            options={'verbose_name_plural': 'Adresses'},
        ),
    ]
