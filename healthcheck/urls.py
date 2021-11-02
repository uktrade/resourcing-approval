from django.urls import path

from .views import healthcheck


app_name = "healthcheck"

urlpatterns = [
    path("", healthcheck, name="index"),
]
