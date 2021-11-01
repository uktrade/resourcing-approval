from django import forms
from django.core.exceptions import ValidationError

from chartofaccount.models import Directorate, DepartmentalGroup, CostCentre
from main.models import (
    InterimRequest,
)


class InterimRequestForm(forms.ModelForm):
    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput,
                   }

    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get("end_date")
        start_date = cleaned_data.get("start_date")

        if end_date and start_date:
            # Only do something if both fields are valid so far.
            if start_date >= end_date:
                # raise ValidationError(
                #     "Start date cannot be after end date."
                # )
                msg = "Start date cannot be after end date."
                self.add_error("end_date", msg)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


        if 'group' in self.data:
            try:
                group_code  = self.data.get('group')
                print(f"group_code {group_code}")
                # print(f"-------- {self.cleaned_data}")

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
