from rest_framework import serializers

from apps.materials.models import Material, MaterialCategory


class MaterialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = ("id", "slug", "title", "display_order", "is_active")


class MaterialListSerializer(serializers.ModelSerializer):
    category = MaterialCategorySerializer(read_only=True)

    class Meta:
        model = Material
        fields = (
            "id",
            "label",
            "title",
            "category",
            "date",
            "place",
            "duration_minutes",
            "cover_image",
            "view_count",
        )


class MaterialDetailSerializer(serializers.ModelSerializer):
    category = MaterialCategorySerializer(read_only=True)

    class Meta:
        model = Material
        fields = (
            "id",
            "label",
            "title",
            "category",
            "date",
            "place",
            "duration_minutes",
            "description",
            "file_url",
            "cover_image",
            "view_count",
        )
