from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from main.constants import APPROVAL_TYPE_TO_GROUP, ApproverGroup
from main.forms.forms import ApprovalForm, CommentForm, ResourcingRequestForm
from main.models import Approval, Comment, ResourcingRequest
from main.services.event_log import EventLogMixin, EventLogService, EventType
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


class ResourcingRequestCreateView(EventLogMixin, PermissionRequiredMixin, CreateView):
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.add_resourcingrequest"
    template_name = "main/form.html"
    event_type = EventType.CREATED
    event_context = {"object": "resourcing request"}

    def get_initial(self):
        return {"requestor": self.request.user}

    def get_event_content_object(self) -> models.Model:
        return self.object


class ResourcingRequestDetailView(
    CanAccessResourcingRequestMixin, PermissionRequiredMixin, DetailView
):
    model = ResourcingRequest
    permission_required = "main.view_resourcingrequest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resourcing_request = context["object"]

        # forms
        context["approval_form"] = ApprovalForm(
            user=self.request.user, resourcing_request=resourcing_request
        )
        context["comment_form"] = CommentForm(
            initial={
                "resourcing_request": resourcing_request.pk,
                "user": self.request.user.pk,
            }
        )

        context["can_user_approve"] = resourcing_request.can_user_approve(
            self.request.user
        )

        return context


class ResourcingRequestUpdateView(
    EventLogMixin,
    CanEditResourcingRequestMixin,
    CanAccessResourcingRequestMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.change_resourcingrequest"
    template_name = "main/form.html"
    event_type = EventType.UPDATED
    event_context = {"object": "resourcing request"}

    def get_event_content_object(self) -> models.Model:
        return self.object


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


class ResourcingRequestActionView(EventLogMixin, PermissionRequiredMixin, View):
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

    def get_event_content_object(self) -> models.Model:
        return self.resourcing_request


class ResourcingRequestSendForApprovalView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"
    event_type = EventType.SENT_FOR_APPROVAL

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_send_for_approval

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AWAITING_APPROVALS
        resourcing_request.save()

        notify_approvers.delay(resourcing_request.pk, self.resourcing_request_url)


class ResourcingRequestAmendView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"
    event_type = EventType.AMENDING

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_amend

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.AMENDING
        resourcing_request.save()


class ResourcingRequestSendForReviewView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"
    event_type = EventType.SENT_FOR_REVIEW

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


class ResourcingRequestFinishAmendmentsReviewView(ResourcingRequestActionView):
    permission_required = "main.can_give_busops_approval"
    event_type = EventType.REVIEWED_AMENDMENTS

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


class ResourcingRequestAddComment(EventLogMixin, PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    permission_required = "main.view_resourcingrequest"
    event_type = EventType.COMMENTED

    def get_initial(self):
        return {"resourcing_request": self.kwargs["pk"], "user": self.request.user.pk}

    def get_success_url(self):
        return self.object.resourcing_request.get_absolute_url()

    def get_event_content_object(self) -> models.Model:
        return self.object.resourcing_request


class ResourcingRequestApprovalView(FormView):
    form_class = ApprovalForm
    template_name = "main/partials/approvals.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.resourcing_request = (
            ResourcingRequest.objects.select_related_approvals().get(
                pk=self.kwargs["pk"]
            )
        )

        self.resourcing_request_url = self.request.build_absolute_uri(
            self.resourcing_request.get_absolute_url()
        )

    def get_context_data(self, **kwargs):
        context = {
            "resourcing_request": self.resourcing_request,
            "can_user_approve": self.resourcing_request.can_user_approve(
                self.request.user
            ),
        }

        return super().get_context_data(**kwargs) | context

    def get_form_kwargs(self):
        form_kwargs = {
            "user": self.request.user,
            "resourcing_request": self.resourcing_request,
        }

        return super().get_form_kwargs() | form_kwargs

    def form_valid(self, form):
        approval_type = form.cleaned_data["type"]
        approved = form.cleaned_data["approved"]
        reason = form.cleaned_data["reason"]

        comment = None

        if reason:
            comment = Comment.objects.create(
                resourcing_request=self.resourcing_request,
                user=self.request.user,
                text=form.cleaned_data["reason"],
            )

        approval = Approval.objects.create(
            resourcing_request=self.resourcing_request,
            user=self.request.user,
            reason=comment,
            type=approval_type,
            approved=approved,
        )

        setattr(self.resourcing_request, f"{approval_type}_approval", approval)

        EventLogService.add_event(
            content_object=self.resourcing_request,
            user=self.request.user,
            event_type=(
                EventType.GROUP_APPROVED if approved else EventType.GROUP_REJECTED
            ),
            event_context={"group": Approval.Type(approval.type).label},
        )

        if self.resourcing_request.get_is_approved():
            self.resourcing_request.state = self.resourcing_request.State.APPROVED

            EventLogService.add_event(
                content_object=self.resourcing_request,
                user=self.request.user,
                event_type=EventType.APPROVED,
            )

        self.resourcing_request.save()

        notify_approvers.delay(
            self.resourcing_request.pk,
            self.resourcing_request_url,
            approval.pk,
        )

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info
