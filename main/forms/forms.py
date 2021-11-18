from django import forms

from main.models import (
    CestDocument,
    CestRationale,
    Comment,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)


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


class ResourcingRequestForm(forms.ModelForm):
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


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


class CestRationaleForm(FormWithStartEndDates):
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


class SdsStatusDeterminationForm(FormWithStartEndDates):
    class Meta:
        model = SdsStatusDetermination
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True
