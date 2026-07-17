from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
