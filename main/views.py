from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from main.forms import (
    CestRationaleForm,
    CommentForm,
    ContractorApprovalForm,
    InterimRequestForm,
    JobDescriptionForm,
    SdsStatusDeterminationForm,
    StatementOfWorkForm,
)
from main.models import (
    CestRationale,
    Comment,
    ContractorApproval,
    InterimRequest,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
)


def index(request):
    return redirect(reverse("dashboard"))


class DashboardView(TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["your_approvals"] = user.approvals.all()

        query = Q()

        if user.has_perm("can_give_chief_approval"):
            query = query | Q(chief_approval__isnull=True)

        if user.has_perm("can_give_hrbp_approval"):
            query = query | Q(hrbp_approval__isnull=True)

        if user.has_perm("can_give_finance_approval"):
            query = query | Q(finance_approval__isnull=True)

        if user.has_perm("can_give_commercial_approval"):
            query = query | Q(commercial_approval__isnull=True)

        context["awaiting_your_approval"] = ContractorApproval.objects.filter(
            Q(
                status__in=(
                    ContractorApproval.Status.AWAITING_CHIEF_APPROVAL,
                    ContractorApproval.Status.AWAITING_APPROVALS,
                )
            )
            & query
        )

        return context


class CanEditApprovalMixin:
    def get_approval(self):
        return self.get_object()

    def dispatch(self, request, *args, **kwargs):
        if not self.get_approval().can_edit:
            raise ValidationError("Cannot edit approval")

        return super().dispatch(request, *args, **kwargs)


# Contractor approval
class ApprovalCreateView(PermissionRequiredMixin, CreateView):
    model = ContractorApproval
    form_class = ContractorApprovalForm
    permission_required = "main.add_contractorapproval"
    template_name = "main/form.html"

    def get_initial(self):
        return {"requestor": self.request.user}


class ApprovalDetailView(PermissionRequiredMixin, DetailView):
    model = ContractorApproval
    context_object_name = "approval"
    permission_required = "main.view_contractorapproval"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approval = context["approval"]
        context["comment_form"] = CommentForm(
            initial={"approval": approval.pk, "user": self.request.user.pk}
        )

        return context


class ApprovalUpdateView(CanEditApprovalMixin, PermissionRequiredMixin, UpdateView):
    model = ContractorApproval
    form_class = ContractorApprovalForm
    permission_required = "main.change_contractorapproval"
    template_name = "main/form.html"


class ApprovalDeleteView(PermissionRequiredMixin, DeleteView):
    model = ContractorApproval
    success_url = reverse_lazy("approval-list")
    permission_required = "main.delete_contractorapproval"
    template_name = "main/form.html"


# Approval actions
class ApprovalChangeStatusView(PermissionRequiredMixin, View):
    permission_required = "main.change_contractorapproval"

    def post(self, request, pk):
        status = int(request.POST["status"])

        approval = ContractorApproval.objects.get(pk=pk)

        if status == approval.Status.DRAFT:
            approval.mark_as_draft()
        elif status == approval.Status.AWAITING_CHIEF_APPROVAL:
            approval.send_to_chief()
        else:
            raise ValidationError("Invalid status")

        approval.save()

        return redirect(reverse("approval-detail", kwargs={"pk": pk}))


class ApprovalApproveRejectView(View):
    # TODO: Change to post.
    def get(self, request, pk, approved=True):
        which_approval = request.GET["which_approval"]

        # TODO: Switch to using ContractorApproval.Approvals enum.
        if which_approval not in ["chief", "hrbp", "finance", "commercial"]:
            raise ValidationError("Invalid approval")

        if not request.user.has_perm(f"main.can_give_{which_approval}_approval"):
            raise PermissionError("User does not have permission to give this approval")

        approval = ContractorApproval.objects.get(pk=pk)

        if which_approval == "chief" and request.user != approval.chief:
            raise PermissionError("Only the nominated chief can give chief approval")

        if approved:
            approval.approve(which_approval, request.user)
        else:
            approval.reject(which_approval, request.user)

        approval.save()

        return redirect(reverse("approval-detail", kwargs={"pk": pk}))


class ApprovalAddComment(PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    permission_required = "main.view_contractorapproval"

    def get_initial(self):
        return {"approval": self.kwargs["pk"], "user": self.request.user.pk}

    def get_success_url(self):
        return self.object.approval.get_absolute_url()


# Supporting forms
# TODO: Possible opportunity to refactor the supporting forms to use a shared view and
# template.
class ApprovalFormCreateView(PermissionRequiredMixin, CreateView):
    template_name = "main/form.html"

    def get_initial(self):
        return {"approval": self.request.GET.get("approval")}

    def get_success_url(self):
        return self.object.approval.get_absolute_url()


class ApprovalFormUpdateView(CanEditApprovalMixin, PermissionRequiredMixin, UpdateView):
    template_name = "main/form.html"

    def get_initial(self):
        return {"approval": self.object.approval.pk}

    def get_success_url(self):
        return self.object.approval.get_absolute_url()

    def get_approval(self):
        return self.get_object().approval


class JobDescriptionCreateView(ApprovalFormCreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.add_jobdescription"


class JobDescriptionUpdateView(ApprovalFormUpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    permission_required = "main.change_jobdescription"


class StatementOfWorkCreateView(ApprovalFormCreateView):
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.add_statementofwork"


class StatementOfWorkUpdateView(ApprovalFormUpdateView):
    model = StatementOfWork
    form_class = StatementOfWorkForm
    permission_required = "main.change_statementofwork"


class InterimRequestCreateView(ApprovalFormCreateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.add_interimrequest"


class InterimRequestUpdateView(ApprovalFormUpdateView):
    model = InterimRequest
    form_class = InterimRequestForm
    permission_required = "main.change_interimrequest"


class CestRationaleCreateView(ApprovalFormCreateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.add_cestrationale"


class CestRationaleUpdateView(ApprovalFormUpdateView):
    model = CestRationale
    form_class = CestRationaleForm
    permission_required = "main.change_cestrationale"


class SdsStatusDeterminationCreateView(ApprovalFormCreateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.add_sdsstatusdetermination"


class SdsStatusDeterminationUpdateView(ApprovalFormUpdateView):
    model = SdsStatusDetermination
    form_class = SdsStatusDeterminationForm
    permission_required = "main.change_sdsstatusdetermination"
