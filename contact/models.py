from django.db import models


class ContactRequest(models.Model):
    class SentimentChoices(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEUTRAL = "neutral", "Neutral"
        NEGATIVE = "negative", "Negative"
        UNKNOWN = "unknown", "Unknown"

    class CategoryChoices(models.TextChoices):
        PROJECT = "project", "Project"
        CONSULTATION = "consultation", "Consultation"
        PARTNERSHIP = "partnership", "Partnership"
        JOB = "job", "Job"
        OTHER = "other", "Other"
        UNCLASSIFIED = "unclassified", "Unclassified"

    class AIStatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FALLBACK = "fallback", "Fallback"
        FAILED = "failed", "Failed"

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    comment = models.TextField(max_length=2000)
    sentiment = models.CharField(
        max_length=16,
        choices=SentimentChoices.choices,
        default=SentimentChoices.UNKNOWN,
    )
    category = models.CharField(
        max_length=32,
        choices=CategoryChoices.choices,
        default=CategoryChoices.UNCLASSIFIED,
    )
    ai_status = models.CharField(
        max_length=16,
        choices=AIStatusChoices.choices,
        default=AIStatusChoices.PENDING,
    )
    ai_summary = models.TextField(blank=True)
    ai_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact request"
        verbose_name_plural = "Contact requests"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
