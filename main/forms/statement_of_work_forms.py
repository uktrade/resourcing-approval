from django import forms

from main.models import (
    CestRationale,
    Comment,
    ResourcingApproval,
    InterimRequest,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)


class StatementOfWorkModuleForm(forms.ModelForm):
    class Meta:
        model = StatementOfWorkModule
        fields = "__all__"
        widgets = {"statement_of_work": forms.TextInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["statement_of_work"].value = 3


class StatementOfWorkModuleDeliverableForm(forms.ModelForm):
    class Meta:
        model = StatementOfWorkModuleDeliverable
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


