from django.db import models

from apps.core.models import TimeStampedModel


class MaterialCategory(TimeStampedModel):
    """Категория материалов (Курсы, Хендбуки и т.п.)."""

    slug = models.SlugField("Слаг", max_length=50, unique=True)
    title = models.CharField("Название", max_length=100)
    display_order = models.PositiveIntegerField("Порядок отображения", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Категория материала"
        verbose_name_plural = "Категории материалов"
        ordering = ["display_order", "title"]

    def __str__(self) -> str:
        return self.title


class Material(TimeStampedModel):
    """Материал: отчёт, курс, чек-лист, запись, кейс."""

    label = models.CharField(
        "Тип/лейбл",
        max_length=50,
        blank=True,
        null=True,
        help_text="Текст в верхней строке карточки: КУРС, ЗАПИСЬ, ХЕНДБУК, ФОТОГРАФИИ",
    )
    title = models.CharField("Название", max_length=300)
    category = models.ForeignKey(
        MaterialCategory,
        verbose_name="Категория",
        related_name="materials",
        on_delete=models.PROTECT,
    )
    date = models.DateField("Дата", blank=True, null=True)
    place = models.CharField(
        "Место/формат",
        max_length=100,
        blank=True,
        help_text="Например: Минск или Online",
    )
    duration_minutes = models.PositiveIntegerField(
        "Длительность, минут", blank=True, null=True
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

    def __str__(self) -> str:
        return self.title

