from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0008_alter_event_price_optional_free_default"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="themes",
        ),
        migrations.DeleteModel(
            name="EventTheme",
        ),
    ]
