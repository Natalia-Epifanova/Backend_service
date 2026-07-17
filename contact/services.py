import logging

from contact.ai_service import AIAnalysisService
from contact.email_service import EmailNotificationService
from contact.models import ContactRequest

logger = logging.getLogger("project.errors")


class ContactRequestService:
    @staticmethod
    def create_contact_request(validated_data: dict) -> ContactRequest:
        contact_request = ContactRequest.objects.create(**validated_data)

        try:
            ai_result = AIAnalysisService.analyze_comment(contact_request.comment)
            contact_request.sentiment = ai_result["sentiment"]
            contact_request.category = ai_result["category"]
            contact_request.ai_summary = ai_result["summary"]
            contact_request.ai_status = ContactRequest.AIStatusChoices.SUCCESS
            contact_request.ai_error = ""
            contact_request.save(
                update_fields=["sentiment", "category", "ai_summary", "ai_status", "ai_error"]
            )
        except Exception as exc:
            AIAnalysisService.apply_fallback(contact_request, str(exc))

        try:
            EmailNotificationService.send_contact_notifications(contact_request)
        except Exception as exc:
            logger.warning(
                "Failed to send contact notifications",
                extra={
                    "contact_request_id": contact_request.id,
                    "email": contact_request.email,
                    "exception": str(exc),
                },
            )

        return contact_request
