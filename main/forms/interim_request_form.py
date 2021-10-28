from django import forms

from chartofaccount.models import Directorate, DepartmentalGroup, CostCentre
from main.models import (
    InterimRequest,
)


class InterimRequestForm(forms.ModelForm):
    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
        self.fields["cost_centre_code"].queryset = CostCentre.objects.none()
        self.fields["directorate"].queryset = Directorate.objects.none()