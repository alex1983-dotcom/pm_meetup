# Диаграмма связей моделей PM.Meetup

> Сверено с кодом `apps/*/models.py`. **Material** → **MaterialCategory** (FK `category`). Две разные модели **Page**: `content.Page` (Markdown-страница) и `pages.Page` (логическая страница + блоки **PageBlock** / **BlockItem** / **BlockType**).

Наглядная схема связей между моделями (ForeignKey и ManyToMany). Подписи на линиях — имена полей и related_name.

---

## 1. Ядро: пользователи, события, регистрации, галереи

```mermaid
flowchart TB
  subgraph users_reg [Пользователи и регистрации]
    User
    EventRegistration
  end
  subgraph events_core [События]
    Event
    EventSegment
    EventGallery
  end
  subgraph ref [Справочники и люди]
    Speaker
    Tag
  end

  EventRegistration -->|"user"| User
  EventRegistration -->|"event"| Event
  EventSegment -->|"event"| Event
  EventGallery -->|"event"| Event

  Event ---|"tags / events"| Tag
  Event ---|"speakers / events"| Speaker
  EventSegment ---|"speakers / event_segments"| Speaker
  Speaker ---|"topics / speakers"| Tag
```

- **Стрелка (→):** ForeignKey. Направление от модели, у которой объявлено поле, к модели, на которую ссылаются. Подпись — имя поля (например, `event`, `user`).
- **Двойная линия (—):** ManyToMany. Подпись в формате `поле / related_name` (например, у Event поле `tags`, у Tag обратный доступ `events`).

---

## 2. Контент (`apps.content`): новости, партнёры, статичная страница

```mermaid
flowchart TB
  subgraph content_related [Связи с User, Event и Tag]
    User
    Event
    Tag
    NewsArticle
    Partner
  end
  subgraph content_standalone ["Без FK на другие приложения"]
    ContentPage["Page — content"]
    TeamMember
    SiteSettings
    PartnershipApplication
  end

  NewsArticle -->|"author"| User
  NewsArticle ---|"tags / news_articles"| Tag
  Partner -->|"event"| Event
```

**`content.Page`** — одна запись = одна статичная страница (поле `content` — Markdown через MDEditor), без связей с событиями. **TeamMember**, **SiteSettings**, **PartnershipApplication** — без внешних ключей на другие модели приложения.

---

## 3. Материалы (`apps.materials`)

```mermaid
flowchart TB
  MaterialCategory
  Material
  Material -->|"category / materials"| MaterialCategory
```

- **Material** ссылается на **MaterialCategory** (`on_delete=PROTECT`); у категории обратная выборка `materials`.

---

## 4. Страницы из блоков (`apps.pages`)

Отдельно от `content.Page`: здесь **логический slug** страницы и состав **блоков** для фронтенда.

```mermaid
flowchart TB
  subgraph pages_app [apps.pages]
    PagesPage["Page — pages"]
    BlockType
    PageBlock
    BlockItem
  end

  PageBlock -->|"page"| PagesPage
  PageBlock -->|"block_type"| BlockType
  BlockItem -->|"block"| PageBlock
```

---

## Легенда

| Обозначение | Значение | Пример в коде |
|-------------|----------|----------------|
| **Стрелка → с подписью** | ForeignKey: у модели-источника есть поле с таким именем | `EventSegment.event` — поле в коде; у события обратно: `event.segments` (related_name) |
| **Линия — с подписью "A / B"** | ManyToMany: с одной стороны поле A, с другой related_name B | У Event поле `tags`, у Tag обратный доступ — `events` |

**Как читать подписи:**
- **Поле** — объявлено в классе модели (например, `event = models.ForeignKey(Event, ...)`). Обращение: `объект_сегмента.event` → получишь событие.
- **related_name** — обратная связь на другой модели; в коде поле не объявляется, его даёт Django. Обращение: `объект_события.segments` → получишь все сегменты этого события.

**Примеры из проекта:**
- `segment.event` — поле (одно событие у сегмента).
- `event.segments` — related_name (много сегментов у события).
- `event.speakers` и `speaker.events` — M2M: поле на Event, related_name на Speaker.
