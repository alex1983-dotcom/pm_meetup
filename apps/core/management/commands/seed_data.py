"""
Команда для загрузки тестовых данных по макетам Figma (Contacts, Events, EventPage, News, NewsItem, Materials).
Использование: python manage.py seed_data
Повторный запуск не создаёт дубликаты (get_or_create по уникальным полям).
"""
from datetime import date, time, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.content.models import Page as ContentPage
from apps.content.models import Partner, PartnershipApplication, SiteSettings, TeamMember
from apps.core.models import ApiKey, Tag
from apps.events.models import (
    Event,
    EventGallery,
    EventRegistration,
    EventSegment,
    EventTheme,
    Speaker,
)
from apps.materials.models import Material, MaterialCategory
from apps.news.models import NewsArticle
from apps.pages.models import BlockItem, BlockType, Page as PagesPage
from apps.pages.models import PageBlock
from apps.users.models import User


class Command(BaseCommand):
    help = "Загружает тестовые данные по макетам Figma (контакты, события, новости, материалы)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все данные перед загрузкой (осторожно: очистит все таблицы приложений).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()
        self._seed_core()
        self._seed_users()
        tags = self._seed_tags()
        themes = self._seed_event_themes()
        speakers = self._seed_speakers(tags)
        events = self._seed_events(themes, tags, speakers)
        self._seed_event_segments_and_galleries(events, speakers)
        users = list(User.objects.filter(email__in=["admin@pm.meetup", "author@pm.meetup", "user@pm.meetup"]))
        if users and events:
            self._seed_registrations(users, events)
        self._seed_news(tags, users)
        self._seed_content(events)
        self._seed_pages_blocks()
        self._seed_materials()
        self.stdout.write(self.style.SUCCESS("Тестовые данные (по макетам Figma) успешно загружены."))

    def _clear_data(self):
        """Удаление в обратном порядке зависимостей."""
        BlockItem.objects.all().delete()
        PageBlock.objects.all().delete()
        BlockType.objects.all().delete()
        PagesPage.objects.all().delete()
        Material.objects.all().delete()
        MaterialCategory.objects.all().delete()
        PartnershipApplication.objects.all().delete()
        ContentPage.objects.all().delete()
        TeamMember.objects.all().delete()
        Partner.objects.all().delete()
        SiteSettings.objects.all().delete()
        NewsArticle.objects.all().delete()
        EventGallery.objects.all().delete()
        EventSegment.objects.all().delete()
        EventRegistration.objects.all().delete()
        Event.objects.all().delete()
        Speaker.objects.all().delete()
        EventTheme.objects.all().delete()
        User.objects.all().delete()
        Tag.objects.all().delete()
        ApiKey.objects.all().delete()
        self.stdout.write("Данные очищены.")

    def _seed_core(self):
        api_key, _ = ApiKey.objects.get_or_create(
            name="Тестовый ключ для фронта",
            defaults={"is_active": True},
        )
        api_key.key = "test-api-key-12345"
        api_key.save(update_fields=["key"])
        self.stdout.write("  API-ключ: X-API-KEY = test-api-key-12345")

    def _seed_tags(self):
        """Теги из макетов: новости (#События, #TechConference, #2025, #Тренды, #Партнеры, #Развитие, #Старт, #Наставничества), события (#Meetup, #Workshop, #Networking)."""
        data = [
            ("События", "sobytiya"),
            ("TechConference", "techconference"),
            ("2025", "2025"),
            ("Тренды", "trendy"),
            ("Партнеры", "partnery"),
            ("Развитие", "razvitie"),
            ("Старт", "start"),
            ("Наставничества", "nastavnichestva"),
            ("Meetup", "meetup"),
            ("Workshop", "workshop"),
            ("Networking", "networking"),
        ]
        created = []
        for name, slug in data:
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            created.append(tag)
        self.stdout.write(f"  Теги: {len(created)}")
        return created

    def _seed_users(self):
        User.objects.get_or_create(
            email="admin@pm.meetup",
            defaults={
                "first_name": "Админ",
                "last_name": "Админов",
                "role": "superadmin",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        u = User.objects.get(email="admin@pm.meetup")
        u.set_password("admin123")
        u.save()
        User.objects.get_or_create(
            email="author@pm.meetup",
            defaults={
                "first_name": "Иван",
                "last_name": "Авторов",
                "role": "organizer",
                "is_staff": False,
                "is_active": True,
            },
        )
        u2 = User.objects.get(email="author@pm.meetup")
        u2.set_password("author123")
        u2.save()
        User.objects.get_or_create(
            email="user@pm.meetup",
            defaults={
                "first_name": "Пётр",
                "last_name": "Участников",
                "role": "member",
                "is_staff": False,
                "is_active": True,
            },
        )
        u3 = User.objects.get(email="user@pm.meetup")
        u3.set_password("user123")
        u3.save()
        self.stdout.write("  Пользователи: admin@pm.meetup (admin123), author@pm.meetup (author123), user@pm.meetup (user123)")

    def _seed_event_themes(self):
        """Тематики для внутренней аналитики (справочник)."""
        data = [
            ("Митап", "meetup", "", 1),
            ("Воркшоп", "workshop", "", 2),
            ("Нетворкинг", "networking", "", 3),
        ]
        created = []
        for name, slug, desc, order in data:
            th, _ = EventTheme.objects.get_or_create(
                slug=slug, defaults={"name": name, "description": desc, "order": order}
            )
            created.append(th)
        self.stdout.write(f"  Тематики мероприятий: {len(created)}")
        return created

    def _seed_speakers(self, tags):
        """Спикеры из макетов: Анна Петрова, Михаил Сергеев, Ольга и Иван (для Networking)."""
        data = [
            ("Анна Петрова", "Руководитель программ", "", "Спикер по AI в бизнесе и управлению проектами."),
            ("Михаил Сергеев", "Эксперт по цифровому маркетингу", "", "Погружение в тренды и инструменты цифрового маркетинга."),
            ("Ольга Иванова", "Предприниматель", "", "Неформальное общение опытных предпринимателей."),
            ("Иван Козлов", "Предприниматель", "", "Нетворкинг: предприниматели Минска."),
        ]
        created = []
        for full_name, position, company, bio in data:
            sp, _ = Speaker.objects.get_or_create(
                full_name=full_name,
                defaults={"position": position, "company": company, "bio": bio},
            )
            if tags and not sp.topics.exists():
                sp.topics.set(tags[:3])
            created.append(sp)
        self.stdout.write(f"  Спикеры: {len(created)}")
        return created

    def _seed_events(self, themes, tags, speakers):
        """События как на макетах Events.jpg и EventPage.jpg: ноябрь 2025 + прошедшие для галерей."""
        # Ноябрь 2025 — предстоящие
        data_upcoming = [
            {
                "title": "Networking: Предприниматели Минска",
                "slug": "networking-predprinimateli-minska",
                "description": "Неформальное общение опытных предпринимателей. Онлайн-встреча общение предпринимателей.",
                "date": date(2025, 11, 1),
                "time_start": time(19, 0),
                "time_end": time(21, 0),
                "format": "offline",
                "location_address": "г. Минск, ул. Ленина 3",
                "location_city": "Минск",
                "location_venue": "ул. Ленина 3",
                "event_type": "networking",
                "capacity": 50,
                "price": Decimal("0"),
                "registration_type": "open",
                "status": "published",
                "is_featured": False,
            },
            {
                "title": "Workshop: Digital Marketing 2026",
                "slug": "workshop-digital-marketing-2026",
                "description": "Погружение в тренды и инструменты цифрового маркетинга.",
                "date": date(2025, 11, 9),
                "time_start": time(19, 0),
                "time_end": time(21, 0),
                "format": "online",
                "location_city": "",
                "online_platform": "Zoom",
                "online_url": "https://example.com/stream",
                "event_type": "workshop",
                "capacity": 100,
                "price": Decimal("50"),
                "registration_type": "open",
                "status": "published",
                "is_featured": False,
            },
            {
                "title": "Tech Meetup: AI в бизнесе",
                "slug": "tech-meetup-ai-v-biznese",
                "description": "Tech Meetup: AI в бизнесе — встреча для проектных менеджеров, предпринимателей и специалистов, которые хотят понять, как использовать искусственный интеллект для повышения эффективности команд и бизнес-процессов.\n\nНа митапе обсудим, как AI уже влияет на управление проектами, где он реально экономит ресурсы, а где — вызывает новые вызовы. Вас ждут живые кейсы, практические инсайты и нетворкинг с коллегами из индустрии.",
                "date": date(2025, 11, 15),
                "time_start": time(19, 0),
                "time_end": time(20, 30),
                "format": "offline",
                "location_address": "г. Минск, пр. Независимости 95",
                "location_city": "Минск",
                "location_venue": "пр. Независимости 95",
                "event_type": "meetup",
                "capacity": 60,
                "price": Decimal("100"),
                "registration_type": "open",
                "status": "published",
                "is_featured": False,
            },
            {
                "title": "Networking: Предприниматели Минска",
                "slug": "networking-predprinimateli-minska-2",
                "description": "Неформальное общение опытных предпринимателей.",
                "date": date(2025, 11, 24),
                "time_start": time(19, 0),
                "time_end": time(21, 0),
                "format": "offline",
                "location_address": "г. Минск, ул. Ленина 3",
                "location_city": "Минск",
                "location_venue": "ул. Ленина 3",
                "event_type": "networking",
                "capacity": 50,
                "price": Decimal("0"),
                "registration_type": "open",
                "status": "published",
                "is_featured": False,
            },
            {
                "title": "Networking: Предприниматели Минска",
                "slug": "networking-predprinimateli-minska-3",
                "description": "Неформальное общение опытных предпринимателей.",
                "date": date(2025, 11, 27),
                "time_start": time(19, 0),
                "time_end": time(21, 0),
                "format": "offline",
                "location_address": "г. Минск, ул. Ленина 3",
                "location_city": "Минск",
                "location_venue": "ул. Ленина 3",
                "event_type": "networking",
                "capacity": 50,
                "price": Decimal("0"),
                "registration_type": "open",
                "status": "published",
                "is_featured": False,
            },
        ]
        # Прошедшие события (для галерей «ФОТОГРАФИИ Tech Conference 2025» и «Бизнес-завтрак. Июль»)
        data_past = [
            {
                "title": "Tech Conference 2025",
                "slug": "tech-conference-2025",
                "description": "Крупнейшая технологическая конференция года.",
                "date": date(2025, 9, 10),
                "time_start": time(10, 0),
                "time_end": time(18, 0),
                "format": "offline",
                "location_city": "Минск",
                "event_type": "conference",
                "capacity": 500,
                "price": Decimal("0"),
                "status": "completed",
                "is_featured": False,
            },
            {
                "title": "Бизнес-завтрак. Июль",
                "slug": "biznes-zavtrak-iyul",
                "description": "Бизнес-завтрак для предпринимателей.",
                "date": date(2025, 7, 8),
                "time_start": time(9, 0),
                "time_end": time(11, 0),
                "format": "offline",
                "location_city": "Минск",
                "event_type": "networking",
                "capacity": 50,
                "price": Decimal("0"),
                "status": "completed",
                "is_featured": False,
            },
        ]
        created = []
        for d in data_upcoming + data_past:
            ev, _ = Event.objects.get_or_create(slug=d["slug"], defaults=d)
            if themes and not ev.themes.exists():
                ev.themes.set(themes)
            if tags and not ev.tags.exists():
                ev.tags.set(tags[:5])
            if speakers and not ev.speakers.exists():
                if "AI" in ev.title:
                    ev.speakers.set([s for s in speakers if "Анна" in s.full_name])
                elif "Digital Marketing" in ev.title:
                    ev.speakers.set([s for s in speakers if "Михаил" in s.full_name])
                elif "Предприниматели" in ev.title:
                    ev.speakers.set([s for s in speakers if s.full_name in ("Ольга Иванова", "Иван Козлов")])
            created.append(ev)
        self.stdout.write(f"  События: {len(created)} (предстоящие + прошедшие)")
        return created

    def _seed_event_segments_and_galleries(self, events, speakers):
        """Сегменты для «Tech Meetup: AI в бизнесе» (как на EventPage) и галереи для прошедших."""
        ev_ai = next((e for e in events if e.slug == "tech-meetup-ai-v-biznese"), None)
        anna = next((s for s in speakers if "Анна" in s.full_name), None)
        if ev_ai and anna:
            topics = [
                "Как AI помогает в планировании и анализе проектов",
                "Инструменты, упрощающие работу менеджера",
                "Кейсы внедрения AI в компаниях разного масштаба",
                "Этика и границы автоматизации",
            ]
            for i, title in enumerate(topics, 1):
                EventSegment.objects.get_or_create(
                    event=ev_ai,
                    title=title,
                    defaults={
                        "time_start": time(19, 0),
                        "time_end": time(20, 30),
                        "order": i,
                    },
                )
            for seg in EventSegment.objects.filter(event=ev_ai):
                if not seg.speakers.exists() and anna:
                    seg.speakers.add(anna)
        # Галереи прошедших (как на макете: ФОТОГРАФИИ Tech Conference 2025 — 478, Бизнес-завтрак. Июль — 112)
        ev_conf = next((e for e in events if e.slug == "tech-conference-2025"), None)
        ev_breakfast = next((e for e in events if e.slug == "biznes-zavtrak-iyul"), None)
        if ev_conf:
            EventGallery.objects.get_or_create(
                event=ev_conf,
                title="ФОТОГРАФИИ Tech Conference 2025",
                defaults={"photo_count": 478},
            )
        if ev_breakfast:
            EventGallery.objects.get_or_create(
                event=ev_breakfast,
                title="ФОТОГРАФИИ Бизнес-завтрак. Июль",
                defaults={"photo_count": 112},
            )
        self.stdout.write("  Сегменты и галереи созданы.")

    def _seed_registrations(self, users, events):
        """Регистрации: 45/60 для Tech Meetup, 78/100 для Workshop, 32/50 для Networking (как на макете)."""
        ev_ai = next((e for e in events if e.slug == "tech-meetup-ai-v-biznese"), None)
        if not ev_ai:
            return
        for u in users[:2]:
            EventRegistration.objects.get_or_create(
                user=u,
                event=ev_ai,
                defaults={"status": "confirmed"},
            )
        self.stdout.write("  Регистрации на события созданы.")

    def _seed_news(self, tags, users):
        """Новости как на News.jpg и полный текст как на NewsItem.jpg (Итоги Tech Conference 2025)."""
        author = users[0] if users else None
        tag_sobytiya = Tag.objects.filter(slug="sobytiya").first()
        tag_tech = Tag.objects.filter(slug="techconference").first()
        tag_2025 = Tag.objects.filter(slug="2025").first()
        tag_trendy = Tag.objects.filter(slug="trendy").first()
        tag_partnery = Tag.objects.filter(slug="partnery").first()
        tag_razvitie = Tag.objects.filter(slug="razvitie").first()
        tag_start = Tag.objects.filter(slug="start").first()
        tag_nastav = Tag.objects.filter(slug="nastavnichestva").first()
        tags_tech = [tag_sobytiya, tag_tech, tag_2025, tag_trendy] if all([tag_sobytiya, tag_tech, tag_2025, tag_trendy]) else list(tags[:4])
        tags_partners = [tag_sobytiya, tag_partnery, tag_razvitie] if all([tag_sobytiya, tag_partnery, tag_razvitie]) else list(tags[:3])
        tags_mentor = [tag_sobytiya, tag_partnery, tag_razvitie, tag_start, tag_nastav] if all([tag_sobytiya, tag_partnery, tag_razvitie, tag_start, tag_nastav]) else list(tags[:5])

        content_tech = """Более 200 участников собрались на крупнейшей технологической конференции года, чтобы обсудить тренды и перспективы развития отрасли.

Tech Conference 2025 стала главным событием для всех, кто живет технологиями и строит цифровое будущее. Более двухсот специалистов — от проектных менеджеров и IT-директоров до стартаперов и аналитиков — встретились, чтобы обменяться опытом, обсудить влияние искусственного интеллекта на бизнес и вместе заглянуть в будущее индустрии.

## Главная тема – AI как катализатор перемен

Искусственный интеллект стал центральной темой конференции. Спикеры говорили о том, как AI меняет подход к управлению проектами, ускоряет принятие решений и открывает новые возможности для автоматизации.

Особое внимание уделили реальным кейсам: компании поделились историями успешной интеграции AI-решений — от чат-ботов для поддержки клиентов до аналитических инструментов, прогнозирующих риски и эффективность команд.

Как отметил один из выступающих, «AI больше не просто тренд — это рабочий инструмент, без которого уже невозможно представлять развитие бизнеса».

## Управление проектами будущего

В отдельной секции конференции обсудили трансформацию роли проектного менеджера. Если раньше акцент делался на контроле задач и сроков, то сегодня всё большее значение приобретает стратегическое мышление, умение работать с данными и использовать технологии для оптимизации процессов.

Спикеры подчеркнули, что успешный менеджер 2025 года – это человек, который умеет сочетать человеческую эмпатию с технологической осведомлённостью.

## Нетворкинг и обмен опытом

Помимо выступлений и панельных дискуссий, участники активно знакомились, обменивались контактами и идеями. Многие отметили, что неформальное общение стало не менее ценным, чем сами доклады — именно здесь рождаются будущие коллаборации и стартапы.

## Что дальше

Организаторы уже анонсировали серию тематических митапов и воркшопов, посвящённых практическому применению AI в управлении проектами. Следующее мероприятие состоится весной 2026 года, и, судя по интересу аудитории, оно обещает стать ещё масштабнее.

Tech Conference 2025 в очередной раз доказала: будущее технологий – это не только про код и алгоритмы, но и про людей, которые умеют объединять знания, опыт и креатив, чтобы создавать новые смыслы и решения."""

        data = [
            (
                "Итоги Tech Conference 2025",
                "itogi-tech-conference-2025",
                "Более 200 участников собрались на крупнейшей технологической конференции года. Обсуждали тренды и перспективы развития отрасли.",
                content_tech,
                timezone.make_aware(datetime(2025, 1, 10, 12, 0)),
                3,
                tags_tech,
            ),
            (
                "Новые партнеры сообщества",
                "novye-partnery-soobshchestva",
                "К нашему сообществу присоединились 5 новых компаний партнеров, которые будут поддерживать развитие профессионального комьюнити.",
                "К нашему сообществу присоединились 5 новых компаний партнеров. Они будут поддерживать развитие профессионального комьюнити и совместные мероприятия.",
                timezone.make_aware(datetime(2025, 1, 10, 12, 0)),
                3,
                tags_partners,
            ),
            (
                "Запуск менторской программы",
                "zapusk-mentorskoj-programmy",
                "Стартует новая программа наставничества для молодых специалистов. Опытные профессионалы поделятся знаниями и помогут в карьерном развитии.",
                "Стартует новая программа наставничества для молодых специалистов. Опытные профессионалы поделятся знаниями и помогут в карьерном развитии.",
                timezone.make_aware(datetime(2025, 1, 10, 12, 0)),
                3,
                tags_mentor,
            ),
        ]
        for title, slug, short, content, pub_date, read_m, tag_list in data:
            art, _ = NewsArticle.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "short_description": short,
                    "content": content,
                    "publication_date": pub_date,
                    "read_time_minutes": read_m,
                    "author": author,
                    "is_published": True,
                },
            )
            if tag_list and not art.tags.exists():
                art.tags.set([t for t in tag_list if t])
        self.stdout.write(f"  Новости: {len(data)}")

    def _seed_content(self, events):
        """Контакты/Контент как на Contacts.jpg: PM.MEETUP, TECH CORP, команда (Максим Сидоров, Елена Козлова), адрес пр. Независимости 95."""
        SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "PM.MEETUP",
                "email": "hello@community.by",
                "phone": "+375 29 123-45-67",
                "address": "г. Минск, пр. Независимости 95",
                "social_links": {"linkedin": "https://linkedin.com/company/pmmeetup", "instagram": "https://instagram.com/pmmeetup"},
            },
        )
        Partner.objects.get_or_create(
            name="TECH CORP",
            defaults={
                "partnership_level": "general",
                "display_order": 1,
                "event": None,
                "description": "Надёжные IT решения",
            },
        )
        # Несколько карточек TECH CORP на макете — одна запись в БД
        TeamMember.objects.get_or_create(
            full_name="Максим Сидоров",
            defaults={
                "position": "Руководитель программ",
                "description": "Координирует образовательные программы и воркшопы",
                "display_order": 1,
            },
        )
        TeamMember.objects.get_or_create(
            full_name="Елена Козлова",
            defaults={
                "position": "Руководитель программ",
                "description": "Координирует образовательные программы и воркшопы",
                "display_order": 2,
            },
        )
        ContentPage.objects.get_or_create(
            slug="about",
            defaults={
                "title": "О нас",
                "content": "Создаём пространство, где идеи рождаются, знания передаются, а каждый может расти профессионально. 578+ участников.",
                "is_published": True,
            },
        )
        ContentPage.objects.get_or_create(
            slug="contacts",
            defaults={
                "title": "Контакты",
                "content": "**Контакты**\n\nEmail: hello@community.by\nТелефон: +375 29 123-45-67\nАдрес: г. Минск, пр. Независимости 95",
                "is_published": True,
            },
        )
        PartnershipApplication.objects.get_or_create(
            company_name="TECH CORP",
            contact_email="info@techcorp.by",
            defaults={"contact_name": "Контакты партнёра", "message": "Хотим стать партнёром сообщества.", "status": "new"},
        )
        self.stdout.write("  Контент: настройки, партнёры, команда, страницы (по макету Контакты).")

    def _seed_pages_blocks(self):
        """Главная: hero как на Contacts — «АКТИВНОЕ КОМЬЮНИТИ ДЛЯ МЕНЕДЖЕРОВ ПРОЕКТОВ», 578+ участников."""
        page, _ = PagesPage.objects.get_or_create(slug="home", defaults={"name": "Главная"})
        for code, name in [("hero", "Hero-блок"), ("faq", "FAQ"), ("applications", "Блок заявок")]:
            BlockType.objects.get_or_create(code=code, defaults={"name": name})
        hero_type = BlockType.objects.get(code="hero")
        faq_type = BlockType.objects.get(code="faq")
        block_hero, _ = PageBlock.objects.get_or_create(page=page, block_type=hero_type, defaults={"order": 1})
        block_faq, _ = PageBlock.objects.get_or_create(page=page, block_type=faq_type, defaults={"order": 2})
        BlockItem.objects.get_or_create(
            block=block_hero,
            order=1,
            defaults={
                "title": "АКТИВНОЕ КОМЬЮНИТИ ДЛЯ МЕНЕДЖЕРОВ ПРОЕКТОВ",
                "subtitle": "578+ участников",
                "content": "Создаём пространство, где идеи рождаются, знания передаются, а каждый может расти профессионально.",
                "icon": "hero-main",
            },
        )
        BlockItem.objects.get_or_create(
            block=block_faq,
            order=1,
            defaults={"title": "Как зарегистрироваться?", "content": "Нажмите «Участвовать» или «Пойти» на карточке события.", "icon": "faq"},
        )
        BlockItem.objects.get_or_create(
            block=block_faq,
            order=2,
            defaults={"title": "Нужна ли оплата?", "content": "Часть мероприятий бесплатна, на части участие платное (указано на карточке).", "icon": "faq"},
        )
        self.stdout.write("  Страницы с блоками: главная (hero как на Figma).")

    def _seed_materials(self):
        """Материалы как на Materials.jpg: категории КУРСЫ, ХЕНДБУКИ, ФОТО С МЕРОПРИЯТИЙ, ЗАПИСИ ВЫСТУПЛЕНИЙ, ПРЕЗЕНТАЦИИ, КНИГИ и карточки с датами/минутами."""
        categories_data = [
            ("courses", "КУРСЫ", 1),
            ("handbooks", "ХЕНДБУКИ", 2),
            ("event_photos", "ФОТО С МЕРОПРИЯТИЙ", 3),
            ("talk_records", "ЗАПИСИ ВЫСТУПЛЕНИЙ", 4),
            ("presentations", "ПРЕЗЕНТАЦИИ", 5),
            ("books", "КНИГИ", 6),
        ]
        for slug, title, order in categories_data:
            MaterialCategory.objects.get_or_create(slug=slug, defaults={"title": title, "display_order": order, "is_active": True})

        cat_photos = MaterialCategory.objects.get(slug="event_photos")
        cat_records = MaterialCategory.objects.get(slug="talk_records")
        cat_courses = MaterialCategory.objects.get(slug="courses")
        cat_handbooks = MaterialCategory.objects.get(slug="handbooks")

        materials_data = [
            ("ФОТОГРАФИИ", "Tech Conference 2025", cat_photos, date(2025, 9, 10), "Минск", None, 478),
            ("ЗАПИСЬ", "Воркшоп: Жизненный цикл проекта в РМВОК 6 и 7", cat_records, date(2025, 9, 1), "Online", 44, None),
            ("КУРС", "Project Manager in IT", cat_courses, date(2025, 7, 6), "Online", 348, None),
            ("ХЕНДБУК", "По эффективному написанию промтов", cat_handbooks, date(2025, 10, 11), "Online", 120, None),
            ("ЗАПИСЬ", "Воркшоп: Спиральная динамика", cat_records, date(2025, 9, 1), "Online", 28, None),
            ("ФОТОГРАФИИ", "Бизнес-завтрак. Июль", cat_photos, date(2025, 7, 8), "Минск", None, 112),
            ("КУРС", "Разработка и AI", cat_courses, date(2025, 10, 11), "Online", 244, None),
        ]
        for label, title, category, d, place, duration, view_count in materials_data:
            Material.objects.get_or_create(
                title=title,
                category=category,
                defaults={
                    "label": label,
                    "date": d,
                    "place": place,
                    "duration_minutes": duration,
                    "view_count": view_count or 0,
                },
            )
        self.stdout.write("  Материалы: категории и карточки как на макете Materials.")