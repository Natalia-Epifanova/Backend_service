from contact.ai_service import AIAnalysisService
from contact.email_service import EmailNotificationService
from contact.models import ContactRequest


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
        except Exception:
            pass

        return contact_request
