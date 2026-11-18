
from django.urls import path
from .api_views import ContactMessageAPIView, NewsletterSubscriberAPIView

urlpatterns = [
    path('contact/', ContactMessageAPIView.as_view(), name='contact'),
    path('newsletter/subscribe/', NewsletterSubscriberAPIView.as_view(), name='contact'),
]



# POST	http://127.0.0.1:8000/contact/
# POST	http://127.0.0.1:8000/newsletter/subscribe/