from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView

from contact.metrics_service import ContactMetricsService
from contact.rate_limit import ContactRateLimitService
from contact.serializers import ContactRequestSerializer


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ContactCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        client_ip = request.META.get("REMOTE_ADDR", "")
        is_allowed, wait_seconds = ContactRateLimitService.check_request_allowed(
            ip_address=client_ip,
            limit=settings.CONTACT_RATE_LIMIT_REQUESTS,
            window_seconds=settings.CONTACT_RATE_LIMIT_WINDOW_SECONDS,
        )

        if not is_allowed:
            raise Throttled(wait=wait_seconds, detail="Too many contact requests. Please try again later.")

        serializer = ContactRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_request = serializer.save()

        return Response(
            {
                "message": "Contact request created successfully.",
                "id": contact_request.id,
                "ai_status": contact_request.ai_status,
            },
            status=status.HTTP_201_CREATED,
        )


class MetricsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(ContactMetricsService.get_metrics(), status=status.HTTP_200_OK)
