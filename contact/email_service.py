from django.conf import settings
from django.core.mail import send_mail

from contact.models import ContactRequest


class EmailNotificationService:
    """Сервис отправки email-уведомлений по обращению."""

    @staticmethod
    def send_contact_notifications(contact_request: ContactRequest) -> None:
        EmailNotificationService.send_owner_notification(contact_request)
        EmailNotificationService.send_user_copy(contact_request)

    @staticmethod
    def send_owner_notification(contact_request: ContactRequest) -> None:
        subject = f"Новое обращение от {contact_request.name}"
        message = (
            "Поступило новое обращение.\n\n"
            f"Имя: {contact_request.name}\n"
            f"Email: {contact_request.email}\n"
            f"Телефон: {contact_request.phone}\n"
            f"Комментарий: {contact_request.comment}\n"
            f"Статус AI: {contact_request.ai_status}\n"
            f"Тональность: {contact_request.sentiment}\n"
            f"Категория: {contact_request.category}\n"
            f"Краткое резюме: {contact_request.ai_summary or '-'}\n"
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
        subject = "Мы получили ваше обращение"
        message = (
            f"Здравствуйте, {contact_request.name}!\n\n"
            "Спасибо за ваше сообщение. Мы получили обращение и свяжемся с вами в ближайшее время.\n\n"
            "Ваш комментарий:\n"
            f"{contact_request.comment}\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_request.email],
            fail_silently=False,
        )
