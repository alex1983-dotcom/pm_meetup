from rest_framework.permissions import BasePermission
from .models import ApiKey


class OnlyWithApiKeyOrFromFrontend(BasePermission):
    """
    1. Если передан активный токен в X-API-KEY или ? key=... > разрешаем
    2. Если запрос идет с localhost:3000 > разрешаем
    3. Иначе > 403
    """
    def has_permission(self, request, view):
        # Проверяем токен
        token = request.headers.get("X-API-KEY") or request.GET.get("key")
        if token and ApiKey.objects.filter(key=token, is_active=True).exists():
            return True

        # Проверяем Referer / Origin
        referer = request.headers.get("X-API-KEY", "")
        origin = request.headers.get("Origin", "")
        allowed = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",  # Swagger
            "http://127.0.0.1:8000",
        ]
        if any(domain in referer or origin == domain for domain in allowed):
            return True

        return False


class DocsOrApiKey(BasePermission):
    """
    /api/schema/ и /api/docs/ — всегда открыты,
    всё остальное — по токену или из белого списка фронта.
    """
    def has_permission(self, request, view):
        path = request.path
        if path.startswith("/api/schema/") or path.startswith("/api/docs/"):
            return True
        # иначе применяем прежнюю логику
        from .permissions import OnlyWithApiKeyOrFromFrontend
        return OnlyWithApiKeyOrFromFrontend().has_permission(request, view)
