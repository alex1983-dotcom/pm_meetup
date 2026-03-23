from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_enable_pg_trgm"),
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="event",
            index=GinIndex(
                fields=["title"],
                name="events_event_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=GinIndex(
                fields=["description"],
                name="events_event_desc_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=GinIndex(
                fields=["location_city"],
                name="events_event_city_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=GinIndex(
                fields=["location_venue"],
                name="events_event_venue_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="speaker",
            index=GinIndex(
                fields=["full_name"],
                name="events_speaker_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
