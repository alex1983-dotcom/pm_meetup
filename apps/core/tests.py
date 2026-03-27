"""Проверка DocsOrApiKey и OnlyWithApiKeyOrFromFrontend (без БД)."""
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, SimpleTestCase

from apps.core.permissions import DocsOrApiKey, OnlyWithApiKeyOrFromFrontend


class ApiAccessProtectionTests(SimpleTestCase):
    """Защита API: без ключа и без доверенного Origin/Referer — False; /api/docs/ и /api/schema/ — True."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = MagicMock()

    @patch("apps.core.permissions.ApiKey.objects.filter")
    def test_only_api_key_denies_without_key_or_trusted_origin(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        perm = OnlyWithApiKeyOrFromFrontend()
        request = self.factory.get("/api/v1/core/tags/")
        self.assertFalse(perm.has_permission(request, self.view))

    @patch("apps.core.permissions.ApiKey.objects.filter")
    def test_only_api_key_allows_valid_key(self, mock_filter):
        mock_filter.return_value.exists.return_value = True
        perm = OnlyWithApiKeyOrFromFrontend()
        request = self.factory.get(
            "/api/v1/core/tags/",
            HTTP_X_API_KEY="secret-key",
        )
        self.assertTrue(perm.has_permission(request, self.view))

    @patch("apps.core.permissions.ApiKey.objects.filter")
    def test_only_api_key_allows_trusted_origin(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        perm = OnlyWithApiKeyOrFromFrontend()
        request = self.factory.get(
            "/api/v1/core/tags/",
            HTTP_ORIGIN="http://localhost:3000",
        )
        self.assertTrue(perm.has_permission(request, self.view))

    @patch("apps.core.permissions.ApiKey.objects.filter")
    def test_only_api_key_allows_trusted_referer(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        perm = OnlyWithApiKeyOrFromFrontend()
        request = self.factory.get(
            "/api/v1/core/tags/",
            HTTP_REFERER="http://127.0.0.1:8000/api/docs/",
        )
        self.assertTrue(perm.has_permission(request, self.view))

    def test_docs_or_api_key_always_allows_swagger_paths(self):
        perm = DocsOrApiKey()
        for path in ("/api/docs/", "/api/schema/"):
            request = self.factory.get(path)
            self.assertTrue(
                perm.has_permission(request, self.view),
                msg=f"ожидали доступ без ключа для {path!r}",
            )

    @patch("apps.core.permissions.ApiKey.objects.filter")
    def test_docs_or_api_key_delegates_for_api_paths(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        perm = DocsOrApiKey()
        request = self.factory.get("/api/v1/core/tags/")
        self.assertFalse(perm.has_permission(request, self.view))
