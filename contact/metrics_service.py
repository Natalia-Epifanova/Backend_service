from django.db.models import Count

from contact.models import ContactRequest


class ContactMetricsService:
    @staticmethod
    def get_metrics() -> dict:
        total_requests = ContactRequest.objects.count()
        ai_status_counts = ContactRequest.objects.values("ai_status").annotate(count=Count("id"))
        category_counts = ContactRequest.objects.values("category").annotate(count=Count("id"))
        sentiment_counts = ContactRequest.objects.values("sentiment").annotate(count=Count("id"))

        return {
            "total_requests": total_requests,
            "ai_status_breakdown": {
                item["ai_status"]: item["count"] for item in ai_status_counts
            },
            "category_breakdown": {
                item["category"]: item["count"] for item in category_counts
            },
            "sentiment_breakdown": {
                item["sentiment"]: item["count"] for item in sentiment_counts
            },
        }
