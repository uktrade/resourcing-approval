from django.urls import path

from dev_tools.views import change_user, index


app_name = "dev_tools"

urlpatterns = [
    path("", index, name="index"),
    path("change-user", change_user, name="change-user"),
]
