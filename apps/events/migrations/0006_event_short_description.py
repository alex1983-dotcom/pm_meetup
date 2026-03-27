# Generated manually — поле краткого описания для превью в списках.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0005_alter_event_is_featured_recommended_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="short_description",
            field=models.CharField(
                blank=True,
                help_text="Текст для карточек и списков; полное описание ниже.",
                max_length=500,
                verbose_name="Краткое описание (превью)",
            ),
        ),
    ]
