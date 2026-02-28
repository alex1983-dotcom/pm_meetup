# Набросок моделей PM.Meetup

Предварительный черновик Django-моделей на основе макетов сайта и данной спецификации

---
## 1. Пользователи (User)

Расширение `AbstractUser` Django или кастомная модель для участников сообщества.

**Связи (обратные):**
- **EventRegistration** — у пользователя много регистраций на события (`user.event_registrations`).
- **NewsArticle** — у пользователя много статей как у автора (`user.news_articles`, author, FK с SET_NULL).

| Поле | Тип | Описание |
|------|-----|----------|
| email | EmailField, unique | Email — используется для входа вместо username |
| first_name | CharField(150), blank | Имя |
| last_name | CharField(150), blank | Фамилия |
| phone | CharField(20), blank | Номер телефона |
| avatar | ImageField, blank, null | Фото профиля |
| role | CharField(30) | Роль: member / organizer / moderator / admin / superadmin |
| is_blocked | BooleanField | Статус блокировки учётной записи |
| created_at | DateTimeField | Дата регистрации |
| **event_registrations** | **обратная FK (EventRegistration.user)** | **related_name='event_registrations', CASCADE** |
| **news_articles** | **обратная FK (NewsArticle.author)** | **related_name='news_articles', SET_NULL** |

---

## 2. События (Event)

**Связи:**
- **ForeignKey (обратные):** EventSegment (`event.segments`), EventRegistration (`event.registrations`), Partner (`event.partners`, null=True), EventGallery (`event.galleries`).
- **ManyToMany:** EventCategory (`event.categories` ↔ `category.events`), Tag (`event.tags` ↔ `tag.events`), Speaker (`event.speakers` ↔ `speaker.events`).

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(200) | Название события |
| slug | SlugField(220), unique | URL-путь для страницы события |
| description | MDTextField | Описание (markdown) |
| date | DateField | Дата проведения |
| time_start | TimeField | Время начала |
| time_end | TimeField, null, blank | Время окончания (опционально) |
| format | CharField(20) | Формат: offline / online / hybrid |
| location_address | CharField(300), blank | Адрес (для офлайн) |
| location_city | CharField(100), blank | Город |
| location_venue | CharField(200), blank | Название помещения, зала |
| online_url | URLField, blank | Ссылка на трансляцию (для онлайн) |
| online_platform | CharField(100), blank | Платформа: Zoom, Google Meet и т.п. |
| event_type | CharField(20) | Тип: meetup / workshop / conference / networking |
| cover_image | ImageField, blank, null | Обложка события (рекомендуемый размер 1200×630) |
| capacity | PositiveIntegerField | Лимит участников |
| price | DecimalField(10,2) | Цена участия (если платное) |
| registration_type | CharField(20) | open / requires_approval / closed |
| status | CharField(30) | draft / published / registration_closed / completed / cancelled |
| cancellation_reason | TextField, blank | Причина отмены (если status=cancelled) |
| meta_title | CharField(200), blank | SEO: заголовок страницы |
| meta_description | CharField(300), blank | SEO: описание для поисковиков |
| is_featured | BooleanField | Показывать в блоке «Ваш выбор» |
| **categories** | **ManyToManyField(EventCategory)** | **related_name='events', blank** |
| **tags** | **ManyToManyField(Tag)** | **related_name='events', blank** |
| **speakers** | **ManyToManyField(Speaker)** | **related_name='events', blank** |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 3. Расписание события (EventSegment)

Сегмент программы мероприятия (доклад, кофе-брейк и т.п.).

| Поле | Тип | Описание |
|------|-----|----------|
| **event** | **ForeignKey(Event)** | **CASCADE, related_name='segments'** |
| title | CharField(200) | Название сегмента |
| description | TextField, blank | Описание сегмента |
| time_start | TimeField | Время начала |
| time_end | TimeField | Время окончания |
| order | PositiveIntegerField | Порядок отображения |
| location | CharField(200), blank | Место (для многозальных событий) |
| **speakers** | **ManyToManyField(Speaker)** | **related_name='event_segments', blank** |

**Связи:**
- **ForeignKey:** Event (`segment.event` → Event, `related_name='segments'`).
- **ManyToMany:** Speaker (`segment.speakers` ↔ `speaker.event_segments` — спикеры сегмента).

---

## 4. Спикеры (Speaker)

| Поле | Тип | Описание |
|------|-----|----------|
| full_name | CharField(200) | ФИО |
| position | CharField(200), blank | Должность |
| company | CharField(200), blank | Компания |
| photo | ImageField, blank, null | Фотография |
| bio | TextField, blank | Краткая биография |
| email | EmailField, blank | Email для связи |
| social_links | JSONField, default=dict, blank | Ссылки на соцсети (LinkedIn, Telegram и т.п.) |
| **topics** | **ManyToManyField(Tag)** | **related_name='speakers', blank — темы выступлений** |
| created_at | DateTimeField | Дата добавления в базу |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи (обратные M2M, поле не в Speaker):** Event (`speaker.events` — через Event.speakers), EventSegment (`speaker.event_segments` — через EventSegment.speakers).

---

## 5. Категории событий (EventCategory)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(100) | Название категории |
| slug | SlugField(120), unique | URL-путь |
| description | TextField, blank | Описание категории |
| order | PositiveIntegerField | Порядок отображения в списках |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |
| **events** | **обратная M2M (Event.categories)** | **related_name='events' — события этой категории** |

**Связи (обратные):** Поле связи задаётся в Event (categories → EventCategory). Со стороны EventCategory доступно `category.events`.

---

## 6. Теги (Tag)

Общие теги для событий и новостей.

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(100) | Название тега |
| slug | SlugField(120), unique | URL-путь |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |
| **events** | **обратная M2M (Event.tags)** | **related_name='events'** |
| **news_articles** | **обратная M2M (NewsArticle.tags)** | **related_name='news_articles'** |
| **speakers** | **обратная M2M (Speaker.topics)** | **related_name='speakers' — спикеры с этой темой** |

**Связи (обратные):** Поля связи заданы в Event (tags), NewsArticle (tags), Speaker (topics). Со стороны Tag доступны `tag.events`, `tag.news_articles`, `tag.speakers`.

---

## 7. Регистрации на события (EventRegistration)

| Поле | Тип | Описание |
|------|-----|----------|
| **user** | **ForeignKey(User)** | **CASCADE, related_name='event_registrations'** |
| **event** | **ForeignKey(Event)** | **CASCADE, related_name='registrations'** |
| status | CharField(20) | pending / confirmed / cancelled |
| attendance_status | CharField(20) | unknown / attended / no_show |
| extra_data | JSONField, default=dict, blank | Дополнительные поля формы регистрации |
| created_at | DateTimeField | Дата регистрации |
| updated_at | DateTimeField | Дата последнего изменения |

**Ограничение:** unique_together = (user, event).

---

## 8. Новости (NewsArticle)

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(300) | Заголовок статьи |
| slug | SlugField(320), unique | URL-путь для страницы новости |
| short_description | TextField, blank | Краткое описание (для карточки) |
| content | MDTextField, blank | Полный текст статьи (markdown) |
| cover_image | ImageField, blank, null | Обложка статьи |
| publication_date | DateTimeField, null, blank | Дата публикации |
| read_time_minutes | PositiveIntegerField | Время чтения в минутах |
| views_count | PositiveIntegerField | Количество просмотров |
| **author** | **ForeignKey(User)** | **SET_NULL, null=True, blank=True, related_name='news_articles'** |
| is_published | BooleanField | Опубликована или черновик |
| meta_title | CharField(200), blank | SEO: заголовок |
| meta_description | CharField(300), blank | SEO: описание |
| **tags** | **ManyToManyField(Tag)** | **related_name='news_articles', blank** |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 9. Материалы (Material)

Раздел «Материалы»: отчёты, курсы, чек-листы, записи.

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField | Название материала |
| category | CharField | Тип: report / course / checklist / recording / case_study |
| description | TextField | Описание |
| file_url | URLField | Ссылка на файл или страницу |
| cover_image | ImageField | Превью |
| view_count | IntegerField | Количество просмотров |
| created_at | DateTimeField | Дата добавления |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи:** нет (модель не ссылается на другие приложения).

---

## 10. Партнёры (Partner)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название компании |
| logo | ImageField | Логотип |
| description | TextField | Краткое описание |
| website_url | URLField | Сайт партнёра |
| partnership_level | CharField(20) | Уровень: general / gold / silver |
| **event** | **ForeignKey(Event)** | **SET_NULL, null=True, blank=True, related_name='partners' — null = глобальный партнёр** |
| display_order | PositiveIntegerField | Порядок отображения на сайте |
| created_at | DateTimeField | Дата добавления |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 11. Команда (TeamMember)

| Поле | Тип | Описание |
|------|-----|----------|
| full_name | CharField | ФИО |
| position | CharField | Должность в команде |
| photo | ImageField | Фотография |
| bio | TextField | Краткая биография |
| email | EmailField | Email |
| linkedin_url | URLField | Профиль LinkedIn |
| twitter_url | URLField | Профиль Twitter |
| display_order | PositiveIntegerField | Порядок отображения |
| created_at | DateTimeField | Дата добавления |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи:** нет (модель не ссылается на другие приложения).

---

## 12. Галерея прошедших событий (EventGallery)

| Поле | Тип | Описание |
|------|-----|----------|
| **event** | **ForeignKey(Event)** | **CASCADE, related_name='galleries'** |
| title | CharField(200) | Название галереи |
| cover_image | ImageField, blank, null | Обложка галереи |
| photo_count | PositiveIntegerField | Количество фотографий |
| external_album_url | URLField, blank | Ссылка на альбом (VK и т.п.) |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 13. Настройки сайта (SiteSettings)

Singleton-модель для общих настроек.

| Поле | Тип | Описание |
|------|-----|----------|
| site_name | CharField | Название сайта |
| logo | ImageField | Логотип |
| favicon | ImageField | Иконка сайта |
| email | EmailField | Email для контактов |
| phone | CharField | Телефон |
| address | TextField | Адрес |
| social_links | JSONField | Ссылки на соцсети |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи:** нет (singleton, не ссылается на другие модели).

---

## 14. Страницы (Page)

Статичные страницы (О нас, Контакты, Правила).

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField | Заголовок страницы |
| slug | SlugField | URL-путь |
| content | RichTextField | Содержимое страницы |
| is_published | BooleanField | Опубликована или черновик |
| meta_title | CharField | SEO: заголовок |
| meta_description | CharField | SEO: описание |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи:** нет (статичные страницы не ссылаются на другие модели).

---

## 15. Заявки на партнёрство (PartnershipApplication)

| Поле | Тип | Описание |
|------|-----|----------|
| company_name | CharField | Название компании |
| contact_name | CharField | Контактное лицо |
| contact_email | EmailField | Email |
| contact_phone | CharField | Телефон |
| message | TextField | Сообщение |
| status | CharField(20) | new / in_review / accepted / rejected |
| created_at | DateTimeField | Дата заявки |
| updated_at | DateTimeField | Дата последнего изменения |

**Связи:** нет (заявка не привязана к User/Event и т.д.).

---

## Схема связей

Подробная диаграмма связей: см. [models-relations-diagram.md](models-relations-diagram.md).

```
User
 ├── event_registrations (EventRegistration) ──► event
 └── news_articles (NewsArticle, author, SET_NULL)

Event
 ├── segments (EventSegment, FK, CASCADE)
 ├── registrations (EventRegistration, FK, CASCADE)
 ├── partners (Partner, FK, SET_NULL, null=True)
 ├── galleries (EventGallery, FK, CASCADE)
 ├── categories (EventCategory, M2M)
 ├── tags (Tag, M2M)
 └── speakers (Speaker, M2M)

EventSegment
 ├── event (Event, FK, CASCADE)
 └── speakers (Speaker, M2M)

Speaker
 ├── events (Event, M2M)
 ├── event_segments (EventSegment, M2M)
 └── topics (Tag, M2M)

EventCategory ─── events (Event, M2M)

Tag
 ├── events (Event, M2M)
 ├── news_articles (NewsArticle, M2M)
 └── speakers (Speaker, M2M — поле topics)

EventRegistration
 ├── user (User, FK, CASCADE)
 └── event (Event, FK, CASCADE)   unique_together (user, event)

NewsArticle
 ├── author (User, FK, SET_NULL, null, blank)
 └── tags (Tag, M2M)

Partner ─── event (Event, FK, SET_NULL, null=True)

EventGallery ─── event (Event, FK, CASCADE)

Material, TeamMember, SiteSettings, Page, PartnershipApplication — связей с другими моделями нет.
```

---

## Сводная таблица связей

| Модель | Поле в модели | Тип | С кем | related_name (обратная сторона) | on_delete / примечание |
|--------|----------------|-----|--------|----------------------------------|------------------------|
| **User** | — | обратная FK | EventRegistration | `user.event_registrations` | задано в EventRegistration.user, CASCADE |
| **User** | — | обратная FK | NewsArticle | `user.news_articles` | задано в NewsArticle.author, SET_NULL, null, blank |
| **Event** | categories | M2M | EventCategory | `event.categories` ↔ `category.events` | blank |
| **Event** | tags | M2M | Tag | `event.tags` ↔ `tag.events` | blank |
| **Event** | speakers | M2M | Speaker | `event.speakers` ↔ `speaker.events` | blank |
| **Event** | — | обратная FK | EventSegment | `event.segments` | задано в EventSegment.event, CASCADE |
| **Event** | — | обратная FK | EventRegistration | `event.registrations` | задано в EventRegistration.event, CASCADE |
| **Event** | — | обратная FK | Partner | `event.partners` | задано в Partner.event, SET_NULL, null, blank |
| **Event** | — | обратная FK | EventGallery | `event.galleries` | задано в EventGallery.event, CASCADE |
| **EventSegment** | event | FK | Event | `segment.event` → `event.segments` | CASCADE |
| **EventSegment** | speakers | M2M | Speaker | `segment.speakers` ↔ `speaker.event_segments` | blank |
| **Speaker** | topics | M2M | Tag | `speaker.topics` ↔ `tag.speakers` | blank, темы выступлений |
| **Speaker** | — | обратная M2M | Event | `speaker.events` | задано в Event.speakers |
| **Speaker** | — | обратная M2M | EventSegment | `speaker.event_segments` | задано в EventSegment.speakers |
| **EventCategory** | — | обратная M2M | Event | `category.events` | задано в Event.categories |
| **Tag** | — | обратная M2M | Event | `tag.events` | задано в Event.tags |
| **Tag** | — | обратная M2M | NewsArticle | `tag.news_articles` | задано в NewsArticle.tags |
| **Tag** | — | обратная M2M | Speaker | `tag.speakers` | задано в Speaker.topics |
| **EventRegistration** | user | FK | User | `registration.user` → `user.event_registrations` | CASCADE |
| **EventRegistration** | event | FK | Event | `registration.event` → `event.registrations` | CASCADE; unique_together (user, event) |
| **NewsArticle** | author | FK | User | `article.author` → `user.news_articles` | SET_NULL, null=True, blank=True |
| **NewsArticle** | tags | M2M | Tag | `article.tags` ↔ `tag.news_articles` | blank |
| **Partner** | event | FK | Event | `partner.event` → `event.partners` | SET_NULL, null=True, blank=True |
| **EventGallery** | event | FK | Event | `gallery.event` → `event.galleries` | CASCADE |

---

## Приоритет для MVP

1. **User** — обязательно
2. **Event**, **EventCategory**, **EventRegistration** — ядро
3. **Speaker**, **EventSegment** — для детальной страницы события
4. **NewsArticle**, **Tag** — раздел новостей
5. **Partner**, **TeamMember** — главная страница
6. **Material**, **EventGallery** — можно добавить позже
7. **Page**, **SiteSettings**, **PartnershipApplication** — по необходимости
