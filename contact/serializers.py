import re

from rest_framework import serializers

from contact.models import ContactRequest


class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = ("name", "phone", "email", "comment")

    def validate_name(self, value: str) -> str:
        cleaned_value = value.strip()

        if len(cleaned_value) < 2:
            raise serializers.ValidationError("Name must contain at least 2 characters.")

        return cleaned_value

    def validate_phone(self, value: str) -> str:
        cleaned_value = value.strip()
        normalized_value = re.sub(r"[^\d+]", "", cleaned_value)
        digits_only = re.sub(r"\D", "", normalized_value)

        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must contain at least 10 digits.")

        if len(digits_only) > 15:
            raise serializers.ValidationError("Phone number must contain no more than 15 digits.")

        if normalized_value.count("+") > 1 or ("+" in normalized_value and not normalized_value.startswith("+")):
            raise serializers.ValidationError("Phone number format is invalid.")

        return cleaned_value

    def validate_comment(self, value: str) -> str:
        cleaned_value = value.strip()

        if len(cleaned_value) < 10:
            raise serializers.ValidationError("Comment must contain at least 10 characters.")

        return cleaned_value
