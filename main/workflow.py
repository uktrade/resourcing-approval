from django_workflow_engine import Workflow, Step, Task, TaskError
from django import forms

from main.models import ContractorApproval


ContractorApprovalWorkflow = Workflow(
    name="contractor_approval",
    steps=[
        Step(
            step_id="setup_contractor_approval",
            task_name="setup_contractor_approval",
            start=True,
            target="query_ir35",
        ),
        Step(
            step_id="query_ir35",
            task_name="query_ir35",
            target=None,
        ),
    ],
)


class FormTask(Task):
    abstract = True
    auto = False
    template = "main/flow_continue.html"

    @property
    def form_class(self):
        raise NotImplementedError

    def get_instance(self):
        raise NotImplementedError

    def execute(self, task_info):
        form = self.form_class(instance=self.get_instance(), data=task_info)

        if form.is_valid():
            form.save()
        else:
            raise TaskError("Form is not valid", {"form": form})

        return None, form.cleaned_data

    def context(self):
        return {"form": self.form_class(instance=self.get_instance())}


class SetupContractorApproval(Task):
    task_name = "setup_contractor_approval"
    auto = True

    def execute(self, task_info):
        ContractorApproval.objects.create(flow=self.flow)

        return None, {}


class QueryIr35Form(forms.ModelForm):
    class Meta:
        model = ContractorApproval
        fields = ["is_ir35"]


class QueryIr35Task(FormTask):
    abstract = False
    task_name = "query_ir35"
    form_class = QueryIr35Form

    def get_instance(self):
        return self.flow.contractor_approval
