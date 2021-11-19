from django.forms import widgets

from main.forms.forms import FormWithStartEndDates
from main.models import InterimRequest


class InterimRequestNewForm(FormWithStartEndDates):
    date_error_msg = "Anticipated end date cannot be before anticipated start date"

    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
