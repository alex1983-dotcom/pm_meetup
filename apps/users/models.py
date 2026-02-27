from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
