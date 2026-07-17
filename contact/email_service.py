from django.conf import settings
from django.core.mail import send_mail

from contact.models import ContactRequest


class EmailNotificationService:
    @staticmethod
    def send_contact_notifications(contact_request: ContactRequest) -> None:
        EmailNotificationService.send_owner_notification(contact_request)
        EmailNotificationService.send_user_copy(contact_request)

    @staticmethod
    def send_owner_notification(contact_request: ContactRequest) -> None:
        subject = f"New contact request from {contact_request.name}"
        message = (
            "A new contact request has been submitted.\n\n"
            f"Name: {contact_request.name}\n"
            f"Email: {contact_request.email}\n"
            f"Phone: {contact_request.phone}\n"
            f"Comment: {contact_request.comment}\n"
            f"AI status: {contact_request.ai_status}\n"
            f"Sentiment: {contact_request.sentiment}\n"
            f"Category: {contact_request.category}\n"
            f"Summary: {contact_request.ai_summary or '-'}\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.OWNER_EMAIL],
            fail_silently=False,
        )

    @staticmethod
    def send_user_copy(contact_request: ContactRequest) -> None:
        subject = "We received your contact request"
        message = (
            f"Hello, {contact_request.name}!\n\n"
            "Thank you for your message. We have received your request and will get back to you soon.\n\n"
            "Your comment:\n"
            f"{contact_request.comment}\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_request.email],
            fail_silently=False,
        )
