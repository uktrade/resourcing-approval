from django.contrib import admin
from django.urls import include, path
from django_workflow_engine import workflow_urls

urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
    path("workflow/", workflow_urls()),
]
