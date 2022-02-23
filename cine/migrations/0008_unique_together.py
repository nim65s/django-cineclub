from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cine", "0007_veto"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="dispotowatch",
            unique_together=set([("soiree", "cinephile")]),
        ),
    ]
