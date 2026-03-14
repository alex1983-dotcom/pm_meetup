from rest_framework import serializers

from apps.users.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    """Публичные поля пользователя (автор новости, спикер и т.д.)."""

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "avatar")
