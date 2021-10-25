from django import forms

from main.models import (
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)


class StatementOfWorkModuleForm(forms.ModelForm):
    class Meta:
        model = StatementOfWorkModule
        fields = "__all__"
        widgets = {"statement_of_work": forms.HiddenInput}


class StatementOfWorkModuleDeliverableForm(forms.ModelForm):
    class Meta:
        model = StatementOfWorkModuleDeliverable
        fields = "__all__"
        widgets = {"statement_of_work_module": forms.HiddenInput}


class StatementOfWorkForm(forms.ModelForm):
    class Meta:
        model = StatementOfWork
        fields = "__all__"
        widgets = {"approval": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["approval"].disabled = True
