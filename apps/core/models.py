from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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