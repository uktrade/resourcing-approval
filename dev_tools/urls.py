from django.urls import path

from dev_tools.views import index, change_user


urlpatterns = [
    path("", index, name="dev-tools"),
    path("change-user", change_user, name="change-user"),
]
