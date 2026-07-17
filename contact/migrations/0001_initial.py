from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=32)),
                ("email", models.EmailField(max_length=254)),
                ("comment", models.TextField(max_length=2000)),
                (
                    "sentiment",
                    models.CharField(
                        choices=[
                            ("positive", "Positive"),
                            ("neutral", "Neutral"),
                            ("negative", "Negative"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        max_length=16,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("project", "Project"),
                            ("consultation", "Consultation"),
                            ("partnership", "Partnership"),
                            ("job", "Job"),
                            ("other", "Other"),
                            ("unclassified", "Unclassified"),
                        ],
                        default="unclassified",
                        max_length=32,
                    ),
                ),
                (
                    "ai_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("fallback", "Fallback"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("ai_summary", models.TextField(blank=True)),
                ("ai_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Contact request",
                "verbose_name_plural": "Contact requests",
                "ordering": ["-created_at"],
            },
        ),
    ]
