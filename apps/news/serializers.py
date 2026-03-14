from rest_framework import serializers

from apps.core.serializers import TagSerializer
from apps.news.models import NewsArticle
from apps.users.serializers import UserPublicSerializer


class NewsArticleListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = NewsArticle
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "cover_image",
            "publication_date",
            "read_time_minutes",
            "views_count",
            "author",
            "tags",
        )


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = NewsArticle
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "content",
            "cover_image",
            "publication_date",
            "read_time_minutes",
            "views_count",
            "author",
            "meta_title",
            "meta_description",
            "tags",
        )
