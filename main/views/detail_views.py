from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView

from main.forms.forms import CommentForm, ResourcingRequestForm
from main.models import  JobDescription

from main.views.resourcing_request import CanAccessResourcingRequestMixin

class JobDescriptionDetailView(
    PermissionRequiredMixin, DetailView
):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Job description"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_title"] = self.title
        return context

class InterimRequestDetailView(
    PermissionRequiredMixin, DetailView
):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Interim Request"
    # template_name = ""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_title"] = self.title
        return context
