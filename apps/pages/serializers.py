from rest_framework import serializers

from apps.pages.models import BlockItem, BlockType, Page, PageBlock


class BlockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockItem
        fields = ("id", "title", "subtitle", "content", "icon", "order")


class BlockTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockType
        fields = ("code", "name")


class PageBlockSerializer(serializers.ModelSerializer):
    block_type = BlockTypeSerializer(read_only=True)
    items = BlockItemSerializer(many=True, read_only=True)

    class Meta:
        model = PageBlock
        fields = ("id", "block_type", "order", "items")


class PageSerializer(serializers.ModelSerializer):
    blocks = PageBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ("slug", "name", "blocks")

