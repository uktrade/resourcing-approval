from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.urls import reverse

from dev_tools.forms import ChangeUserForm, CreateTestResourcingRequestForm


User = get_user_model()

DEV_TOOLS_ENABLED = settings.APP_ENV in ("local", "dev")


def dev_tools_context(request):
    return {
        "DEV_TOOLS_ENABLED": DEV_TOOLS_ENABLED,
    }


def check_dev_tools_enabled(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not DEV_TOOLS_ENABLED:
            raise SuspiciousOperation("Dev tools are not enabled")

        return func(*args, **kwargs)

    return wrapper


@check_dev_tools_enabled
def index(request):
    context = {
        "change_user_form": ChangeUserForm(initial={"user": request.user.pk}),
        "create_test_resourcing_request_form": CreateTestResourcingRequestForm(),
    }

    return render(request, "dev_tools/index.html", context=context)


@check_dev_tools_enabled
def change_user(request):
    form = ChangeUserForm(data=request.POST)

    if not form.is_valid():
        raise ValidationError("Invalid change user form")

    if form.cleaned_data["user"]:
        new_user = User.objects.get(pk=form.cleaned_data["user"])

        login(request, new_user)
    else:
        logout(request)

    return redirect(reverse("dev_tools:index"))


# TODO: Come up with a mechanism to have project specific dev tools kept out of the
# dev_tools app.
@check_dev_tools_enabled
def create_test_resourcing_request(request):
    form = CreateTestResourcingRequestForm(data=request.POST)

    if not form.is_valid():
        raise ValidationError("Invalid create test resourcing request form")

    call_command(
        "create_test_resourcing_request",
        **form.cleaned_data,
    )

    return redirect(reverse("dev_tools:index"))
