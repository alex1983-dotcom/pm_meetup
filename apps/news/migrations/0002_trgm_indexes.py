from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_enable_pg_trgm"),
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="newsarticle",
            index=GinIndex(
                fields=["title"],
                name="news_article_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="newsarticle",
            index=GinIndex(
                fields=["short_description"],
                name="news_article_short_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="newsarticle",
            index=GinIndex(
                fields=["content"],
                name="news_article_content_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
