from django import forms
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from main.models import (
    CestDocument,
    FinancialInformation,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)
from main.utils import syncronise_cost_centre_dropdowns


class FormWithStartEndDates(forms.ModelForm):
    start_date_field = "start_date"
    end_date_field = "end_date"
    date_error_msg = "End date cannot be before start date"

    def clean(self):
        cleaned_data = super().clean()

        end_date = cleaned_data.get(self.end_date_field)
        start_date = cleaned_data.get(self.start_date_field)

        if end_date and start_date:
            # Only do something if both fields are valid so far.
            if start_date >= end_date:
                self.add_error(self.end_date_field, self.date_error_msg)

        return cleaned_data


class ResourcingRequestForm(FormWithStartEndDates):
    class Meta:
        model = ResourcingRequest
        fields = [
            "requestor",
            "type",
            "job_title",
            "project_name",
            "portfolio",
            "profession",
            "start_date",
            "end_date",
            "is_ir35",
            "chief",
        ]
        widgets = {
            "requestor": forms.HiddenInput,
            "type": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["requestor"].disabled = True

        # Add placeholders to the form.
        placeholders = {
            "job_title": "Python Developer",
            "project_name": "JML",
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs["placeholder"] = placeholder


class FinancialInformationForm(forms.ModelForm):
    class Meta:
        model = FinancialInformation
        fields = "__all__"
        widgets = {
            "resourcing_request": forms.HiddenInput,
            "group": forms.Select(
                attrs={
                    "hx-get": reverse_lazy("htmx-load-directorates"),
                    "hx-target": "#id_directorate",
                }
            ),
        }

    inside_ir35_fields = ["min_day_rate", "max_day_rate", "days_required"]
    outside_ir35_fields = ["project_fees"]

    def __init__(self, *args, is_ir35, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_ir35 = is_ir35

        self.fields["resourcing_request"].disabled = True

        self.fields["total_budget"].help_text = render_to_string(
            "main/partials/total-budget-help-text.html"
        )

        # Add prefix to currency fields.
        money_fields = ["total_budget", "min_day_rate", "max_day_rate", "project_fees"]

        for field in money_fields:
            self.fields[field].prefix = "£"

        # Update required fields.
        required_ir35_fields = (
            self.inside_ir35_fields if self.is_ir35 else self.outside_ir35_fields
        )

        for field in required_ir35_fields:
            self.fields[field].required = True

        # Remove unnecessary fields.
        ir35_fields_to_remove = (
            self.inside_ir35_fields if not self.is_ir35 else self.outside_ir35_fields
        )

        for field in ir35_fields_to_remove:
            del self.fields[field]

        syncronise_cost_centre_dropdowns(self)


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


class CestDocumentForm(forms.ModelForm):
    class Meta:
        model = CestDocument
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


class SdsStatusDeterminationForm(forms.ModelForm):
    class Meta:
        model = SdsStatusDetermination
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
