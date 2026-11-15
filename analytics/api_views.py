from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from categories.permissions import IsTextSenseAdmin
from .services import get_dashboard_analytics


class AdminAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTextSenseAdmin]

    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        data = get_dashboard_analytics(date_from=date_from, date_to=date_to)

        return Response({
            "message": "Analytics fetched successfully",
            "analytics": data
        })
