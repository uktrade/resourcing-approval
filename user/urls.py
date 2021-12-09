from django.urls import path

from user.views import EditUserView


app_name = "user"

urlpatterns = [
    path("<int:pk>/edit", EditUserView.as_view(), name="edit-user"),
]
