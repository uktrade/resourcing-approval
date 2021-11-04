from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView

from main.views.supporting_forms import SupportingFormDetailView
from main.models import JobDescription, InterimRequest


class JobDescriptionDetailView(SupportingFormDetailView):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Job description"


class InterimRequestDetailView(SupportingFormDetailView):
    model = InterimRequest
    permission_required = "main.view_jobdescription"
    title = "Interim Request"
