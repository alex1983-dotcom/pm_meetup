from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from mdeditor.fields import MDTextField

from apps.core.models import TimeStampedModel, Tag


class EventCategory(TimeStampedModel):
    """Категория событий (тематика)."""
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL-путь", max_length=120, unique=True)
    description = models.TextField("Описание", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Категория событий"
        verbose_name_plural = "Категории событий"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Speaker(TimeStampedModel):
    """Спикер мероприятия."""
    full_name = models.CharField("ФИО", max_length=200)
    position = models.CharField("Должность", max_length=200, blank=True)
    company = models.CharField("Компания", max_length=200, blank=True)
    photo = models.ImageField("Фотография", upload_to="speakers/", blank=True, null=True)
    bio = models.TextField("Биография", blank=True)
    email = models.EmailField("Email", blank=True)
    social_links = models.JSONField("Ссылки на соцсети", default=dict, blank=True)
    topics = models.ManyToManyField(
        Tag, verbose_name="Темы выступлений", related_name="speakers", blank=True
    )

    class Meta:
        verbose_name = "Спикер"
        verbose_name_plural = "Спикеры"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Event(TimeStampedModel):
    """Событие (митап, воркшоп, конференция)."""
    FORMAT_CHOICES = [
        ("offline", "Офлайн"),
        ("online", "Онлайн"),
        ("hybrid", "Гибрид"),
    ]
    TYPE_CHOICES = [
        ("meetup", "Митап"),
        ("workshop", "Воркшоп"),
        ("conference", "Конференция"),
        ("networking", "Нетворкинг"),
    ]
    REGISTRATION_CHOICES = [
        ("open", "Открытая"),
        ("requires_approval", "Требует подтверждения"),
        ("closed", "Закрытая"),
    ]
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("registration_closed", "Регистрация закрыта"),
        ("completed", "Завершено"),
        ("cancelled", "Отменено"),
    ]

    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL-путь", max_length=220, unique=True)
    description = MDTextField("Описание", blank=True)
    date = models.DateField("Дата проведения")
    time_start = models.TimeField("Время начала")
    time_end = models.TimeField("Время окончания", null=True, blank=True)
    format = models.CharField(
        "Формат", max_length=20, choices=FORMAT_CHOICES, default="offline"
    )
    location_address = models.CharField("Адрес", max_length=300, blank=True)
    location_city = models.CharField("Город", max_length=100, blank=True)
    location_venue = models.CharField("Помещение/зал", max_length=200, blank=True)
    online_url = models.URLField("Ссылка на трансляцию", blank=True)
    online_platform = models.CharField("Платформа (Zoom и т.п.)", max_length=100, blank=True)
    event_type = models.CharField(
        "Тип события", max_length=20, choices=TYPE_CHOICES, default="meetup"
    )
    cover_image = models.ImageField(
        "Обложка", upload_to="events/", blank=True, null=True
    )
    capacity = models.PositiveIntegerField("Лимит участников", default=0)
    price = models.DecimalField(
        "Цена участия", max_digits=10, decimal_places=2, default=Decimal("0")
    )
    registration_type = models.CharField(
        "Тип регистрации",
        max_length=20,
        choices=REGISTRATION_CHOICES,
        default="open",
    )
    status = models.CharField(
        "Статус", max_length=30, choices=STATUS_CHOICES, default="draft"
    )
    cancellation_reason = models.TextField("Причина отмены", blank=True)
    meta_title = models.CharField("SEO: заголовок", max_length=200, blank=True)
    meta_description = models.CharField("SEO: описание", max_length=300, blank=True)
    is_featured = models.BooleanField("Показывать в «Ваш выбор»", default=False)

    categories = models.ManyToManyField(
        EventCategory, verbose_name="Категории", related_name="events", blank=True
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", related_name="events", blank=True
    )
    speakers = models.ManyToManyField(
        Speaker, verbose_name="Спикеры", related_name="events", blank=True
    )

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["-date", "-time_start"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class EventSegment(TimeStampedModel):
    """Сегмент программы мероприятия (доклад, кофе-брейк)."""
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="segments", verbose_name="Событие"
    )
    title = models.CharField("Название сегмента", max_length=200)
    description = models.TextField("Описание", blank=True)
    time_start = models.TimeField("Время начала")
    time_end = models.TimeField("Время окончания")
    order = models.PositiveIntegerField("Порядок", default=0)
    location = models.CharField("Место", max_length=200, blank=True)
    speakers = models.ManyToManyField(
        Speaker, verbose_name="Спикеры", related_name="event_segments", blank=True
    )

    class Meta:
        verbose_name = "Сегмент программы"
        verbose_name_plural = "Сегменты программы"
        ordering = ["event", "order", "time_start"]

    def __str__(self):
        return f"{self.event.title} — {self.title}"


class EventRegistration(TimeStampedModel):
    """Регистрация пользователя на событие."""
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("confirmed", "Подтверждена"),
        ("cancelled", "Отменена"),
    ]
    ATTENDANCE_CHOICES = [
        ("unknown", "Неизвестно"),
        ("attended", "Посетил"),
        ("no_show", "Не явился"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
        verbose_name="Участник",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Событие",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    attendance_status = models.CharField(
        "Посещение",
        max_length=20,
        choices=ATTENDANCE_CHOICES,
        default="unknown",
    )
    extra_data = models.JSONField("Доп. поля формы", default=dict, blank=True)

    class Meta:
        verbose_name = "Регистрация на событие"
        verbose_name_plural = "Регистрации на события"
        ordering = ["-created_at"]
        unique_together = [["user", "event"]]

    def __str__(self):
        return f"{self.user} — {self.event}"


class EventGallery(TimeStampedModel):
    """Галерея фотографий прошедшего события."""
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="galleries", verbose_name="Событие"
    )
    title = models.CharField("Название галереи", max_length=200)
    cover_image = models.ImageField(
        "Обложка", upload_to="galleries/", blank=True, null=True
    )
    photo_count = models.PositiveIntegerField("Кол-во фото", default=0)
    external_album_url = models.URLField("Ссылка на альбом (VK и т.п.)", blank=True)

    class Meta:
        verbose_name = "Галерея события"
        verbose_name_plural = "Галереи событий"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.title} — {self.title}"
