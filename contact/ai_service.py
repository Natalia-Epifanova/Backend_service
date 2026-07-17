import json
import os

from openai import OpenAI

from contact.models import ContactRequest


class AIAnalysisService:
    """Сервис анализа комментария через AI-провайдера."""

    DEFAULT_MODEL = "gpt-4.1-mini"

    @classmethod
    def analyze_comment(cls, comment: str) -> dict:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", cls.DEFAULT_MODEL)

        if not api_key:
            raise ValueError("OPENAI_API_KEY не настроен.")

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You analyze contact form messages. "
                        "Return only valid JSON with keys: sentiment, category, summary. "
                        "Allowed sentiment values: positive, neutral, negative. "
                        "Allowed category values: project, consultation, partnership, job, other. "
                        "The summary must be one short sentence."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Comment: {comment}",
                },
            ],
        )
        payload = json.loads(response.output_text)

        return {
            "sentiment": payload["sentiment"],
            "category": payload["category"],
            "summary": payload["summary"],
        }

    @staticmethod
    def apply_fallback(contact_request: ContactRequest, error_message: str) -> ContactRequest:
        contact_request.sentiment = ContactRequest.SentimentChoices.UNKNOWN
        contact_request.category = ContactRequest.CategoryChoices.UNCLASSIFIED
        contact_request.ai_status = ContactRequest.AIStatusChoices.FALLBACK
        contact_request.ai_summary = ""
        contact_request.ai_error = error_message
        contact_request.save(
            update_fields=["sentiment", "category", "ai_status", "ai_summary", "ai_error"]
        )
        return contact_request
