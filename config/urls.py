from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("main.urls")),
    path("dev-tools/", include("dev_tools.urls")),
    path("admin/", admin.site.urls),
]
