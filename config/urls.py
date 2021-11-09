from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", include("main.urls")),
    path("auth/", include("authbroker_client.urls")),
    path("dev-tools/", include("dev_tools.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    # Remove admin login page.
    path("admin/login/", RedirectView.as_view(url=settings.LOGIN_URL)),
    # Remove admin set password page.
    path(
        "admin/user/user/<int:user_id>/password/",
        RedirectView.as_view(url=reverse_lazy("index")),
    ),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
