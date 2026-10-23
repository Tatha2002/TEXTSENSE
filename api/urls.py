from django.urls import path
from .api_views import RegisterAPIView, LoginAPIView, TestAuthAPIView, RefreshAPIView, LogoutAPIView


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("test-auth/", TestAuthAPIView.as_view(), name="test_auth"),
    path("refresh/", RefreshAPIView.as_view(), name="refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]



# POST http://127.0.0.1:8000/api/register/
# POST http://127.0.0.1:8000/api/login/
# GET http://127.0.0.1:8000/api/test-auth/
# POST http://127.0.0.1:8000/api/logout/
# GET http://127.0.0.1:8000/api/refresh/