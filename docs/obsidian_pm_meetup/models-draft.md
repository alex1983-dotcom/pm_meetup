# Набросок моделей PM.Meetup

Предварительный черновик Django-моделей на основе макетов сайта и данной спецификации

---
## 1. Пользователи (User)

Расширение `AbstractUser` Django или кастомная модель для участников сообщества.

| Поле | Тип | Описание |
|------|-----|----------|
| email | EmailField, unique | Email — используется для входа вместо username |
| first_name | CharField | Имя |
| last_name | CharField | Фамилия |
| phone | CharField, optional | Номер телефона |
| avatar | ImageField, optional | Фото профиля |
| role | CharField/FK | Роль: участник, организатор, модератор и т.п. |
| is_blocked | BooleanField | Статус блокировки учётной записи |
| created_at | DateTimeField | Дата регистрации |

---

## 2. События (Event)

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField(100) | Название события |
| slug | SlugField | URL-путь для страницы события |
| description | TextField | Описание (rich text / markdown) |
| date | DateField | Дата проведения |
| time_start | TimeField | Время начала |
| time_end | TimeField | Время окончания (опционально) |
| format | CharField | Формат: offline / online / hybrid |
| location_address | CharField | Адрес (для офлайн) |
| location_city | CharField | Город |
| location_venue | CharField | Название помещения, зала |
| online_url | URLField | Ссылка на трансляцию (для онлайн) |
| online_platform | CharField | Платформа: Zoom, Google Meet и т.п. |
| event_type | CharField | Тип: meetup / workshop / conference / networking |
| cover_image | ImageField | Обложка события (рекомендуемый размер 1200×630) |
| capacity | IntegerField | Лимит участников |
| price | DecimalField | Цена участия (если платное) |
| registration_type | CharField | open / requires_approval / closed |
| status | CharField | draft / published / registration_closed / completed / cancelled |
| cancellation_reason | TextField | Причина отмены (если status=cancelled) |
| meta_title | CharField | SEO: заголовок страницы |
| meta_description | CharField | SEO: описание для поисковиков |
| is_featured | BooleanField | Показывать в блоке «Ваш выбор» |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 3. Расписание события (EventSegment)

Сегмент программы мероприятия (доклад, кофе-брейк и т.п.).

| Поле | Тип | Описание |
|------|-----|----------|
| event | ForeignKey(Event) | Событие |
| title | CharField | Название сегмента |
| description | TextField | Описание сегмента |
| time_start | TimeField | Время начала |
| time_end | TimeField | Время окончания |
| order | IntegerField | Порядок отображения |
| location | CharField | Место (для многозальных событий) |

**Связь:** M2M с моделью Speaker (спикеры сегмента).

---

## 4. Спикеры (Speaker)

| Поле | Тип | Описание |
|------|-----|----------|
| full_name | CharField | ФИО |
| position | CharField | Должность |
| company | CharField | Компания |
| photo | ImageField | Фотография |
| bio | TextField | Краткая биография |
| email | EmailField | Email для связи |
| social_links | JSONField | Ссылки на соцсети (LinkedIn, Telegram и т.п.) |
| created_at | DateTimeField | Дата добавления в базу |

**Связи:** M2M с Event (через EventSpeaker), M2M с EventSegment, M2M с Tag (темы выступлений).

---

## 5. Категории событий (EventCategory)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название категории |
| slug | SlugField | URL-путь |
| description | TextField | Описание категории |
| order | IntegerField | Порядок отображения в списках |

---

## 6. Теги (Tag)

Общие теги для событий и новостей.

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название тега |
| slug | SlugField | URL-путь |
| created_at | DateTimeField | Дата создания |

---

## 7. Регистрации на события (EventRegistration)

| Поле | Тип | Описание |
|------|-----|----------|
| user | ForeignKey(User) | Участник |
| event | ForeignKey(Event) | Событие |
| status | CharField | Подтверждена / ожидает / отменена |
| attendance_status | CharField | Посетил / не явился / неизвестно |
| extra_data | JSONField | Дополнительные поля формы регистрации |
| created_at | DateTimeField | Дата регистрации |
| updated_at | DateTimeField | Дата последнего изменения |

---

## 8. Новости (NewsArticle)

| Поле | Тип | Описание |
|------|-----|----------|
| title | CharField | Заголовок статьи |
| slug | SlugField | URL-путь для страницы новости |
| short_description | TextField | Краткое описание (для карточки) |
| content | RichTextField | Полный текст статьи |
| cover_image | ImageField | Обложка статьи |
| publication_date | DateTimeField | Дата публикации |
| read_time_minutes | IntegerField | Время чтения в минутах |
| views_count | IntegerField | Количество просмотров |
| author | ForeignKey(User) | Автор статьи |
| is_published | BooleanField | Опубликована или черновик |
| meta_title | CharField | SEO: заголовок |
| meta_description | CharField | SEO: описание |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата последнего изменения |

**Связь:** M2M с Tag.

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

---

## 10. Партнёры (Partner)

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название компании |
| logo | ImageField | Логотип |
| description | TextField | Краткое описание |
| website_url | URLField | Сайт партнёра |
| partnership_level | CharField | Уровень: general / gold / silver |
| event | ForeignKey(Event), null | Событие (null = глобальный партнёр) |
| display_order | IntegerField | Порядок отображения на сайте |
| created_at | DateTimeField | Дата добавления |

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
| display_order | IntegerField | Порядок отображения |
| created_at | DateTimeField | Дата добавления |

---

## 12. Галерея прошедших событий (EventGallery)

| Поле | Тип | Описание |
|------|-----|----------|
| event | ForeignKey(Event) | Связанное событие |
| title | CharField | Название галереи |
| cover_image | ImageField | Обложка галереи |
| photo_count | IntegerField | Количество фотографий |
| external_album_url | URLField | Ссылка на альбом (VK и т.п.) |
| created_at | DateTimeField | Дата создания |

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

---

## 15. Заявки на партнёрство (PartnershipApplication)

| Поле | Тип | Описание |
|------|-----|----------|
| company_name | CharField | Название компании |
| contact_name | CharField | Контактное лицо |
| contact_email | EmailField | Email |
| contact_phone | CharField | Телефон |
| message | TextField | Сообщение |
| status | CharField | new / in_review / accepted / rejected |
| created_at | DateTimeField | Дата заявки |

---

## Схема связей

```
User ──┬── EventRegistration ─── Event
       ├── NewsArticle (author)
       └── Comment (если будет)

Event ──┬── EventSegment ─── Speaker (M2M)
        ├── EventRegistration
        ├── EventCategory (M2M)
        ├── Tag (M2M)
        ├── Partner (optional FK)
        └── EventGallery

NewsArticle ─── Tag (M2M)
```

---

## Приоритет для MVP

1. **User** — обязательно
2. **Event**, **EventCategory**, **EventRegistration** — ядро
3. **Speaker**, **EventSegment** — для детальной страницы события
4. **NewsArticle**, **Tag** — раздел новостей
5. **Partner**, **TeamMember** — главная страница
6. **Material**, **EventGallery** — можно добавить позже
7. **Page**, **SiteSettings**, **PartnershipApplication** — по необходимости
