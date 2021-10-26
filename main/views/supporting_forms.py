from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView

from main.forms.forms import (
    CestRationaleForm,
    InterimRequestForm,
    JobDescriptionForm,
    SdsStatusDeterminationForm,
)
from main.models import (
    CestRationale,
    InterimRequest,
    JobDescription,
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


class JobDescriptionCreateView(SupportingFormCreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.add_jobdescription"


class JobDescriptionUpdateView(SupportingFormUpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.change_jobdescription"


class InterimRequestCreateView(SupportingFormCreateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.add_interimrequest"


class InterimRequestUpdateView(SupportingFormUpdateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.change_interimrequest"


class CestRationaleCreateView(SupportingFormCreateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.add_cestrationale"


class CestRationaleUpdateView(SupportingFormUpdateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.change_cestrationale"


class SdsStatusDeterminationCreateView(SupportingFormCreateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.add_sdsstatusdetermination"


class SdsStatusDeterminationUpdateView(SupportingFormUpdateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.change_sdsstatusdetermination"