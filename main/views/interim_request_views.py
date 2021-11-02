from main.forms.interim_request_form import InterimRequestForm
from django.urls import reverse
from django.shortcuts import render

from main.models import (
    InterimRequest,
)
from chartofaccount.models import Directorate, DepartmentalGroup, CostCentre

from main.views.supporting_forms import (
    SupportingFormCreateView,
    SupportingFormUpdateView,
)


class InterimRequestCreateView(SupportingFormCreateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.add_interimrequest"
    template_name = "main/interim_request.html"


class InterimRequestUpdateView(SupportingFormUpdateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.change_interimrequest"
    template_name = "main/interim_request.html"


def load_directorates(request):
    group_code = request.GET.get("group")
    directorates = Directorate.objects.filter(group=group_code).order_by(
        "directorate_name"
    )
    return render(
        request,
        "main/partials/directorate_list_options.html",
        {"directorates": directorates},
    )


def load_costcentres(request):
    directorate_code = request.GET.get("directorate")
    costcentres = CostCentre.objects.filter(directorate=directorate_code).order_by(
        "cost_centre_name"
    )
    return render(
        request,
        "main/partials/costcentre_list_options.html",
        {"costcentres": costcentres},
    )
