from django.urls import path

from contact.views import ContactCreateView, HealthCheckView

urlpatterns = [
    path("contact/", ContactCreateView.as_view(), name="contact-create"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
