from django import forms

from main.models import (
    CestRationale,
    Comment,
    ContractorApproval,
    InterimRequest,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
)


class ContractorApprovalForm(forms.ModelForm):
    class Meta:
        model = ContractorApproval
        fields = ["name", "is_ir35", "chief"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        widgets = {
            "approval": forms.HiddenInput,
            "user": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True
        self.fields["user"].disabled = True
        self.fields["text"].widget.attrs.update({"rows": 5})


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True


class StatementOfWorkForm(forms.ModelForm):
    class Meta:
        model = StatementOfWork
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True


class InterimRequestForm(forms.ModelForm):
    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True


class CestRationaleForm(forms.ModelForm):
    class Meta:
        model = CestRationale
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True


class SdsStatusDeterminationForm(forms.ModelForm):
    class Meta:
        model = SdsStatusDetermination
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["approval"].disabled = True
