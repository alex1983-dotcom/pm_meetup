from django.db import models
from django.utils.text import slugify

from mdeditor.fields import MDTextField

from apps.core.models import TimeStampedModel


class Material(TimeStampedModel):
    """Материал: отчёт, курс, чек-лист, запись, кейс."""
    CATEGORY_CHOICES = [
        ("report", "Отчёт"),
        ("course", "Курс"),
        ("checklist", "Чек-лист"),
        ("recording", "Запись"),
        ("case_study", "Кейс"),
    ]

    title = models.CharField("Название", max_length=300)
    category = models.CharField(
        "Категория", max_length=20, choices=CATEGORY_CHOICES, default="report"
    )
    description = models.TextField("Описание", blank=True)
    file_url = models.URLField("Ссылка на файл/страницу", blank=True)
    cover_image = models.ImageField(
        "Превью", upload_to="materials/", blank=True, null=True
    )
    view_count = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Partner(TimeStampedModel):
    """Партнёр сообщества."""
    LEVEL_CHOICES = [
        ("general", "Генеральный"),
        ("gold", "Золотой"),
        ("silver", "Серебряный"),
    ]

    name = models.CharField("Название компании", max_length=200)
    logo = models.ImageField("Логотип", upload_to="partners/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    website_url = models.URLField("Сайт", blank=True)
    partnership_level = models.CharField(
        "Уровень партнёрства",
        max_length=20,
        choices=LEVEL_CHOICES,
        default="general",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partners",
        verbose_name="Событие (null = глобальный)",
    )
    display_order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class TeamMember(TimeStampedModel):
    """Член команды сообщества."""
    full_name = models.CharField("ФИО", max_length=200)
    position = models.CharField("Должность", max_length=200, blank=True)
    photo = models.ImageField("Фотография", upload_to="team/", blank=True, null=True)
    bio = models.TextField("Биография", blank=True)
    email = models.EmailField("Email", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    twitter_url = models.URLField("Twitter", blank=True)
    display_order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Член команды"
        verbose_name_plural = "Команда"
        ordering = ["display_order", "full_name"]

    def __str__(self):
        return self.full_name


class SiteSettings(TimeStampedModel):
    """Настройки сайта (singleton)."""
    site_name = models.CharField("Название сайта", max_length=100, default="PM.Meetup")
    logo = models.ImageField("Логотип", upload_to="settings/", blank=True, null=True)
    favicon = models.ImageField("Иконка", upload_to="settings/", blank=True, null=True)
    email = models.EmailField("Email для контактов", blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    address = models.TextField("Адрес", blank=True)
    social_links = models.JSONField("Ссылки на соцсети", default=dict, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(TimeStampedModel):
    """Статичная страница (О нас, Контакты, Правила)."""
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL-путь", max_length=220, unique=True)
    content = MDTextField("Содержимое", blank=True)
    is_published = models.BooleanField("Опубликовано", default=False)
    meta_title = models.CharField("SEO: заголовок", max_length=200, blank=True)
    meta_description = models.CharField("SEO: описание", max_length=300, blank=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class PartnershipApplication(TimeStampedModel):
    """Заявка на партнёрство."""
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_review", "На рассмотрении"),
        ("accepted", "Принята"),
        ("rejected", "Отклонена"),
    ]

    company_name = models.CharField("Название компании", max_length=200)
    contact_name = models.CharField("Контактное лицо", max_length=200)
    contact_email = models.EmailField("Email")
    contact_phone = models.CharField("Телефон", max_length=30, blank=True)
    message = models.TextField("Сообщение", blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="new"
    )

    class Meta:
        verbose_name = "Заявка на партнёрство"
        verbose_name_plural = "Заявки на партнёрство"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company_name} ({self.status})"
