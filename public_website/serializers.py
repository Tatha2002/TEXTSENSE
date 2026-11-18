
from rest_framework import serializers
from .models import ContactMessage, NewsletterSubscriber


class ContactMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMessage
        fields = ['id', 'full_name', 'email', 'company', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Full name is required.")
        return value.strip()

    def validate_subject(self, value):
        if not value.strip():
            raise serializers.ValidationError("Subject is required.")
        return value.strip()

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message is required.")
        return value.strip()


class NewsletterSubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'source', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at']

    def validate_email(self, value):
        return value.strip().lower()
