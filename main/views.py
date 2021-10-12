from django.shortcuts import redirect
from django_workflow_engine.views import (
    FlowContinueView,
    FlowCreateView,
    FlowListView,
    FlowView,
)


def index(request):
    return redirect("flow-list")


class MyFlowCreateView(FlowCreateView):
    template_name = "main/flow_form.html"


class MyFlowListView(FlowListView):
    template_name = "main/flow_list.html"


class MyFlowView(FlowView):
    template_name = "main/flow.html"


class MyFlowContinueView(FlowContinueView):
    # TODO: Can't override template like this for the continue view.
    template_name = "main/flow_continue.html"
