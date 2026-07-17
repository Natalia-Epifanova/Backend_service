import json
import logging
import time

from django.http import RawPostDataException

logger = logging.getLogger("project.requests")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()
        body = ""
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = request.body.decode("utf-8")
            except (UnicodeDecodeError, RawPostDataException):
                body = "<unavailable-body>"

        response = self.get_response(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

        logger.info(
            json.dumps(
                {
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "remote_addr": request.META.get("REMOTE_ADDR", ""),
                    "duration_ms": duration_ms,
                    "body": body,
                },
                ensure_ascii=False,
            )
        )

        return response
