from django.urls import path
from django_workflow_engine import workflow_urls

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "workflow/",
        workflow_urls(
            create_view=views.MyFlowCreateView,
            list_view=views.MyFlowListView,
            view=views.MyFlowView,
            continue_view=views.MyFlowContinueView,
        ),
    ),
]
