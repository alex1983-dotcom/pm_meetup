# Renamed verbose label to «Рекомендованное событие», default=False.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_alter_event_is_featured"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="is_featured",
            field=models.BooleanField(
                default=False,
                help_text="Показывать в блоке рекомендованных событий на сайте.",
                verbose_name="Рекомендованное событие",
            ),
        ),
    ]
