from django.urls import path
from .api_views import RegisterAPIView, LoginAPIView, TestAuthAPIView, RefreshAPIView, LogoutAPIView, ForgotPasswordAPIView, VerifyResetOTPAPIView, ResetPasswordAPIView


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("test-auth/", TestAuthAPIView.as_view(), name="test_auth"),
    path("refresh/", RefreshAPIView.as_view(), name="refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),

    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("verify-reset-otp/", VerifyResetOTPAPIView.as_view(), name="verify-reset-otp"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password",),
]



# POST http://127.0.0.1:8000/textsense/register/
# POST http://127.0.0.1:8000/textsense/login/
# GET http://127.0.0.1:8000/textsense/test-auth/
# POST http://127.0.0.1:8000/textsense/logout/
# POST http://127.0.0.1:8000/textsense/refresh/

# POST http://127.0.0.1:8000/textsense/forgot-password/
# POST http://127.0.0.1:8000/textsense/verify-reset-otp/
# POST http://127.0.0.1:8000/textsense/reset-password/


