
from django.conf import settings
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK

from .serializers import ContactMessageSerializer, NewsletterSubscriberSerializer

from .serializers import NewsletterSubscriberSerializer
from .models import NewsletterSubscriber, ContactMessage


class ContactMessageAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)

        if serializer.is_valid():
            contact = serializer.save()

            try:
                send_mail(
                    subject=f"New Contact Message: {contact.subject}",
                    message=(
                        f"Name: {contact.full_name}\n"
                        f"Email: {contact.email}\n"
                        f"Company: {contact.company or 'Not provided'}\n"
                        f"Subject: {contact.subject}\n\n"
                        f"Message:\n{contact.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.SUPPORT_EMAIL],
                    fail_silently=False,
                )
            except Exception:
                pass

            return Response({
                "success": True,
                "message": "Your message has been submitted successfully.",
                "data": serializer.data
            }, status=HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=HTTP_400_BAD_REQUEST)



class NewsletterSubscriberAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NewsletterSubscriberSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            subscriber = NewsletterSubscriber.objects.filter(email__iexact=email).first()

            if subscriber:
                return Response({
                    "success": True,
                    "message": "You are already subscribed."
                }, status=HTTP_200_OK)

            serializer.save()

            return Response({
                "success": True,
                "message": "You have successfully subscribed to our newsletter."
            }, status=HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=HTTP_400_BAD_REQUEST)
