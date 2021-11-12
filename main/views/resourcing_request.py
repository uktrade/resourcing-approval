from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from main.constants import APPROVAL_TYPE_TO_GROUP, ApproverGroup
from main.forms.forms import CommentForm, ResourcingRequestForm
from main.models import Approval, Comment, ResourcingRequest
from main.tasks import notify_approvers, send_group_notification, send_notification


def get_approvals_context_data(user, resourcing_request):
    approvals = resourcing_request.get_approvals()

    for approval_type in Approval.Type:
        has_permission = user.has_approval_perm(approval_type)

        if approval_type == Approval.Type.CHIEF:
            has_permission = has_permission and (
                user == resourcing_request.chief or user.is_superuser
            )

        yield {
            "type": approval_type,
            "has_permission": has_permission,
            "object": approvals[approval_type],
        }


# TODO: Adds 2 queries.
class CanAccessResourcingRequestMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user

        return user == self.get_object().requestor or user.is_approver


class CanEditResourcingRequestMixin:
    def get_resourcing_request(self):
        return self.get_object()

    def dispatch(self, request, *args, **kwargs):
        if not self.get_resourcing_request().can_update:
            raise ValidationError("Cannot edit resourcing request")

        return super().dispatch(request, *args, **kwargs)


class ResourcingRequestCreateView(PermissionRequiredMixin, CreateView):
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.add_resourcingrequest"
    template_name = "main/form.html"

    def get_initial(self):
        return {"requestor": self.request.user}


class ResourcingRequestDetailView(
    CanAccessResourcingRequestMixin, PermissionRequiredMixin, DetailView
):
    model = ResourcingRequest
    permission_required = "main.view_resourcingrequest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resourcing_request = context["object"]

        context["comment_form"] = CommentForm(
            initial={
                "resourcing_request": resourcing_request.pk,
                "user": self.request.user.pk,
            }
        )

        approvals = list(
            get_approvals_context_data(self.request.user, resourcing_request)
        )

        context["approvals"] = approvals
        context["is_approved"] = all(
            x["object"] and x["object"].approved for x in approvals
        )

        return context


class ResourcingRequestUpdateView(
    CanEditResourcingRequestMixin,
    CanAccessResourcingRequestMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.change_resourcingrequest"
    template_name = "main/form.html"


class ResourcingRequestDeleteView(
    CanAccessResourcingRequestMixin, PermissionRequiredMixin, DeleteView
):
    model = ResourcingRequest
    success_url = reverse_lazy("dashboard")
    permission_required = "main.delete_resourcingrequest"
    template_name = "main/form.html"


class ResourcingRequestListView(PermissionRequiredMixin, ListView):
    model = ResourcingRequest
    permission_required = "main.view_all_resourcingrequests"


class ResourcingRequestActionView(PermissionRequiredMixin, View):
    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        """Return `True` if the action can be performed else `False`."""
        raise NotImplementedError

    def action(self, resourcing_request):
        raise NotImplementedError

    def post(self, request, pk, **kwargs):
        self.resourcing_request = (
            ResourcingRequest.objects.select_related_approvals().get(pk=pk)
        )

        self.resourcing_request_url = self.request.build_absolute_uri(
            self.resourcing_request.get_absolute_url()
        )

        if not self.can_do_action(self.resourcing_request):
            raise ValidationError("Cannot perform this action")

        self.action(self.resourcing_request)

        return redirect(
            reverse(
                "resourcing-request-detail", kwargs={"pk": self.resourcing_request.pk}
            )
        )


class ResourcingRequestSendForApprovalView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_send_for_approval

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AWAITING_APPROVALS
        resourcing_request.save()

        notify_approvers.delay(resourcing_request.pk, self.resourcing_request_url)


class ResourcingRequestAmendView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_amend

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AMENDING
        resourcing_request.save()


class ResourcingRequestSendForReviewView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_send_for_review

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AMENDMENTS_REVIEW
        resourcing_request.save()

        send_group_notification(
            ApproverGroup.BUSOPS,
            template_id=settings.GOVUK_NOTIFY_AMENDED_TEMPLATE_ID,
            personalisation={"resourcing_request_url": self.resourcing_request_url},
        )


class ResourcingRequestAddApproval(ResourcingRequestActionView):
    def get_permission_required(self):
        approval_type = self.request.POST["type"]

        return (f"main.can_give_{approval_type}_approval",)

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_approve

    def action(self, resourcing_request):
        approval_type = self.request.POST["type"]
        approved = self.request.POST["approved"]

        is_approved = resourcing_request.get_is_approved()

        if is_approved:
            raise ValidationError("Resourcing request is already approved")

        if approval_type not in Approval.Type:
            raise ValidationError("Invalid approval type")

        if approval_type == "chief":
            if (
                self.request.user != resourcing_request.chief
                and not self.request.user.is_superuser
            ):
                raise ValidationError(
                    "Only the nominated Chief can give Chief approval"
                )

        approved_choices = {
            "true": True,
            "false": False,
            "unknown": None,
        }
        approved = approved_choices[approved]

        approval = Approval.objects.create(
            resourcing_request=resourcing_request,
            user=self.request.user,
            reason=None,
            type=approval_type,
            approved=approved,
        )

        setattr(resourcing_request, f"{approval_type}_approval", approval)

        is_approved = resourcing_request.get_is_approved()

        if is_approved:
            resourcing_request.state = resourcing_request.State.APPROVED

        resourcing_request.save()

        notify_approvers.delay(
            resourcing_request.pk,
            self.resourcing_request_url,
            approval.pk,
        )


class ResourcingRequestClearApprovalView(ResourcingRequestActionView):
    permission_required = "main.can_give_busops_approval"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_clear_approval

    def action(self, resourcing_request):
        approval_type = self.request.POST["type"]

        if approval_type not in Approval.Type:
            raise ValidationError("Invalid approval type")

        approval = Approval.objects.create(
            resourcing_request=resourcing_request,
            user=self.request.user,
            reason=None,
            type=approval_type,
            approved=None,
        )

        setattr(resourcing_request, f"{approval_type}_approval", approval)

        resourcing_request.save()


class ResourcingRequestFinishAmendmentsReviewView(ResourcingRequestActionView):
    permission_required = "main.can_give_busops_approval"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_finish_amendments_review

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AWAITING_APPROVALS
        resourcing_request.save()

        # Notify the requestor that the amendments have been reviewed.
        send_notification.delay(
            to=resourcing_request.requestor.email,
            template_id=settings.GOVUK_NOTIFY_FINISHED_AMENDMENTS_REVIEW_TEMPLATE_ID,
            personalisation={"resourcing_request_url": self.resourcing_request_url},
        )

        # Notify all the approval groups which had their approvals cleared.
        re_approval_groups = [
            APPROVAL_TYPE_TO_GROUP[approval.type]
            for approval in resourcing_request.get_approvals().values()
            if approval and approval.approved is None
        ]

        for group in re_approval_groups:
            send_group_notification(
                group,
                template_id=settings.GOVUK_NOTIFY_RE_APPROVAL_TEMPLATE_ID,
                personalisation={"resourcing_request_url": self.resourcing_request_url},
            )


class ResourcingRequestAddComment(PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    permission_required = "main.view_resourcingrequest"

    def get_initial(self):
        return {"resourcing_request": self.kwargs["pk"], "user": self.request.user.pk}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()
