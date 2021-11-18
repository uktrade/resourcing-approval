from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from main.forms.forms import (
    CestDocumentForm,
    CestRationaleForm,
    JobDescriptionForm,
    SdsStatusDeterminationForm,
)
from main.models import (
    CestDocument,
    CestRationale,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)

from .resourcing_request import CanEditResourcingRequestMixin


# TODO: Possible opportunity to refactor the supporting forms to use a shared view and
# template.
class SupportingFormCreateView(PermissionRequiredMixin, CreateView):
    template_name = "main/form.html"

    def get_initial(self):
        return {"resourcing_request": self.request.GET.get("resourcing_request")}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()

    def get_resourcing_request(self):
        return ResourcingRequest.objects.get(
            pk=self.request.GET.get("resourcing_request")
        )


class SupportingFormUpdateView(
    CanEditResourcingRequestMixin, PermissionRequiredMixin, UpdateView
):
    template_name = "main/form.html"

    def get_initial(self):
        return {"resourcing_request": self.object.resourcing_request.pk}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()

    def get_resourcing_request(self):
        return self.get_object().resourcing_request


class SupportingFormDetailView(PermissionRequiredMixin, DetailView):
    template_name = "main/detail.html"
    exclude_list = ["id", "resourcing_request"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_title"] = self.title
        context["exclude_list"] = self.exclude_list
        return context


class JobDescriptionCreateView(SupportingFormCreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.add_jobdescription"


class JobDescriptionUpdateView(SupportingFormUpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.change_jobdescription"


class CestRationaleCreateView(SupportingFormCreateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.add_cestrationale"


class CestRationaleUpdateView(SupportingFormUpdateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.change_cestrationale"


class CestDocumentCreateView(SupportingFormCreateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.add_cestdocument"


class CestDocumentUpdateView(SupportingFormUpdateView):
    model = CestDocument
    form_class = CestDocumentForm
    permission_required = "main.change_cestdocument"


class SdsStatusDeterminationCreateView(SupportingFormCreateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.add_sdsstatusdetermination"


class SdsStatusDeterminationUpdateView(SupportingFormUpdateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.change_sdsstatusdetermination"
