from main.forms.statement_of_work_forms import (
    StatementOfWorkForm,
    StatementOfWorkModuleDeliverableForm,
    StatementOfWorkModuleForm,
)
from main.models import (
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)
from main.views.supporting_documents import (
    SupportingDocumentCreateView,
    SupportingDocumentDeleteView,
    SupportingDocumentUpdateView,
)


class StatementOfWorkBaseMixin:
    def get_success_url(self):
        return self.object.get_absolute_url()


# Statement of work
class StatementOfWorkMixin(StatementOfWorkBaseMixin):
    model = StatementOfWork
    pk_url_kwarg = "statement_of_work_pk"
    event_context = {"object": "statement of work"}
    title = "Statement of work"


class StatementOfWorkCreateView(StatementOfWorkMixin, SupportingDocumentCreateView):
    form_class = StatementOfWorkForm
    permission_required = "main.add_statementofwork"


class StatementOfWorkUpdateView(StatementOfWorkMixin, SupportingDocumentUpdateView):
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"


# Modules
class StatementOfWorkModuleMixin(StatementOfWorkBaseMixin):
    model = StatementOfWorkModule
    pk_url_kwarg = "module_pk"
    event_context = {"object": "statement of work module"}
    title = "Statement of work module"


class StatementOfWorkModuleCreateView(
    StatementOfWorkModuleMixin, SupportingDocumentCreateView
):
    form_class = StatementOfWorkModuleForm
    permission_required = "main.add_statementofwork"

    def get_initial(self):
        return {"statement_of_work": self.kwargs["statement_of_work_pk"]}


class StatementOfWorkModuleUpdateView(
    StatementOfWorkModuleMixin, SupportingDocumentUpdateView
):
    form_class = StatementOfWorkModuleForm
    permission_required = "main.change_statementofwork"


class StatementOfWorkModuleDeleteView(
    StatementOfWorkModuleMixin, SupportingDocumentDeleteView
):
    permission_required = "main.delete_statementofwork"


# Deliverables
class StatementOfWorkModuleDeliverableMixin(StatementOfWorkBaseMixin):
    model = StatementOfWorkModuleDeliverable
    pk_url_kwarg = "deliverable_pk"
    event_context = {"object": "statement of work module deliverable"}
    title = "Statement of work module deliverable"


class StatementOfWorkModuleDeliverableCreateView(
    StatementOfWorkModuleDeliverableMixin, SupportingDocumentCreateView
):
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    pk_url_kwarg = "deliverable_pk"
    permission_required = "main.add_statementofwork"

    def get_initial(self):
        return {"statement_of_work_module": self.kwargs["module_pk"]}


class StatementOfWorkModuleDeliverableUpdateView(
    StatementOfWorkModuleDeliverableMixin, SupportingDocumentUpdateView
):
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.change_statementofwork"


class StatementOfWorkModuleDeliverableDeleteView(
    StatementOfWorkModuleDeliverableMixin, SupportingDocumentDeleteView
):
    permission_required = "main.delete_statementofwork"
