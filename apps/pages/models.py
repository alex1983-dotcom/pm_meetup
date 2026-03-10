from django.db import models

from apps.core.models import TimeStampedModel


class Page(TimeStampedModel):
    """
    Логическая страница фронтенда, для которой настраиваются блоки.
    Пример slug: 'home', 'about', 'services'.
    """

    slug = models.SlugField("Slug страницы", max_length=100, unique=True)
    name = models.CharField("Название страницы", max_length=200)

    class Meta:
        verbose_name = "Страница (блоки)"
        verbose_name_plural = "Страницы (блоки)"
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class BlockType(models.Model):
    """
    Справочник типов блоков.
    Пример code: 'hero', 'applications', 'faq'.
    """

    code = models.CharField("Код типа блока", max_length=50, unique=True)
    name = models.CharField("Название типа блока", max_length=200)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Тип блока"
        verbose_name_plural = "Типы блоков"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class PageBlock(models.Model):
    """
    Конкретный блок на конкретной странице.
    Не содержит текстов, только тип и порядок.
    """

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="blocks",
        verbose_name="Страница",
    )
    block_type = models.ForeignKey(
        BlockType,
        on_delete=models.CASCADE,
        related_name="page_blocks",
        verbose_name="Тип блока",
    )
    order = models.PositiveIntegerField("Порядок на странице", default=0)

    class Meta:
        verbose_name = "Блок страницы"
        verbose_name_plural = "Блоки страниц"
        ordering = ["page", "order", "id"]

    def __str__(self) -> str:
        return f"{self.page.slug} — {self.block_type.code} (#{self.order})"


class BlockItem(TimeStampedModel):
    """
    Элемент внутри блока:
    заголовок / подзаголовок / контент / иконка.
    """

    block = models.ForeignKey(
        PageBlock,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Блок",
    )
    title = models.CharField("Заголовок", max_length=255, blank=True)
    subtitle = models.CharField("Подзаголовок", max_length=500, blank=True)
    content = models.TextField("Контент", blank=True)
    icon = models.CharField(
        "Иконка",
        max_length=255,
        blank=True,
        help_text="Ключ или путь до иконки, который использует фронтенд",
    )
    url = models.URLField(
        "Ссылка",
        blank=True,
        help_text="Произвольная ссылка (например, на YouTube-видео или внешний ресурс)",
    )
    order = models.PositiveIntegerField("Порядок внутри блока", default=0)

    class Meta:
        verbose_name = "Элемент блока"
        verbose_name_plural = "Элементы блока"
        ordering = ["block", "order", "id"]

    def __str__(self) -> str:
        return self.title or f"Элемент #{self.pk} блока {self.block_id}"

