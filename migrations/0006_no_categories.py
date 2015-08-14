from django.db import migrations, models


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
