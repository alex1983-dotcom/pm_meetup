# Кодовая база моделей PM.Meetup

Документ содержит код всех моделей проекта: заголовок — модель, ниже — код класса. Исходные файлы: `apps/users/models.py`, `apps/core/models.py`, `apps/events/models.py`, `apps/news/models.py`, `apps/content/models.py`.

---

## UserManager

Файл: `apps/users/models.py`

```python
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
```

---

## User

Файл: `apps/users/models.py`

```python
class User(AbstractUser):
    """Пользователь — участник сообщества PM.Meetup."""
    username = None  # Используем email для входа
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    avatar = models.ImageField("Фото профиля", upload_to="avatars/", blank=True, null=True)
    role = models.CharField(
        "Роль",
        max_length=30,
        choices=[
            ("member", "Участник"),
            ("organizer", "Организатор"),
            ("moderator", "Модератор"),
            ("admin", "Администратор"),
            ("superadmin", "Суперадминистратор"),
        ],
        default="member",
    )
    is_blocked = models.BooleanField("Заблокирован", default=False)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email or f"{self.first_name} {self.last_name}".strip() or str(self.pk)
```

---

## TimeStampedModel

Файл: `apps/core/models.py`. Абстрактная база: своей таблицы в БД нет, от неё наследуются остальные модели.

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

---

## ApiKey

Файл: `apps/core/models.py`

```python
class ApiKey(models.Model):
    name = models.CharField("Название ключа", max_length=120, unique=True)
    key = models.CharField("Токен", max_length=40, unique=True, editable=False)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "API-ключ"
        verbose_name_plural = "API-ключи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.key[:8]}...)"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_string(40)
        super().save(*args, **kwargs)
```

---

## Tag

Файл: `apps/core/models.py`

```python
class Tag(TimeStampedModel):
    """Общие теги для событий и новостей."""
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL-путь", max_length=120, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
```

---

## EventCategory

Файл: `apps/events/models.py`

```python
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
```

---

## Speaker

Файл: `apps/events/models.py`

```python
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
```

---

## Event

Файл: `apps/events/models.py`

```python
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
```

---

## EventSegment

Файл: `apps/events/models.py`

```python
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
```

---

## EventRegistration

Файл: `apps/events/models.py`

```python
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
```

---

## EventGallery

Файл: `apps/events/models.py`

```python
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
```

---

## NewsArticle

Файл: `apps/news/models.py`

```python
class NewsArticle(TimeStampedModel):
    """Новость / статья блога."""
    title = models.CharField("Заголовок", max_length=300)
    slug = models.SlugField("URL-путь", max_length=320, unique=True)
    short_description = models.TextField("Краткое описание (для карточки)", blank=True)
    content = MDTextField("Содержимое", blank=True)
    cover_image = models.ImageField(
        "Обложка", upload_to="news/", blank=True, null=True
    )
    publication_date = models.DateTimeField("Дата публикации", null=True, blank=True)
    read_time_minutes = models.PositiveIntegerField("Время чтения (мин)", default=0)
    views_count = models.PositiveIntegerField("Просмотры", default=0)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news_articles",
        verbose_name="Автор",
    )
    is_published = models.BooleanField("Опубликовано", default=False)
    meta_title = models.CharField("SEO: заголовок", max_length=200, blank=True)
    meta_description = models.CharField("SEO: описание", max_length=300, blank=True)
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", related_name="news_articles", blank=True
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-publication_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
```

---

## Material

Файл: `apps/content/models.py`

```python
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
```

---

## Partner

Файл: `apps/content/models.py`

```python
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
```

---

## TeamMember

Файл: `apps/content/models.py`

```python
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
```

---

## SiteSettings

Файл: `apps/content/models.py`

```python
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
```

---

## Page

Файл: `apps/content/models.py`

```python
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
```

---

## PartnershipApplication

Файл: `apps/content/models.py`

```python
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
```
