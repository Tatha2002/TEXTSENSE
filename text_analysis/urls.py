from django.urls import path
from .api_views import TextAnalysisPredictAPIView

urlpatterns = [

    path("predict/", TextAnalysisPredictAPIView.as_view(), name="text-analysis-predict"),

]


# POST http://127.0.0.1:8000/textsense/text-analysis/predict/
