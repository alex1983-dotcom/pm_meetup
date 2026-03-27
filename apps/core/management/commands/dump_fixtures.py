"""
Создаёт один общий файл фикстур fixtures/initial_data.json для фронта.
Бэкенд: создаёт дамп с нужными данными. Фронт: разворачивает у себя через loaddata initial_data.

Через Docker:
  docker compose exec web python manage.py dump_fixtures --seed   # загрузить seed + экспорт в initial_data.json
  docker compose exec web python manage.py loaddata initial_data  # развернуть (на стороне фронта)
"""
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Экспорт данных в один файл fixtures/initial_data.json (для развёртывания на фронте)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Сначала загрузить тестовые данные (seed_data --clear), затем экспорт.",
        )

    def handle(self, *args, **options):
        fixture_dir = Path(settings.BASE_DIR) / "fixtures"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        out_path = fixture_dir / "initial_data.json"

        if options["seed"]:
            self.stdout.write("Загрузка тестовых данных (seed_data --clear)...")
            call_command("seed_data", "--clear", verbosity=1)

        self.stdout.write(f"Экспорт в {out_path}...")
        with open(out_path, "w", encoding="utf-8") as f:
            call_command(
                "dumpdata",
                "core.Tag",
                "core.ApiKey",
                "users.User",
                "events.Speaker",
                "events.Event",
                "events.EventSegment",
                "events.EventRegistration",
                "events.EventGallery",
                "news.NewsArticle",
                "content.Partner",
                "content.TeamMember",
                "content.SiteSettings",
                "content.Page",
                "content.PartnershipApplication",
                "pages.Page",
                "pages.BlockType",
                "pages.PageBlock",
                "pages.BlockItem",
                "materials.MaterialCategory",
                "materials.Material",
                indent=2,
                stdout=f,
            )
        self.stdout.write(self.style.SUCCESS(f"Готово: {out_path}"))
        self.stdout.write("Фронт разворачивает: docker compose exec web python manage.py loaddata initial_data")
