from django import forms

from main.models import (
    CestRationale,
    Comment,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)


class ResourcingRequestForm(forms.ModelForm):
    class Meta:
        model = ResourcingRequest
        fields = ["requestor", "name", "is_ir35", "chief"]
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


class CestRationaleForm(forms.ModelForm):
    class Meta:
        model = CestRationale
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


