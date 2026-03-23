from django.test import TestCase
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from apps.core.models import ApiKey, Tag
from apps.news.models import NewsArticle
from apps.news.views import NewsArticleViewSet


class NewsSearchApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key = ApiKey.objects.create(name="tests-news-key", is_active=True)
        cls.tag_trends = Tag.objects.create(name="Trends", slug="trends")
        cls.tag_pm = Tag.objects.create(name="PM", slug="pm")

        cls.article = NewsArticle.objects.create(
            title="Project Management Trends 2026",
            slug="project-management-trends-2026",
            short_description="Industry outlook for PMs.",
            content="Roadmaps, planning, risks and product delivery.",
            publication_date=timezone.now(),
            is_published=True,
        )
        cls.article.tags.set([cls.tag_trends, cls.tag_pm])
        cls.article_other = NewsArticle.objects.create(
            title="Design Systems Weekly",
            slug="design-systems-weekly",
            short_description="UI tokens and components.",
            content="CSS variables only; no product management section.",
            publication_date=timezone.now(),
            is_published=True,
        )
        cls.article_other.tags.set([cls.tag_trends])

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)

    def test_trigram_search_returns_news(self):
        response = self.client.get(
            "/api/v1/news/articles/",
            {"search": "managment trands", "min_rank": "0.10"},
        )
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data["results"]]
        self.assertIn(self.article.title, titles)

    def test_min_rank_filters_out_weak_matches(self):
        response = self.client.get(
            "/api/v1/news/articles/",
            {"search": "managment trands", "min_rank": "0.95"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_tag_filters(self):
        single_tag_response = self.client.get("/api/v1/news/articles/", {"tag": "pm"})
        self.assertEqual(single_tag_response.status_code, 200)
        self.assertEqual(single_tag_response.data["count"], 1)

        multi_tag_response = self.client.get(
            "/api/v1/news/articles/",
            {"tags": "pm,trends"},
        )
        self.assertEqual(multi_tag_response.status_code, 200)
        # tags__slug__in — хотя бы один из слагов; у обеих статей есть `trends`
        self.assertEqual(multi_tag_response.data["count"], 2)

    def test_search_list_order_matches_viewset_search_rank(self):
        """
        Порядок в ответе API совпадает с order_by(-search_rank, ...) в NewsArticleViewSet.get_queryset().
        """
        params = {"search": "management", "min_rank": "0.08"}
        factory = APIRequestFactory()
        django_request = factory.get("/api/v1/news/articles/", params)
        drf_request = Request(django_request)
        view = NewsArticleViewSet()
        view.request = drf_request
        view.action = "list"
        expected_slugs = list(view.get_queryset().values_list("slug", flat=True))

        response = self.client.get("/api/v1/news/articles/", params)
        self.assertEqual(response.status_code, 200)
        api_slugs = [row["slug"] for row in response.data["results"]]
        self.assertEqual(
            api_slugs,
            expected_slugs,
            msg="Порядок API должен совпадать с сортировкой по search_rank в ViewSet.",
        )
