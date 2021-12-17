from typing import ClassVar

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from main.forms.forms import (
    CestDocumentForm,
    CestRationaleForm,
    FinancialInformationForm,
    JobDescriptionForm,
    SdsStatusDeterminationForm,
)
from main.models import (
    CestDocument,
    CestRationale,
    FinancialInformation,
    JobDescription,
    SdsStatusDetermination,
)
from main.services.event_log import EventLogMixin, EventType
from main.views.base import ResourcingRequestBaseView
from main.views.mixins import FormMixin

from .resourcing_request import CanEditResourcingRequestMixin


class SupportingDocumentCreateView(
    EventLogMixin,
    PermissionRequiredMixin,
    FormMixin,
    CreateView,
    ResourcingRequestBaseView,
):
    event_type = EventType.CREATED

    def get_initial(self):
        return {"resourcing_request": self.resourcing_request.pk}

    def get_event_content_object(self) -> models.Model:
        return self.resourcing_request


class SupportingDocumentDetailView(
    PermissionRequiredMixin, DetailView, ResourcingRequestBaseView
):
    # Class attributes
    # Django
    pk_url_kwarg = "supporting_document_pk"
    template_name = "main/supporting_document_detail.html"
    # App
    title = "Supporting document"
    excluded_fields: ClassVar[list[str]] = ["id", "resourcing_request"]
    stacked_fields: ClassVar[list[str]] = []

    def get_context_data(self, **kwargs):
        context = {
            "title": self.title,
            "excluded_fields": self.excluded_fields,
            "stacked_fields": self.stacked_fields,
        }

        return super().get_context_data(**kwargs) | context


class SupportingDocumentUpdateView(
    EventLogMixin,
    CanEditResourcingRequestMixin,
    PermissionRequiredMixin,
    FormMixin,
    UpdateView,
    ResourcingRequestBaseView,
):
    pk_url_kwarg = "supporting_document_pk"
    event_type = EventType.UPDATED

    def get_initial(self):
        return {"resourcing_request": self.resourcing_request.pk}

    def get_event_content_object(self) -> models.Model:
        return self.resourcing_request


class SupportingDocumentDeleteView(
    EventLogMixin,
    CanEditResourcingRequestMixin,
    PermissionRequiredMixin,
    DeleteView,
    ResourcingRequestBaseView,
):
    pk_url_kwarg = "supporting_document_pk"
    template_name = "main/confirm_delete.html"
    event_type = EventType.DELETED

    def get_event_content_object(self) -> models.Model:
        return self.resourcing_request


class FinancialInformationCreateView(SupportingDocumentCreateView):
    model = FinancialInformation
    form_class = FinancialInformationForm
    permission_required = "main.add_financialinformation"
    event_context = {"object": "financial information"}
    title = "Financial information"

    def get_form_kwargs(self):
        form_kwargs = {"is_ir35": self.resourcing_request.is_ir35}

        return super().get_form_kwargs() | form_kwargs


class FinancialInformationDetailView(SupportingDocumentDetailView):
    model = FinancialInformation
    permission_required = "main.view_financialinformation"
    title = "Financial information"


class FinancialInformationUpdateView(SupportingDocumentUpdateView):
    model = FinancialInformation
    form_class = FinancialInformationForm
    permission_required = "main.change_financialinformation"
    event_context = {"object": "financial information"}
    title = "Financial information"

    def get_form_kwargs(self):
        form_kwargs = {"is_ir35": self.resourcing_request.is_ir35}

        return super().get_form_kwargs() | form_kwargs


class JobDescriptionCreateView(SupportingDocumentCreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.add_jobdescription"
    event_context = {"object": "job description"}
    title = "Job description"


class JobDescriptionUpdateView(SupportingDocumentUpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.change_jobdescription"
    event_context = {"object": "job description"}
    title = "Job description"


class CestRationaleCreateView(SupportingDocumentCreateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.add_cestrationale"
    event_context = {"object": "CEST rationale"}
    title = "CEST rationale"


class CestRationaleUpdateView(SupportingDocumentUpdateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.change_cestrationale"
    event_context = {"object": "CEST rationale"}
    title = "CEST rationale"


class CestDocumentCreateView(SupportingDocumentCreateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.add_cestdocument"
    event_context = {"object": "CEST document"}
    title = "CEST document"


class CestDocumentUpdateView(SupportingDocumentUpdateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.change_cestdocument"
    event_context = {"object": "CEST document"}
    title = "CEST document"


class SdsStatusDeterminationCreateView(SupportingDocumentCreateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.add_sdsstatusdetermination"
    event_context = {"object": "SDS status determination"}
    title = "SDS status determination"


class SdsStatusDeterminationUpdateView(SupportingDocumentUpdateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.change_sdsstatusdetermination"
    event_context = {"object": "SDS status determination"}
    title = "SDS status determination"
