import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("project.errors")


def custom_exception_handler(exc, context):
    """Преобразует исключения DRF в единый API-ответ."""

    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            wait_seconds = getattr(exc, "wait", None)
            detail = "Слишком много обращений. Попробуйте позже."
            if wait_seconds is not None:
                detail = f"{detail} Повторите попытку через {int(wait_seconds)} сек."
            response.data = {"detail": detail}

        logger.warning(
            "Handled API exception",
            extra={
                "path": getattr(context.get("request"), "path", ""),
                "method": getattr(context.get("request"), "method", ""),
                "status_code": response.status_code,
                "exception": str(exc),
            },
        )
        return response

    request = context.get("request")
    logger.exception(
        "Unhandled API exception",
        extra={
            "path": getattr(request, "path", ""),
            "method": getattr(request, "method", ""),
        },
    )

    return Response(
        {"detail": "Внутренняя ошибка сервера."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
