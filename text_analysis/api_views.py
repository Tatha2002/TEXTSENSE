import logging
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from feedback.models import Feedback
from .services import analyze_and_save_feedback
# from .serializers import TextAnalysisSerializer

logger = logging.getLogger(__name__)


class TextAnalysisPredictAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        feedback_id = request.data.get("feedback_id")

        if not feedback_id:
            return Response(
                {"error": "feedback_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        feedback = get_object_or_404(Feedback, id=feedback_id)
        user = request.user

        is_admin = (user.is_superuser or user.role in ["SUPER_USER", "REACT_ADMIN"])

        if not is_admin and feedback.user_id != user.id:
            return Response(
                {"error": "You cannot analyze another user's feedback"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            result = analyze_and_save_feedback(feedback)
            return Response(
                {
                    "message": "Feedback analyzed successfully",
                    "feedback_id": feedback.id,
                    "analysis": result,
                },
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("Text analysis failed for feedback ID %s",feedback.id)

            return Response(
                {
                    "error": "Unable to analyze feedback. Please try again."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )