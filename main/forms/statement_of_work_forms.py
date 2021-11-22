from django import forms

from main.forms.forms import FormWithStartEndDates
from main.models import (
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)


class StatementOfWorkForm(forms.ModelForm):
    class Meta:
        model = StatementOfWork
        fields = "__all__"
        widgets = {"resourcing_request": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True


class StatementOfWorkModuleForm(forms.ModelForm):
    class Meta:
        model = StatementOfWorkModule
        fields = "__all__"
        widgets = {"statement_of_work": forms.HiddenInput}


class StatementOfWorkModuleDeliverableForm(FormWithStartEndDates):
    class Meta:
        model = StatementOfWorkModuleDeliverable
        fields = "__all__"
        widgets = {"statement_of_work_module": forms.HiddenInput}
