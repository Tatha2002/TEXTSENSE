from django.urls import path
from .api_views import TextAnalysisPredictAPIView, TextAnalysisResultAPIView

urlpatterns = [

    path("predict/", TextAnalysisPredictAPIView.as_view(), name="text-analysis-predict"),
    path("result/<int:feedback_id>/", TextAnalysisResultAPIView.as_view(), name="text-analysis-result"),

]


# POST http://127.0.0.1:8000/textsense/text-analysis/predict/
# GET http://127.0.0.1:8000/textsense/text-analysis/result/10/
