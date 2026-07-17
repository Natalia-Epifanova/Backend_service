from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from contact.models import ContactRequest


@override_settings(
    CONTACT_RATE_LIMIT_REQUESTS=3,
    CONTACT_RATE_LIMIT_WINDOW_SECONDS=60,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ContactApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.contact_payload = {
            "name": "Анна Иванова",
            "phone": "+7 (999) 123-45-67",
            "email": "anna@example.com",
            "comment": "Хочу обсудить backend-проект и интеграцию AI.",
        }

    def test_healthcheck_returns_ok(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("contact.services.EmailNotificationService.send_contact_notifications")
    @patch("contact.services.AIAnalysisService.analyze_comment")
    def test_create_contact_request_success(self, mock_analyze_comment, mock_send_notifications):
        mock_analyze_comment.return_value = {
            "sentiment": ContactRequest.SentimentChoices.POSITIVE,
            "category": ContactRequest.CategoryChoices.PROJECT,
            "summary": "Клиент хочет обсудить backend-проект.",
        }

        response = self.client.post("/api/contact/", self.contact_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["message"], "Обращение успешно создано.")
        self.assertEqual(response.json()["ai_status"], ContactRequest.AIStatusChoices.SUCCESS)
        self.assertEqual(ContactRequest.objects.count(), 1)

        contact_request = ContactRequest.objects.get()
        self.assertEqual(contact_request.sentiment, ContactRequest.SentimentChoices.POSITIVE)
        self.assertEqual(contact_request.category, ContactRequest.CategoryChoices.PROJECT)
        self.assertEqual(contact_request.ai_status, ContactRequest.AIStatusChoices.SUCCESS)
        self.assertEqual(contact_request.ai_summary, "Клиент хочет обсудить backend-проект.")
        mock_send_notifications.assert_called_once()

    def test_create_contact_request_validation_error(self):
        invalid_payload = {
            "name": "A",
            "phone": "123",
            "email": "invalid-email",
            "comment": "short",
        }

        response = self.client.post("/api/contact/", invalid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())
        self.assertIn("phone", response.json())
        self.assertIn("email", response.json())
        self.assertIn("comment", response.json())
        self.assertEqual(response.json()["name"][0], "Имя должно содержать минимум 2 символа.")
        self.assertEqual(response.json()["phone"][0], "Телефон должен содержать минимум 10 цифр.")
        self.assertEqual(response.json()["comment"][0], "Комментарий должен содержать минимум 10 символов.")

    @patch("contact.services.EmailNotificationService.send_contact_notifications")
    @patch("contact.services.AIAnalysisService.analyze_comment")
    def test_rate_limit_returns_429_after_limit(self, mock_analyze_comment, mock_send_notifications):
        mock_analyze_comment.side_effect = ValueError("OPENAI_API_KEY не настроен.")

        responses = [
            self.client.post("/api/contact/", self.contact_payload, format="json")
            for _ in range(4)
        ]

        self.assertEqual(responses[0].status_code, status.HTTP_201_CREATED)
        self.assertEqual(responses[1].status_code, status.HTTP_201_CREATED)
        self.assertEqual(responses[2].status_code, status.HTTP_201_CREATED)
        self.assertEqual(responses[3].status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            responses[3].json()["detail"],
            "Слишком много обращений. Попробуйте позже. Повторите попытку через 60 сек.",
        )

    @patch("contact.services.EmailNotificationService.send_contact_notifications")
    @patch("contact.services.AIAnalysisService.analyze_comment")
    def test_metrics_returns_aggregated_statistics(self, mock_analyze_comment, mock_send_notifications):
        mock_analyze_comment.side_effect = [
            {
                "sentiment": ContactRequest.SentimentChoices.POSITIVE,
                "category": ContactRequest.CategoryChoices.PROJECT,
                "summary": "Запрос по проекту.",
            },
            ValueError("OPENAI_API_KEY не настроен."),
        ]

        self.client.post("/api/contact/", self.contact_payload, format="json")
        second_payload = {
            **self.contact_payload,
            "email": "second@example.com",
            "comment": "Нужна консультация по API и архитектуре.",
        }
        self.client.post("/api/contact/", second_payload, format="json")

        response = self.client.get("/api/metrics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total_requests"], 2)
        self.assertEqual(response.json()["ai_status_breakdown"]["success"], 1)
        self.assertEqual(response.json()["ai_status_breakdown"]["fallback"], 1)
