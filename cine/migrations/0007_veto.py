from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cine", "0006_no_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="vote",
            name="veto",
            field=models.BooleanField(default=False),
        ),
    ]
