from django.urls import path

from dev_tools.views import change_user, create_test_resourcing_request, index


app_name = "dev_tools"

urlpatterns = [
    path("", index, name="index"),
    path("change-user", change_user, name="change-user"),
    path(
        "create-test-resourcing-request",
        create_test_resourcing_request,
        name="create-test-resourcing-request",
    ),
]
