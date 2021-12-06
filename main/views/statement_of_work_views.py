# https://simpleit.rocks/python/django/having-multiple-submit-buttons-for-same-form-in-django/
from django.urls import reverse

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
from main.views.supporting_forms import (
    SupportingFormCreateView,
    SupportingFormUpdateView,
)


class StatementOfWorkCreateView(SupportingFormCreateView):
    template_name = "main/statement_of_work.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.add_statementofwork"
    event_context = {"object": "statement of work"}

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse(
                "statement-of-work-module-create", kwargs={"parent_pk": self.object.id}
            )
        else:
            url = self.object.resourcing_request.get_absolute_url()
        return url


class StatementOfWorkUpdateView(SupportingFormUpdateView):
    template_name = "main/statement_of_work.html"
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"
    event_context = {"object": "statement of work"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_children"] = self.object.modules.all()
        return context

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse(
                "statement-of-work-module-create", kwargs={"parent_pk": self.object.id}
            )
        else:
            url = self.object.resourcing_request.get_absolute_url()
        return url


class StatementOfWorkModuleCreateView(SupportingFormCreateView):
    template_name = "main/statement_of_work_module.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.add_statementofwork"
    event_context = {"object": "statement of work module"}

    def get_initial(self):
        return {"statement_of_work": self.kwargs["parent_pk"]}

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse(
                "statement-of-work-module-deliverable-create",
                kwargs={"parent_pk": self.object.id},
            )
        else:
            url = reverse(
                "statement-of-work-update",
                kwargs={"pk": self.object.statement_of_work.id},
            )
        return url


class StatementOfWorkModuleUpdateView(SupportingFormUpdateView):
    template_name = "main/statement_of_work_module.html"
    model = StatementOfWorkModule
    form_class = StatementOfWorkModuleForm
    permission_required = "main.change_statementofwork"
    event_context = {"object": "statement of work module"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_children"] = self.object.deliverables.all()
        return context

    def get_success_url(self):
        if "create_child" in self.request.POST:
            url = reverse(
                "statement-of-work-module-deliverable-create",
                kwargs={"parent_pk": self.object.id},
            )
        else:
            url = reverse(
                "statement-of-work-update",
                kwargs={"pk": self.object.statement_of_work.id},
            )
        return url


class StatementOfWorkModuleDeliverableCreateView(SupportingFormCreateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.add_statementofwork"
    event_context = {"object": "statement of work module deliverable"}

    def get_initial(self):
        return {"statement_of_work_module": self.kwargs["parent_pk"]}

    def get_success_url(self):
        return reverse(
            "statement-of-work-module-update",
            kwargs={"pk": self.object.statement_of_work_module.id},
        )


class StatementOfWorkModuleDeliverableUpdateView(SupportingFormUpdateView):
    template_name = "main/form.html"
    model = StatementOfWorkModuleDeliverable
    form_class = StatementOfWorkModuleDeliverableForm
    permission_required = "main.change_statementofwork"
    event_context = {"object": "statement of work module deliverable"}

    def get_success_url(self):
        return reverse(
            "statement-of-work-module-update",
            kwargs={"pk": self.object.statement_of_work_module.id},
        )
