from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Feedback
from .serializers import FeedbackSerializer, MyFeedbackSerializer, RecentFeedbackSerializer
from django.core.exceptions import ValidationError

from categories.permissions import IsTextSenseAdmin
from notifications.services import create_notification
from text_analysis.services import analyze_and_save_feedback


class FeedbackListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsTextSenseAdmin]

    def get(self, request):

        user = request.user

        is_admin = (
            user.is_superuser
            or user.role in ["SUPER_USER", "REACT_ADMIN"]
        )

        if is_admin:
            feedbacks = Feedback.objects.all()
        else:
            feedbacks = Feedback.objects.filter(user=user)

        feedbacks = feedbacks.select_related(
            "user", "category"
        ).order_by("-created_at")

        serializer = FeedbackSerializer(feedbacks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedbackCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save feedback first. Status is fixed by the backend.
        feedback = serializer.save(user=request.user, status="NEW")

        # Notification failure must not delete the feedback.
        try:
            create_notification(
                user=request.user,
                title="Feedback Submitted",
                message="Your feedback was submitted successfully.",
                notification_type="FEEDBACK_SUBMITTED",
                category="FEEDBACK",
                priority="MEDIUM",
                reference_id=str(feedback.id)
            )

        except Exception:
            pass

        # NLP failure must not delete the feedback.
        analysis_error = False

        try:
            analyze_and_save_feedback(feedback)
        except Exception:
            analysis_error = True

        response_data = FeedbackSerializer(feedback).data

        if analysis_error:
            response_data["analysis_message"] = (
                "Feedback saved successfully, but sentiment analysis "
                "could not be completed."
            )

        return Response(response_data, status=status.HTTP_201_CREATED)


class FeedbackDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Feedback.objects.select_related("user", "category").get(pk=pk)

        except Feedback.DoesNotExist:
            return None

    def get(self, request, pk):
        feedback = self.get_object(pk)

        if feedback is None:
            return Response({"error": "Feedback not found"},status=status.HTTP_404_NOT_FOUND)

        is_admin = (request.user.is_superuser or request.user.role in ["SUPER_USER", "REACT_ADMIN"])

        if not is_admin and feedback.user_id != request.user.id:
            return Response({"error": "You do not have permission to view this feedback"}, status=status.HTTP_403_FORBIDDEN)

        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):

        # Only admins can update feedback status.
        permission = IsTextSenseAdmin()

        if not permission.has_permission(request, self):
            return Response({"error": "Only admins can update feedback"}, status=status.HTTP_403_FORBIDDEN)

        feedback = self.get_object(pk)

        if feedback is None:
            return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

        if set(request.data.keys()) != {"status"}:
            return Response({"error": "Only the status field can be updated"}, status=status.HTTP_400_BAD_REQUEST)

        old_status = feedback.status
        new_status = request.data.get("status")

        valid_statuses = dict(Feedback.STATUS_CHOICES).keys()

        if new_status not in valid_statuses:
            return Response({"error": "Invalid feedback status"}, status=status.HTTP_400_BAD_REQUEST)

        feedback.status = new_status
        feedback.save(update_fields=["status"])

        if old_status != new_status:
            try:
                create_notification(
                    user=feedback.user,
                    title="Feedback Status Updated",
                    message=f"Your feedback status has been updated to {new_status}.",
                    notification_type="ADMIN_UPDATE",
                    category="FEEDBACK",
                    priority="HIGH",
                    reference_id=str(feedback.id)
                )

            except Exception:
                pass

        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):

        permission = IsTextSenseAdmin()

        if not permission.has_permission(request, self):
            return Response({"error": "Only admins can delete feedback"}, status=status.HTTP_403_FORBIDDEN)

        feedback = self.get_object(pk)

        if feedback is None:
            return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

        feedback.delete()

        return Response({"message": "Feedback deleted successfully"}, status=status.HTTP_200_OK)


class MyFeedbackAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get feedback belonging to the logged-in user
        feedbacks = Feedback.objects.filter(user=request.user).select_related("category", "analysis").order_by("-created_at")

        # Optional status filter
        status_filter = request.query_params.get("status")

        if status_filter:
            valid_statuses = dict(Feedback.STATUS_CHOICES)

            if status_filter not in valid_statuses:
                return Response(
                    {"error": "Invalid feedback status"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            feedbacks = feedbacks.filter(status=status_filter)

        # Optional search by title or text
        search = request.query_params.get("search")

        if search:
            feedbacks = feedbacks.filter(Q(title__icontains=search) | Q(text__icontains=search))

        # Serialize the feedback records
        serializer = MyFeedbackSerializer(feedbacks, many=True)

        return Response(
            {
                "message": "Feedback fetched successfully",
                "feedback": serializer.data
            }, status=status.HTTP_200_OK
        )



class MyFeedbackSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get only the logged-in user's feedback
        feedbacks = Feedback.objects.filter(user=request.user)

        # 1. Total feedback
        total_feedback = feedbacks.count()

        # 2. Count feedback according to status
        status_counts = {
            item["status"]: item["count"]
            for item in feedbacks.values("status").annotate(count=Count("id"))
        }

        # Include all available statuses, even if count is zero
        status_distribution = [
            {
                "status": status_code,
                "count": status_counts.get(status_code, 0)
            }
            for status_code, status_name in Feedback.STATUS_CHOICES
        ]

        # 3. Pending and reviewed counts
        pending_feedback = (status_counts.get("NEW", 0) + status_counts.get("PENDING", 0))

        reviewed_feedback = (status_counts.get("REVIEWED", 0) + status_counts.get("RESOLVED", 0))

        # 4. Sentiment distribution
        sentiment_counts = {
            item["analysis__sentiment"]: item["count"]
            for item in feedbacks.values("analysis__sentiment").annotate(count=Count("id"))
        }

        sentiment_distribution = {
            "Positive": sentiment_counts.get("Positive", 0),
            "Neutral": sentiment_counts.get("Neutral", 0),
            "Negative": sentiment_counts.get("Negative", 0),
            "not_analyzed": sentiment_counts.get(None, 0)
        }

        # 5. Latest 5 feedback records
        recent_feedbacks = (feedbacks.select_related("category", "analysis").order_by("-created_at")[:5])

        recent_serializer = RecentFeedbackSerializer(recent_feedbacks, many=True)

        # Final response
        return Response(
            {
                "message": "Summary fetched successfully",
                "summary": {
                    "total_feedback": total_feedback,
                    "pending_feedback": pending_feedback,
                    "reviewed_feedback": reviewed_feedback,
                    "status_distribution": status_distribution,
                    "sentiment_distribution": sentiment_distribution,
                    "recent_feedback": recent_serializer.data
                }
            }, status=status.HTTP_200_OK
        )
