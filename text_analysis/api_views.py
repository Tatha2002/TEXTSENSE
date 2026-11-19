import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from categories.permissions import IsTextSenseAdmin
from feedback.models import Feedback
from .services import analyze_and_save_feedback, get_analysis_result
from notifications.services import create_notification

from text_analysis.models import TextAnalysis
from .serializers import TextAnalysisSerializer

logger = logging.getLogger(__name__)


class TextAnalysisPredictAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTextSenseAdmin]

    def post(self, request):

        # 1. Accept feedback ID
        feedback_id = request.data.get("feedback_id")

        if not feedback_id:
            return Response(
                {"success": False, "message": "feedback_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            feedback_id = int(feedback_id)
        except (ValueError, TypeError):
            return Response(
                {"success": False, "message": "Invalid feedback_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Check whether feedback exists
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return Response(
                {"success": False, "message": "Feedback not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Check user permission
        user = request.user
        is_admin = user.is_superuser or user.role in ["SUPER_USER", "REACT_ADMIN"]

        if not is_admin and feedback.user_id != user.id:
            return Response(
                {"success": False, "message": "You cannot analyze another user's feedback."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 4. Run analysis or return existing analysis
        try:
            result = analyze_and_save_feedback(feedback)

            try:
                create_notification(
                    user=feedback.user,
                    title="Feedback Analysis Completed",
                    message="Your feedback analysis has been completed successfully.",
                    notification_type="ANALYSIS_COMPLETED",
                    category="ANALYSIS",
                    priority="MEDIUM",
                    reference_id=str(feedback.id)
                )
            except Exception:
                logger.exception("Notification creation failed for feedback ID %s", feedback.id)

            return Response(
                {
                    "success": True,
                    "message": "Analysis completed successfully.",
                    "data": result
                },
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("Text analysis failed for feedback ID %s", feedback.id)

            return Response(
                {
                    "success": False,
                    "message": "Unable to analyze feedback. Please try again."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )



class TextAnalysisResultAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, feedback_id):

        # 1. Check whether feedback exists
        try:
            feedback = Feedback.objects.get(id=feedback_id)

        except Feedback.DoesNotExist:
            return Response(
                {
                    "error": "Feedback not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Check user permission
        user = request.user

        is_admin = (
            user.is_superuser
            or user.role in ["SUPER_USER", "REACT_ADMIN"]
        )

        if not is_admin and feedback.user_id != user.id:
            return Response(
                {
                    "error": "You do not have permission to view this analysis."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Retrieve existing analysis
        try:
            analysis = TextAnalysis.objects.get(feedback=feedback)

        except TextAnalysis.DoesNotExist:
            return Response(
                {
                    "error": "Analysis not available yet.",
                    "code": "analysis_pending"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. Serialize stored analysis
        result = get_analysis_result(analysis)

        return Response(
            {
                "success": True,
                "message": "Analysis fetched successfully.",
                "data": result
            },
            status=status.HTTP_200_OK
        )
