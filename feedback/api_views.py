from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Feedback
from .serializers import FeedbackSerializer
# from categories.permissions import IsTextSenseAdmin
from django.db import transaction

from notifications.services import create_notification
from text_analysis.services import analyze_and_save_feedback



class FeedbackListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_superuser or user.role in ["SUPER_USER", "REACT_ADMIN"]:
            feedbacks = Feedback.objects.all().order_by("-created_at")
        else:
            feedbacks = Feedback.objects.filter(user=user).order_by("-created_at")

        serializer: FeedbackSerializer = FeedbackSerializer(feedbacks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


    # def post(self, request):
    #     serializer = FeedbackSerializer(data=request.data)

    #     if not serializer.is_valid():
    #         return Response(
    #             serializer.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     feedback = serializer.save(user=request.user)

    #     return Response(
    #         {
    #             "message": "Feedback submitted successfully",
    #             "feedback": FeedbackSerializer(feedback).data
    #         },
    #         status=status.HTTP_201_CREATED
    #     )


    def post(self, request, *args, **kwargs):

        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():

            feedback = serializer.save(user=request.user)

            # Create feedback submission notification
            create_notification(
                user=request.user,
                message="Your feedback was submitted successfully.",
                notification_type="FEEDBACK_SUBMITTED"
            )

            # Keep your existing NLP analysis call here
            analyze_and_save_feedback(feedback)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )



class FeedbackDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Feedback.objects.get(pk=pk)
        except Feedback.DoesNotExist:
            return None

    def get(self, request, pk):
        feedback = self.get_object(pk)

        if feedback is None:
            return Response(
                {"error": "Feedback not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        is_admin = (request.user.is_superuser or request.user.role in ["SUPER_USER", "REACT_ADMIN"])

        if not is_admin and feedback.user != request.user:
            return Response(
                {"error": "You do not have permission to view this feedback"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = FeedbackSerializer(feedback)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # def patch(self, request, pk):

    #     is_admin = (
    #         request.user.is_superuser
    #         or request.user.role in ["SUPER_USER", "REACT_ADMIN"]
    #     )

    #     if not is_admin:
    #         return Response(
    #             {"error": "Only admins can update feedback"},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

    #     feedback = self.get_object(pk)

    #     if feedback is None:
    #         return Response(
    #             {"error": "Feedback not found"},
    #             status=status.HTTP_404_NOT_FOUND
    #         )

    #     # Admin can update the status only.
    #     allowed_fields = {"status"}

    #     if not set(request.data.keys()).issubset(allowed_fields):
    #         return Response(
    #             {"error": "Only status can be updated here"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     serializer = FeedbackSerializer(feedback, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk):

        is_admin = (
            request.user.is_superuser
            or request.user.role in ["SUPER_USER", "REACT_ADMIN"]
        )

        if not is_admin:
            return Response(
                {"error": "Only admins can update feedback"},
                status=status.HTTP_403_FORBIDDEN
            )

        feedback = self.get_object(pk)

        if feedback is None:
            return Response(
                {"error": "Feedback not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Admin can update the status only.
        allowed_fields = {"status"}

        if not set(request.data.keys()).issubset(allowed_fields):
            return Response(
                {"error": "Only status can be updated here"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store previous status
        old_status = feedback.status

        serializer = FeedbackSerializer(
            feedback,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            updated_feedback = serializer.save()

            # Generate notification only if status changes
            if old_status != updated_feedback.status:

                create_notification(
                    user=updated_feedback.user,
                    message=f"Your feedback status has been updated to {updated_feedback.status}.",
                    notification_type="ADMIN_UPDATE"
                )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


