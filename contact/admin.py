from django.contrib import admin

from contact.models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "category", "sentiment", "ai_status", "created_at")
    list_filter = ("category", "sentiment", "ai_status", "created_at")
    search_fields = ("name", "email", "phone", "comment")
    readonly_fields = ("created_at",)
