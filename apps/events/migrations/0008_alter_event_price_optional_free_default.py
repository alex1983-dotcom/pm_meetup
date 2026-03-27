from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0007_rename_event_category_to_theme"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=None,
                help_text="Если не указано — участие бесплатное.",
                max_digits=10,
                null=True,
                verbose_name="Цена участия",
            ),
        ),
    ]
