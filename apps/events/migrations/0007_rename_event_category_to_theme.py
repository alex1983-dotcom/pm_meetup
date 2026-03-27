# Generated manually for EventTheme / themes (analytics)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0006_event_short_description"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EventCategory",
            new_name="EventTheme",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="categories",
            new_name="themes",
        ),
        migrations.AlterModelOptions(
            name="eventtheme",
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Тематика мероприятия",
                "verbose_name_plural": "Тематики мероприятий",
            },
        ),
        migrations.AlterField(
            model_name="eventtheme",
            name="description",
            field=models.TextField(blank=True, verbose_name="Заметки"),
        ),
        migrations.AlterField(
            model_name="event",
            name="themes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Для внутренних отчётов и раздела аналитики; не дублирует теги для витрины.",
                related_name="events",
                to="events.eventtheme",
                verbose_name="Тематики (аналитика)",
            ),
        ),
    ]
