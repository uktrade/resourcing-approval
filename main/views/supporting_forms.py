from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

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
    ResourcingRequest,
    SdsStatusDetermination,
)
from main.services.event_log import EventLogMixin, EventType

from .resourcing_request import CanEditResourcingRequestMixin


# TODO: Possible opportunity to refactor the supporting forms to use a shared view and
# template.
class SupportingFormCreateView(EventLogMixin, PermissionRequiredMixin, CreateView):
    template_name = "main/form.html"
    event_type = EventType.CREATED

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.resourcing_request = self.get_resourcing_request()

    def get_initial(self):
        return {"resourcing_request": self.request.GET.get("resourcing_request")}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()

    def get_resourcing_request(self):
        return ResourcingRequest.objects.get(
            pk=self.request.GET.get("resourcing_request")
        )

    def get_event_content_object(self) -> models.Model:
        return self.object.resourcing_request


class SupportingFormUpdateView(
    EventLogMixin, CanEditResourcingRequestMixin, PermissionRequiredMixin, UpdateView
):
    template_name = "main/form.html"
    event_type = EventType.UPDATED

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.resourcing_request = self.get_resourcing_request()

    def get_initial(self):
        return {"resourcing_request": self.object.resourcing_request.pk}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()

    def get_resourcing_request(self):
        return self.get_object().resourcing_request

    def get_event_content_object(self) -> models.Model:
        return self.object.resourcing_request


class SupportingFormDetailView(PermissionRequiredMixin, DetailView):
    template_name = "main/detail.html"
    exclude_list = ["id", "resourcing_request"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_title"] = self.title
        context["exclude_list"] = self.exclude_list
        return context


class FinancialInformationCreateView(SupportingFormCreateView):
    model = FinancialInformation
    form_class = FinancialInformationForm
    permission_required = "main.add_financialinformation"
    event_context = {"object": "financial information"}

    def get_form_kwargs(self):
        form_kwargs = {"is_ir35": self.resourcing_request.is_ir35}

        return super().get_form_kwargs() | form_kwargs


class FinancialInformationDetailView(SupportingFormDetailView):
    model = FinancialInformation
    permission_required = "main.view_financialinformation"
    title = "Financial information"


class FinancialInformationUpdateView(SupportingFormUpdateView):
    model = FinancialInformation
    form_class = FinancialInformationForm
    permission_required = "main.change_financialinformation"
    event_context = {"object": "financial information"}

    def get_form_kwargs(self):
        form_kwargs = {"is_ir35": self.resourcing_request.is_ir35}

        return super().get_form_kwargs() | form_kwargs


class JobDescriptionCreateView(SupportingFormCreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.add_jobdescription"
    event_context = {"object": "job description"}


class JobDescriptionUpdateView(SupportingFormUpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.change_jobdescription"
    event_context = {"object": "job description"}


class CestRationaleCreateView(SupportingFormCreateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.add_cestrationale"
    event_context = {"object": "CEST rationale"}


class CestRationaleUpdateView(SupportingFormUpdateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.change_cestrationale"
    event_context = {"object": "CEST rationale"}


class CestDocumentCreateView(SupportingFormCreateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.add_cestdocument"
    event_context = {"object": "CEST document"}


class CestDocumentUpdateView(SupportingFormUpdateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.change_cestdocument"
    event_context = {"object": "CEST document"}


class SdsStatusDeterminationCreateView(SupportingFormCreateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.add_sdsstatusdetermination"
    event_context = {"object": "SDS status determination"}


class SdsStatusDeterminationUpdateView(SupportingFormUpdateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.change_sdsstatusdetermination"
    event_context = {"object": "SDS status determination"}
