from django import forms
from django.urls import reverse_lazy

from main.models import (
    InterimRequest,
)
from main.forms.forms import FormWithStartEndDates
from main.utils import syncronise_cost_centre_dropdowns

class InterimRequestForm(FormWithStartEndDates):
    date_error_msg = "Anticipated end date cannot be before anticipated start date"

    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {
            "resourcing_request": forms.HiddenInput,
            "group": forms.Select(
                attrs={
                    "hx-get": reverse_lazy("htmx-load-directorates"),
                    "hx-target": "#id_directorate",
                }
            ),
            "directorate": forms.Select(
                attrs={
                    "hx-get": reverse_lazy("htmx-load-costcentres"),
                    "hx-target": "#id_cost_centre_code",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
        syncronise_cost_centre_dropdowns(self)
