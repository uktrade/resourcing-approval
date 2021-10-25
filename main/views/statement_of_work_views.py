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
        if "create_module" in self.request.POST:
            url = reverse("statement-of-work-module-create", kwargs={"parent_pk": self.object.id})
        else:
            url = self.object.approval.get_absolute_url()
        return url


class StatementOfWorkUpdateView(ApprovalFormUpdateView):
    template_name = "main/statementofwork.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_children"] = self.object.modules.all()
        return context

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse("statement-of-work-module-create", kwargs={"parent_pk": self.object.id})
        else:
            url = self.object.approval.get_absolute_url()
        return url


class StatementOfWorkModuleCreateView(ApprovalFormCreateView):
    template_name = "main/statement_of_work_module.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.add_statementofwork"

    def get_initial(self):
        return {"statement_of_work": self.kwargs["parent_pk"]}

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse("statement-of-work-module-deliverable-create",
                          kwargs={"parent_pk": self.object.id})
        else:
            url = reverse("statement-of-work-update", kwargs={"pk":self.object.statement_of_work.id})
        return url


class StatementOfWorkModuleUpdateView(ApprovalFormUpdateView):
    template_name = "main/statement_of_work_module.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.change_statementofwork"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_children"] = self.object.deliverables.all()
        return context

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse("statement-of-work-module-deliverable-create",
                          kwargs={"parent_pk": self.object.id})
        else:
            url = reverse("statement-of-work-update", kwargs={"pk":self.object.statement_of_work.id})
        return url


class StatementOfWorkModuleDeliverableCreateView(ApprovalFormCreateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.add_statementofwork"

    def get_initial(self):
        return {"statement_of_work_module": self.kwargs["parent_pk"]}

    def get_success_url(self):
        return reverse("statement-of-work-update", kwargs={"pk":self.object.statement_of_work_module.id})


class StatementOfWorkModuleDeliverableUpdateView(ApprovalFormUpdateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.change_statementofwork"

    def get_success_url(self):
        return reverse("statement-of-work-module-update", kwargs={"pk":self.object.statement_of_work_module.id})



