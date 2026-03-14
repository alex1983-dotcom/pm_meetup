from rest_framework import serializers

from apps.content.models import Page, Partner, PartnershipApplication, SiteSettings, TeamMember


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = (
            "id",
            "name",
            "logo",
            "description",
            "website_url",
            "partnership_level",
            "event",
            "display_order",
        )


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = (
            "id",
            "full_name",
            "position",
            "photo",
            "description",
            "email",
            "linkedin_url",
            "twitter_url",
            "display_order",
        )


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = (
            "id",
            "site_name",
            "logo",
            "favicon",
            "email",
            "phone",
            "address",
            "social_links",
        )


class ContentPageSerializer(serializers.ModelSerializer):
    """Статичная страница контента (О нас, Контакты и т.д.)."""

    class Meta:
        model = Page
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "meta_title",
            "meta_description",
        )


class PartnershipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnershipApplication
        fields = (
            "id",
            "company_name",
            "contact_name",
            "contact_email",
            "contact_phone",
            "message",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at")
