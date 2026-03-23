from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_enable_pg_trgm"),
        ("materials", "0002_material_date_material_duration_minutes_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="material",
            index=GinIndex(
                fields=["title"],
                name="materials_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="material",
            index=GinIndex(
                fields=["label"],
                name="materials_label_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="material",
            index=GinIndex(
                fields=["description"],
                name="materials_desc_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="material",
            index=GinIndex(
                fields=["place"],
                name="materials_place_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="materialcategory",
            index=GinIndex(
                fields=["title"],
                name="materials_cat_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
