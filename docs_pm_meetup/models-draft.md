# Набросок моделей PM.Meetup

Документ приведён в соответствие с кодом в `apps/*/models.py` (актуально на момент правки). Ниже — доменные модели и служебные сущности ядра.

**Общее:** модели `Event`, `Speaker`, `EventSegment`, `EventRegistration`, `EventGallery`, `NewsArticle`, `Partner`, `TeamMember`, `SiteSettings`, `content.Page`, `PartnershipApplication`, `Material`, `MaterialCategory`, `BlockItem` наследуют **`TimeStampedModel`** (`created_at`, `updated_at`) из `apps.core.models`. **`Tag`** тоже наследует `TimeStampedModel`. **`ApiKey`** — отдельная модель без таймстампов обновления (только `created_at`). **`pages.Page`**, **`BlockType`**, **`PageBlock`** — без `TimeStampedModel` (у `PageBlock` нет своих `created_at`/`updated_at` в модели).

---

## 0. API-ключи (`core.ApiKey`)

Используются для доступа к API (не путать с сессией пользователя).

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(120), unique | Название ключа |
| key | CharField(40), unique, editable=False | Токен (генерируется при сохранении, если пусто) |
| is_active | BooleanField, default=True | Активен ли ключ |
| created_at | DateTimeField, auto_now_add | Создан |

**Связи:** нет FK на `User` / `Event`.

---

## 1. Пользователи (`users.User`)

Кастомная модель: **`AbstractUser`**, поле **`username = None`**, вход по **`email`** (`USERNAME_FIELD = "email"`). Унаследованы поля Django: в т.ч. `first_name`, `last_name`, `is_staff`, `is_active`, `is_superuser`, `date_joined`, `last_login`, `password` и т.д.

| Поле | Тип | Описание |
|------|-----|----------|
| email | EmailField, unique | Email — вход вместо username |
| first_name | CharField(150), blank | Из `AbstractUser` |
| last_name | CharField(150), blank | Из `AbstractUser` |
| phone | CharField(20), blank | Телефон |
| avatar | ImageField, blank, null, upload_to=avatars/ | Фото профиля |
| role | CharField(30), choices, default=member | member / organizer / moderator / admin / superadmin |
| is_blocked | BooleanField, default=False | Блокировка учётной записи |
| created_at | DateTimeField, auto_now_add | Дата регистрации (доп. поле проекта) |
| **event_registrations** | **обратная FK (`EventRegistration.user`)** | **related_name='event_registrations', CASCADE** |
| **news_articles** | **обратная FK (`NewsArticle.author`)** | **related_name='news_articles', SET_NULL** |

---

## 2. События (`events.Event`)

**Связи:**
- **Обратные FK:** `EventSegment` (`event.segments`), `EventRegistration` (`event.registrations`), `Partner` (`event.partners`, null=True), `EventGallery` (`event.galleries`).
- **ManyToMany:** `Tag` (`event.tags` ↔ `tag.events`), `Speaker` (`event.speakers` ↔ `speaker.events`).

Отдельной модели категорий/тем события в текущем коде **нет** (исторически были категории/темы — сняты миграциями).

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(200) | Название |
| slug | SlugField(220), unique | URL-путь (автозаполнение из title при сохранении, если пусто) |
| short_description | CharField(500), blank | Краткое описание для карточек |
| description | MDTextField, blank | Описание (markdown) |
| date | DateField | Дата проведения |
| time_start | TimeField | Время начала |
| time_end | TimeField, null, blank | Время окончания |
| format | CharField(20), choices, default=offline | offline / online |
| location_address | CharField(300), blank | Адрес |
| location_city | CharField(100), blank | Город |
| location_venue | CharField(200), blank | Помещение / зал |
| online_url | URLField, blank | Ссылка на трансляцию |
| online_platform | CharField(100), blank | Платформа |
| event_type | CharField(20), choices, default=meetup | meetup / workshop / conference / networking |
| cover_image | ImageField, blank, null, upload_to=events/ | Обложка |
| capacity | PositiveIntegerField, default=0 | Лимит участников |
| price | DecimalField(10,2), null, blank, default=None | Цена; пусто — бесплатно |
| registration_type | CharField(20), choices, default=open | open / requires_approval / closed |
| status | CharField(30), choices, default=draft | draft / published / registration_closed / completed / cancelled |
| cancellation_reason | TextField, blank | Причина отмены |
| meta_title | CharField(200), blank | SEO |
| meta_description | CharField(300), blank | SEO |
| is_featured | BooleanField, default=False | Рекомендованное событие |
| **tags** | **M2M → Tag** | **related_name='events', blank** |
| **speakers** | **M2M → Speaker** | **related_name='events', blank** |
| created_at, updated_at | DateTimeField | Из `TimeStampedModel` |

---

## 3. Расписание (`events.EventSegment`)

| Поле | Тип | Описание |
|------|-----|----------|
| **event** | **FK → Event** | **CASCADE, related_name='segments'** |
| title | CharField(200) | Название сегмента |
| description | TextField, blank | Описание |
| time_start | TimeField | Начало |
| time_end | TimeField | Конец (в коде обязателен, без null) |
| order | PositiveIntegerField, default=0 | Порядок |
| location | CharField(200), blank | Место |
| **speakers** | **M2M → Speaker** | **related_name='event_segments', blank** |

---

## 4. Спикеры (`events.Speaker`)

| Поле | Тип | Описание |
|------|-----|----------|
| full_name | CharField(200) | ФИО |
| position | CharField(200), blank | Должность |
| company | CharField(200), blank | Компания |
| photo | ImageField, blank, null | Фото |
| bio | TextField, blank | Биография |
| email | EmailField, blank | Контакт |
| social_links | JSONField, default=dict, blank | Соцсети |
| **topics** | **M2M → Tag** | **related_name='speakers', blank** |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

**Обратные M2M:** `speaker.events` (через `Event.speakers`), `speaker.event_segments` (через `EventSegment.speakers`).

---

## 5. Теги (`core.Tag`)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(100) | Название |
| slug | SlugField(120), unique | URL (авто из name, если пусто) |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

**Обратные M2M:** `Event.tags`, `NewsArticle.tags`, `Speaker.topics` — со стороны тега: `tag.events`, `tag.news_articles`, `tag.speakers`.

---

## 6. Регистрации (`events.EventRegistration`)

| Поле | Тип | Описание |
|------|-----|----------|
| **user** | **FK → User** | **CASCADE, related_name='event_registrations'** |
| **event** | **FK → Event** | **CASCADE, related_name='registrations'** |
| status | CharField(20), choices, default=pending | pending / confirmed / cancelled |
| attendance_status | CharField(20), choices, default=unknown | unknown / attended / no_show |
| extra_data | JSONField, default=dict, blank | Доп. поля формы |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

**Meta:** `unique_together = [['user', 'event']]`.

---

## 7. Новости (`news.NewsArticle`)

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(300) | Заголовок |
| slug | SlugField(320), unique | URL |
| short_description | TextField, blank | Краткое описание |
| content | MDTextField, blank | Текст |
| cover_image | ImageField, blank, null | Обложка |
| publication_date | DateTimeField, null, blank | Дата публикации |
| read_time_minutes | PositiveIntegerField, default=0 | Время чтения |
| views_count | PositiveIntegerField, default=0 | Просмотры |
| **author** | **FK → User** | **SET_NULL, null, blank, related_name='news_articles'** |
| is_published | BooleanField, default=False | Черновик / опубликовано |
| meta_title | CharField(200), blank | SEO |
| meta_description | CharField(300), blank | SEO |
| **tags** | **M2M → Tag** | **related_name='news_articles', blank** |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 8. Материалы (`materials.MaterialCategory`, `materials.Material`)

**MaterialCategory**

| Поле | Тип | Описание |
|------|-----|----------|
| slug | SlugField(50), unique | Слаг |
| title | CharField(100) | Название |
| display_order | PositiveIntegerField, default=0 | Порядок |
| is_active | BooleanField, default=True | Активна |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

**Material**

| Поле | Тип | Описание |
|------|-----|----------|
| label | CharField(50), null, blank | Лейбл карточки |
| title | CharField(300) | Название |
| **category** | **FK → MaterialCategory** | **PROTECT, related_name='materials'** |
| date | DateField, null, blank | Дата |
| place | CharField(100), blank | Место / формат |
| duration_minutes | PositiveIntegerField, null, blank | Длительность, мин |
| description | TextField, blank | Описание |
| file_url | URLField, blank | Ссылка |
| cover_image | ImageField, blank, null | Превью |
| view_count | PositiveIntegerField, default=0 | Просмотры |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 9. Партнёры (`content.Partner`)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(200) | Компания |
| logo | ImageField, blank, null, upload_to=partners/ | Логотип |
| description | TextField, blank | Описание |
| website_url | URLField, blank | Сайт |
| partnership_level | CharField(20), choices, default=general | general / gold / silver |
| **event** | **FK → Event** | **SET_NULL, null, blank, related_name='partners'** |
| display_order | PositiveIntegerField, default=0 | Порядок |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 10. Команда (`content.TeamMember`)

| Поле | Тип | Описание |
|------|-----|----------|
| full_name | CharField(200) | ФИО |
| position | CharField(200), blank | Должность |
| photo | ImageField, blank, null | Фото |
| description | TextField, blank | Описание / роль в команде |
| email | EmailField, blank | Email |
| linkedin_url | URLField, blank | LinkedIn |
| twitter_url | URLField, blank | Twitter |
| display_order | PositiveIntegerField, default=0 | Порядок |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 11. Галерея (`events.EventGallery`)

| Поле | Тип | Описание |
|------|-----|----------|
| **event** | **FK → Event** | **CASCADE, related_name='galleries'** |
| title | CharField(200) | Название |
| cover_image | ImageField, blank, null | Обложка |
| photo_count | PositiveIntegerField, default=0 | Кол-во фото |
| external_album_url | URLField, blank | Внешний альбом |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 12. Настройки сайта (`content.SiteSettings`)

Singleton: в `save()` принудительно **`pk = 1`**, есть `SiteSettings.load()`.

| Поле | Тип | Описание |
|------|-----|----------|
| site_name | CharField(100), default="PM.Meetup" | Название |
| logo | ImageField, blank, null | Логотип |
| favicon | ImageField, blank, null | Иконка |
| email | EmailField, blank | Контактный email |
| phone | CharField(30), blank | Телефон |
| address | TextField, blank | Адрес |
| social_links | JSONField, default=dict, blank | Соцсети |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 13. Статичные страницы контента (`content.Page`)

Текстовые страницы («О нас», «Контакты») в Markdown.

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(200) | Заголовок |
| slug | SlugField(220), unique | URL |
| content | MDTextField, blank | Содержимое |
| is_published | BooleanField, default=False | Публикация |
| meta_title | CharField(200), blank | SEO |
| meta_description | CharField(300), blank | SEO |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

**Не путать** с `pages.Page` (конструктор блоков для SPA).

---

## 14. Заявки на партнёрство (`content.PartnershipApplication`)

| Поле | Тип | Описание |
|------|-----|----------|
| company_name | CharField(200) | Компания |
| contact_name | CharField(200) | Контакт |
| contact_email | EmailField | Email |
| contact_phone | CharField(30), blank | Телефон |
| message | TextField, blank | Сообщение |
| status | CharField(20), choices, default=new | new / in_review / accepted / rejected |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## 15. Конструктор страниц SPA (`pages.Page`, `PageBlock`, `BlockItem`, `BlockType`)

Логические страницы фронта (`slug`: home, about, …) и их блоки. **Не** `content.Page`.

### `pages.Page`

| Поле | Тип | Описание |
|------|-----|----------|
| slug | SlugField(100), unique | Идентификатор страницы для API/фронта |
| name | CharField(200) | Человекочитаемое название |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

### `pages.BlockType`

Справочник типов блоков (без `TimeStampedModel`).

| Поле | Тип | Описание |
|------|-----|----------|
| code | CharField(50), unique | Код (hero, faq, …) |
| name | CharField(200) | Название |
| description | TextField, blank | Описание |

### `pages.PageBlock`

| Поле | Тип | Описание |
|------|-----|----------|
| **page** | **FK → pages.Page** | **CASCADE, related_name='blocks'** |
| **block_type** | **FK → BlockType** | **CASCADE, related_name='page_blocks'** |
| order | PositiveIntegerField, default=0 | Порядок на странице |

### `pages.BlockItem`

| Поле | Тип | Описание |
|------|-----|----------|
| **block** | **FK → PageBlock** | **CASCADE, related_name='items'** |
| title | CharField(255), blank | Заголовок |
| subtitle | CharField(500), blank | Подзаголовок |
| content | TextField, blank | Контент |
| icon | CharField(255), blank | Ключ иконки для фронта |
| url | URLField, blank | Ссылка |
| order | PositiveIntegerField, default=0 | Порядок в блоке |
| created_at, updated_at | DateTimeField | `TimeStampedModel` |

---

## Схема связей (кратко)

```
User
 ├── event_registrations (EventRegistration)
 └── news_articles (NewsArticle.author, SET_NULL)

Event
 ├── segments (EventSegment)
 ├── registrations (EventRegistration)
 ├── partners (Partner, SET_NULL, null=True)
 ├── galleries (EventGallery)
 ├── tags (M2M → Tag)
 └── speakers (M2M → Speaker)

EventSegment
 ├── event (FK)
 └── speakers (M2M → Speaker)

Speaker
 ├── events (M2M)
 ├── event_segments (M2M)
 └── topics (M2M → Tag)

Tag ↔ Event, NewsArticle, Speaker (см. выше)

Material → MaterialCategory (FK, PROTECT)

pages.Page → PageBlock (FK, related_name='blocks')
PageBlock → BlockItem (FK, related_name='items')
PageBlock → BlockType (FK)
```

---

## Сводная таблица связей (FK / M2M)

| Модель | Поле | Тип | С кем | related_name / примечание |
|--------|------|-----|--------|---------------------------|
| **EventRegistration** | user | FK | User | `event_registrations`, CASCADE |
| **EventRegistration** | event | FK | Event | `registrations`, CASCADE; unique (user, event) |
| **EventSegment** | event | FK | Event | `segments`, CASCADE |
| **EventSegment** | speakers | M2M | Speaker | `event_segments` |
| **Event** | tags | M2M | Tag | `events` |
| **Event** | speakers | M2M | Speaker | `events` |
| **NewsArticle** | author | FK | User | `news_articles`, SET_NULL |
| **NewsArticle** | tags | M2M | Tag | `news_articles` |
| **Speaker** | topics | M2M | Tag | `speakers` |
| **Partner** | event | FK | Event | `partners`, SET_NULL |
| **EventGallery** | event | FK | Event | `galleries`, CASCADE |
| **Material** | category | FK | MaterialCategory | `materials`, PROTECT |
| **PageBlock** | page | FK | pages.Page | `blocks`, CASCADE |
| **PageBlock** | block_type | FK | BlockType | `page_blocks`, CASCADE |
| **BlockItem** | block | FK | PageBlock | `items`, CASCADE |

---

## Приоритет для MVP

Реализация уже покрывает перечисленное; при проектировании API учитывайте два типа страниц: **`content.Page`** и **`pages.Page`**.

1. **User** — обязательно  
2. **Event**, **EventRegistration** — ядро  
3. **Speaker**, **EventSegment** — карточка события  
4. **NewsArticle**, **Tag** — новости  
5. **Partner**, **TeamMember** — главная / о проекте  
6. **Material**, **MaterialCategory**, **EventGallery**  
7. **content.Page**, **pages** (блоки), **SiteSettings**, **PartnershipApplication**  
8. **ApiKey** — доступ к публичному API
