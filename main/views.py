from django.shortcuts import render
from django_workflow_engine.views import FlowCreateView, FlowContinueView


def index(request):
    return render(request, "main/index.html")


class MyFlowCreateView(FlowCreateView):
    template_name = "main/flow_form.html"


class MyFlowContinueView(FlowContinueView):
    # TODO: Can't override template like this for the continue view.
    template_name = "main/flow_continue.html"
