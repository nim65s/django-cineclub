from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cine", "0003_auto_20150112_0554"),
    ]

    operations = [
        migrations.CreateModel(
            name="Adress",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("adresse", models.TextField()),
                (
                    "user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
