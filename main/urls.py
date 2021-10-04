from django.urls import path
from django_workflow_engine import workflow_urls

from . import views

urlpatterns = [
    path(
        "workflow/",
        workflow_urls(
            create_view=views.MyFlowCreateView,
            continue_view=views.MyFlowContinueView,
        ),
    ),
]
