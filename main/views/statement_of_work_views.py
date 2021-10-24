from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin

# https://simpleit.rocks/python/django/having-multiple-submit-buttons-for-same-form-in-django/
from django.urls import reverse


from main.forms.statement_of_work_forms import (
    StatementOfWorkForm,
    StatementOfWorkModuleForm,
    StatementOfWorkModuleDeliverableForm,
)
from main.models import (
    StatementOfWork,
    StatementOfWorkModuleDeliverable,
    StatementOfWorkModule,
)

from main.views.views import ApprovalFormCreateView,ApprovalFormUpdateView

class StatementOfWorkCreateView(ApprovalFormCreateView):
    template_name = "main/statementofwork.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.add_statementofwork"

    def get_success_url(self):
        return self.object.approval.get_absolute_url()


class StatementOfWorkUpdateView(ApprovalFormUpdateView):
    template_name = "main/statementofwork.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"

    def get_success_url(self):
        if "create_module" in self.request.POST:
            url = reverse("statement-of-work-module-create", kwargs={"parent_pk": self.object.id})
        else:
            url = self.object.approval.get_absolute_url()
        return url





class StatementOfWorkModuleCreateView(ApprovalFormCreateView):
    template_name = "main/form.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.add_statementofwork"
    def get_initial(self):
        return {"parent": self.kwargs["parent_pk"]}


class StatementOfWorkModuleUpdateView(ApprovalFormUpdateView):
    template_name = "main/form.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.change_statementofwork"
    def get_initial(self):
        return {"approval": self.kwargs["parent_pk"]}


class StatementOfWorkModuleDeliverableCreateView(ApprovalFormCreateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.add_statementofwork"


class StatementOfWorkModuleDeliverableUpdateView(ApprovalFormUpdateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.change_statementofwork"


