from datetime import date, time

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from apps.core.models import ApiKey, Tag
from apps.events.models import Event
from apps.events.views import EventViewSet


class EventSearchApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key = ApiKey.objects.create(name="tests-key", is_active=True)
        cls.tag_pm = Tag.objects.create(name="Project Management", slug="pm")
        cls.tag_soft = Tag.objects.create(name="Soft Skills", slug="soft-skills")

        cls.event = Event.objects.create(
            title="Project Management Meetup",
            slug="project-management-meetup",
            description="Talks about planning, scope and risk management.",
            date=date(2026, 4, 10),
            time_start=time(19, 0),
            status="published",
            location_city="Minsk",
            location_venue="Main Hall",
        )
        cls.event.tags.set([cls.tag_pm, cls.tag_soft])
        # Второе событие — чтобы проверить сортировку по search_rank (не один элемент в выдаче)
        cls.event_other = Event.objects.create(
            title="Agile Workshop",
            slug="agile-workshop",
            description="Scrum and Kanban; management is mentioned briefly.",
            date=date(2026, 6, 1),
            time_start=time(18, 0),
            status="published",
            location_city="Minsk",
            location_venue="Hall B",
        )
        # Без тегов: фильтр `tags=pm,soft-skills` (IN) иначе совпадёт и второе событие
        cls.event_other.tags.clear()


    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)

    def test_trigram_search_returns_events(self):
        response = self.client.get(
            "/api/v1/events/events/",
            {"search": "managment", "min_rank": "0.10"},
        )
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data["results"]]
        self.assertIn(self.event.title, titles)

    def test_min_rank_filters_out_weak_matches(self):
        response = self.client.get(
            "/api/v1/events/events/",
            {"search": "managment", "min_rank": "0.95"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_tag_filters(self):
        single_tag_response = self.client.get("/api/v1/events/events/", {"tag": "pm"})
        self.assertEqual(single_tag_response.status_code, 200)
        self.assertEqual(single_tag_response.data["count"], 1)

        multi_tag_response = self.client.get(
            "/api/v1/events/events/",
            {"tags": "pm,soft-skills"},
        )
        self.assertEqual(multi_tag_response.status_code, 200)
        self.assertEqual(multi_tag_response.data["count"], 1)

    def test_search_list_order_matches_viewset_search_rank(self):
        """
        Интеграция: порядок в JSON совпадает с order_by(-search_rank, ...) из EventViewSet.get_queryset().
        """
        params = {"search": "management", "min_rank": "0.08", "status": "published"}
        factory = APIRequestFactory()
        django_request = factory.get("/api/v1/events/events/", params)
        drf_request = Request(django_request)
        view = EventViewSet()
        view.request = drf_request
        view.action = "list"
        expected_slugs = list(view.get_queryset().values_list("slug", flat=True))

        response = self.client.get("/api/v1/events/events/", params)
        self.assertEqual(response.status_code, 200)
        api_slugs = [row["slug"] for row in response.data["results"]]
        self.assertEqual(
            api_slugs,
            expected_slugs,
            msg="Порядок API должен совпадать с сортировкой по search_rank в ViewSet.",
        )
