from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from TEXTSENSE import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('accounts/', include('accounts.urls')),
    path('textsense/auth/', include('api.urls')),
    path('textsense/category/', include('categories.urls')),
    path("textsense/feedback/", include("feedback.urls")),
    path("textsense/text-analysis/", include("text_analysis.urls")),
    path("textsense/admin/", include("analytics.urls")),
    path("textsense/content/", include("content.urls")),
    path("textsense/notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)