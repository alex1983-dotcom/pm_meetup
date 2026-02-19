import pathlib
from django.conf import settings

_cleanup_done = False

class LogCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _cleanup_done
        if not _cleanup_done:
            _cleanup_done = True
            for h in ('file', 'drf_file'):
                pathlib.Path(settings.LOGGING['handlers'][h]['filename']).unlink(missing_ok=True)
        return self.get_response(request)
    
    