from django import forms
from chartofaccount.models import Directorate, CostCentre
from main.models import (
    InterimRequest,
)

from main.forms.forms import FormWithStartEndDates

class InterimRequestForm(FormWithStartEndDates):
    date_error_msg = "Anticipated end date cannot be before anticipated start date"

    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput,
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True

        # Adjust the directorate and costcentre selection
        # accordingly to selection in group
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
