from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin

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


class StatementOfWorkUpdateView(ApprovalFormUpdateView):
    template_name = "main/statementofwork.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"


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


