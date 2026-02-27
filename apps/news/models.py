from django.db import models
from django.conf import settings
from django.utils.text import slugify

from mdeditor.fields import MDTextField

from apps.core.models import TimeStampedModel, Tag


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
