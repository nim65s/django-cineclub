import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0002_auto_20150109_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soiree',
            name='time',
            field=models.TimeField(default=datetime.time(20, 30), verbose_name='heure'),
            preserve_default=True,
        ),
    ]
