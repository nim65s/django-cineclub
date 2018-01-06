# Written by some kind of probably drunk guy, today, now.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0024_clean'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='soiree',
            options={'get_latest_by': 'moment', 'ordering': ['moment']},
        ),
        migrations.RemoveField(
            model_name='soiree',
            name='date',
        ),
        migrations.RemoveField(
            model_name='soiree',
            name='time',
        ),
        migrations.AddField(
            model_name='cinephile',
            name='pas_classes',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='soiree',
            name='hote',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
