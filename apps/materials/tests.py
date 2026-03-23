from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from apps.core.models import ApiKey
from apps.materials.models import Material, MaterialCategory
from apps.materials.views import MaterialViewSet


class MaterialSearchApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key = ApiKey.objects.create(name="tests-materials-key", is_active=True)
        cls.category_courses = MaterialCategory.objects.create(
            slug="courses",
            title="Courses",
            is_active=True,
        )
        cls.category_books = MaterialCategory.objects.create(
            slug="books",
            title="Books",
            is_active=True,
        )
        cls.material = Material.objects.create(
            title="Workshop Recording: Product Discovery",
            label="RECORDING",
            category=cls.category_courses,
            place="Online",
            description="Session about product discovery and facilitation.",
        )
        cls.material_other = Material.objects.create(
            title="Product Analytics Checklist",
            label="PDF",
            category=cls.category_books,
            place="Online",
            description="Metrics and dashboards.",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)

    def test_trigram_search_returns_materials(self):
        response = self.client.get(
            "/api/v1/materials/materials/",
            {"search": "workshp", "min_rank": "0.10"},
        )
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data["results"]]
        self.assertIn(self.material.title, titles)

    def test_min_rank_filters_out_weak_matches(self):
        response = self.client.get(
            "/api/v1/materials/materials/",
            {"search": "workshp", "min_rank": "0.95"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_category_filter(self):
        response = self.client.get(
            "/api/v1/materials/materials/",
            {"category": "courses"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        books_response = self.client.get(
            "/api/v1/materials/materials/",
            {"category": "books"},
        )
        self.assertEqual(books_response.status_code, 200)
        self.assertEqual(books_response.data["count"], 1)

    def test_search_list_order_matches_viewset_search_rank(self):
        """
        Порядок в ответе API совпадает с order_by(-search_rank, ...) в MaterialViewSet.get_queryset().
        """
        params = {"search": "product", "min_rank": "0.08"}
        factory = APIRequestFactory()
        django_request = factory.get("/api/v1/materials/materials/", params)
        drf_request = Request(django_request)
        view = MaterialViewSet()
        view.request = drf_request
        view.action = "list"
        expected_ids = list(view.get_queryset().values_list("id", flat=True))

        response = self.client.get("/api/v1/materials/materials/", params)
        self.assertEqual(response.status_code, 200)
        api_ids = [row["id"] for row in response.data["results"]]
        self.assertEqual(
            api_ids,
            expected_ids,
            msg="Порядок API должен совпадать с сортировкой по search_rank в ViewSet.",
        )
