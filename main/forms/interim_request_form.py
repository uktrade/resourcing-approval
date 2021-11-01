from django import forms
from django.urls import reverse_lazy

from chartofaccount.models import Directorate, DepartmentalGroup, CostCentre
from main.models import (
    InterimRequest,
)


class InterimRequestForm(forms.ModelForm):
    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput,
                   "group": forms.Select(
                       attrs={
                           'hx-get': reverse_lazy("htmx-load-directorates"),
                           "hx-target":"#id_directorate",
                       }
                   ),
                   "directorate": forms.Select(
                       attrs={
                           'hx-get': reverse_lazy("htmx-load-costcentres"),
                           "hx-target":"#id_cost_centre_code",
                       }
                   ),
                   }

    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get("end_date")
        start_date = cleaned_data.get("start_date")

        if end_date and start_date:
            # Only do something if both fields are valid so far.
            if start_date >= end_date:
                msg = "Start date cannot be after end date."
                self.add_error("end_date", msg)

        # The following checks that we have not select cost centres or groups or directorates
        # not related to each other.
        # It may never happen, but I'll rather check it.
        group = cleaned_data.get("group")
        directorate = cleaned_data.get("directorate")
        cost_centre_code = cleaned_data.get("cost_centre_code")

        if cost_centre_code and directorate:
            correct_directorate = CostCentre.objects.get(cost_centre_code=cost_centre_code).directorate
            if directorate != correct_directorate:
                msg = "The selected Cost Centre is not part of the selected Directorate"
                self.add_error("cost_centre_code", msg)

        if directorate and group:
            correct_group = Directorate.objects.get(directorate= directorate).group
            if group != correct_group:
                msg = "The selected Directorate is not part of the selected Group"
                self.add_error("directorate", msg)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True

        if 'group' in self.data:
            try:
                group_code  = self.data.get('group')
                self.fields['directorate'].queryset = \
                    Directorate.objects.filter(group=group_code).order_by('directorate_name')
            except (ValueError, TypeError):
                pass
            if "directorate" in self.data:
                try:
                    directorate_code = self.data.get('directorate')
                    self.fields['cost_centre_code'].queryset = \
                        CostCentre.objects.filter(directorate=directorate_code).order_by('cost_centre_name')
                except (ValueError, TypeError):
                    pass
            else:
                self.fields["cost_centre_code"].queryset = CostCentre.objects.none()
        elif self.instance.pk:
            self.fields['directorate'].queryset = self.instance.group.directorates.order_by('directorate_name')
            self.fields['cost_centre_code'].queryset = self.instance.directorate.cost_centres.order_by('cost_centre_name')
        else:
            self.fields["cost_centre_code"].queryset = CostCentre.objects.none()
            self.fields["directorate"].queryset = Directorate.objects.none()
