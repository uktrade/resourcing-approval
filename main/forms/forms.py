from django import forms
from django.urls import reverse_lazy

from main.models import (
    Approval,
    CestDocument,
    CestRationale,
    Comment,
    FinancialInformation,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)
from main.utils import get_user_related_approval_types, syncronise_cost_centre_dropdowns


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
            "full_name",
            "job_title",
            "project_name",
            "start_date",
            "end_date",
            "is_ir35",
            "chief",
        ]
        widgets = {
            "requestor": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["requestor"].disabled = True


class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = [
            "type",
            "approved",
        ]

    reason = forms.CharField(
        required=False, empty_value=None, widget=forms.Textarea(attrs={"rows": 5})
    )

    def __init__(self, *args, user, resourcing_request, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["type"].choices = [
            (approval_type.value, approval_type.label)
            for approval_type in get_user_related_approval_types(
                user, resourcing_request
            )
        ]

    def clean(self):
        cleaned_data = super().clean()

        approved = cleaned_data.get("approved")
        reason = cleaned_data.get("reason")

        if approved in (False, None) and not reason:
            self.add_error(
                "reason", "This field is required when rejecting or clearing."
            )

        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        widgets = {
            "resourcing_request": forms.HiddenInput,
            "user": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
        self.fields["user"].disabled = True
        self.fields["text"].widget.attrs.update({"rows": 5})


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

    def clean(self):
        cleaned_data = super().clean()

        inside_ir35_fields = ["min_day_rate", "max_day_rate", "days_required"]
        outside_ir35_fields = ["project_fees"]

        if cleaned_data.get("resourcing_request").is_ir35 is True:
            # Check inside fields.
            for field in inside_ir35_fields:
                if cleaned_data.get(field) is None:
                    self.add_error(field, "Required if inside IR35")
            # Clear outside fields.
            for field in outside_ir35_fields:
                cleaned_data[field] = None
        elif cleaned_data.get("resourcing_request").is_ir35 is False:
            # Check outside fields.
            for field in outside_ir35_fields:
                if cleaned_data.get(field) is None:
                    self.add_error(field, "Required if outside IR35")
            # Clear inside fields.
            for field in inside_ir35_fields:
                cleaned_data[field] = None

        return cleaned_data


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


class CestRationaleForm(forms.ModelForm):
    start_date_field = "role_start_date"
    end_date_field = "role_end_date"

    class Meta:
        model = CestRationale
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
