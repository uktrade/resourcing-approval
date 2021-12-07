from django import forms
from django.contrib.auth import get_user_model

from main.models import TRUE_FALSE_CHOICES


User = get_user_model()


def get_user_choices():
    return [
        (None, "AnonymousUser"),
        *[(x.id, str(x)) for x in User.objects.all()],
    ]


class ChangeUserForm(forms.Form):
    user = forms.ChoiceField(choices=get_user_choices, required=False)


class CreateTestResourcingRequestForm(forms.Form):
    job_title = forms.CharField()
    project_name = forms.CharField()
    inside_ir35 = forms.ChoiceField(choices=TRUE_FALSE_CHOICES)
