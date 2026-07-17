import re

from rest_framework import serializers

from contact.models import ContactRequest
from contact.services import ContactRequestService


class ContactRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для валидации формы обратной связи."""

    class Meta:
        model = ContactRequest
        fields = ("name", "phone", "email", "comment")

    def create(self, validated_data: dict) -> ContactRequest:
        return ContactRequestService.create_contact_request(validated_data)

    def validate_name(self, value: str) -> str:
        cleaned_value = value.strip()

        if len(cleaned_value) < 2:
            raise serializers.ValidationError("Имя должно содержать минимум 2 символа.")

        return cleaned_value

    def validate_phone(self, value: str) -> str:
        cleaned_value = value.strip()
        normalized_value = re.sub(r"[^\d+]", "", cleaned_value)
        digits_only = re.sub(r"\D", "", normalized_value)

        if len(digits_only) < 10:
            raise serializers.ValidationError("Телефон должен содержать минимум 10 цифр.")

        if len(digits_only) > 15:
            raise serializers.ValidationError("Телефон должен содержать не более 15 цифр.")

        if normalized_value.count("+") > 1 or ("+" in normalized_value and not normalized_value.startswith("+")):
            raise serializers.ValidationError("Неверный формат телефона.")

        return cleaned_value

    def validate_comment(self, value: str) -> str:
        cleaned_value = value.strip()

        if len(cleaned_value) < 10:
            raise serializers.ValidationError("Комментарий должен содержать минимум 10 символов.")

        return cleaned_value
