from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from main.constants import APPROVAL_TYPE_TO_GROUP, ApproverGroup
from main.forms.forms import ResourcingRequestForm
from main.forms.review import ReviewForm
from main.models import ResourcingRequest
from main.services.event_log import EventLogMixin, EventType
from main.services.review import ReviewAction, ReviewService
from main.tasks import notify_approvers, send_group_notification, send_notification
from main.views.base import ResourcingRequestBaseView
from main.views.mixins import FormMixin


# TODO: Adds 2 queries.
class CanAccessResourcingRequestMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user

        return user == self.resourcing_request.requestor or user.is_approver


class CanEditResourcingRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.resourcing_request.can_update:
            raise ValidationError("Cannot edit contractor request")

        return super().dispatch(request, *args, **kwargs)


class ResourcingRequestCreateView(
    EventLogMixin,
    PermissionRequiredMixin,
    FormMixin,
    CreateView,
):
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.add_resourcingrequest"
    event_type = EventType.CREATED
    event_context = {"object": "contractor request"}
    title = "Create a new contractor request"

    def get_initial(self):
        return {
            "requestor": self.request.user,
            "type": ResourcingRequest.Type.NEW,
        }

    def get_event_content_object(self) -> models.Model:
        return self.object


class ResourcingRequestDetailView(
    CanAccessResourcingRequestMixin,
    PermissionRequiredMixin,
    DetailView,
    ResourcingRequestBaseView,
):
    pk_url_kwarg = "resourcing_request_pk"
    model = ResourcingRequest
    permission_required = "main.view_resourcingrequest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resourcing_request = context["object"]

        # forms
        context["review_form"] = ReviewForm(
            user=self.request.user, resourcing_request=resourcing_request
        )

        context["can_user_approve"] = resourcing_request.can_user_approve(
            self.request.user
        )

        context["object_changes"] = resourcing_request.change_log.get_changes()

        return context


class ResourcingRequestUpdateView(
    EventLogMixin,
    CanEditResourcingRequestMixin,
    CanAccessResourcingRequestMixin,
    PermissionRequiredMixin,
    FormMixin,
    UpdateView,
    ResourcingRequestBaseView,
):
    pk_url_kwarg = "resourcing_request_pk"
    model = ResourcingRequest
    form_class = ResourcingRequestForm
    permission_required = "main.change_resourcingrequest"
    event_type = EventType.UPDATED
    event_context = {"object": "contractor request"}
    title = "Update contractor request"

    def get_event_content_object(self) -> models.Model:
        return self.object


class ResourcingRequestDeleteView(
    CanAccessResourcingRequestMixin,
    PermissionRequiredMixin,
    DeleteView,
    ResourcingRequestBaseView,
):
    pk_url_kwarg = "resourcing_request_pk"
    model = ResourcingRequest
    success_url = reverse_lazy("dashboard")
    permission_required = "main.delete_resourcingrequest"


class ResourcingRequestListView(PermissionRequiredMixin, ListView):
    model = ResourcingRequest
    permission_required = "main.view_all_resourcingrequests"


class ResourcingRequestActionView(
    EventLogMixin, PermissionRequiredMixin, ResourcingRequestBaseView
):
    pk_url_kwarg = "resourcing_request_pk"

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        """Return `True` if the action can be performed else `False`."""
        raise NotImplementedError

    def action(self, resourcing_request):
        raise NotImplementedError

    def post(self, request, resourcing_request_pk, **kwargs):
        if not self.can_do_action(self.resourcing_request):
            raise ValidationError("Cannot perform this action")

        self.action(self.resourcing_request)

        return redirect(
            reverse(
                "resourcing-request-detail",
                kwargs={"resourcing_request_pk": self.resourcing_request.pk},
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
            email_address=resourcing_request.requestor.contact_email,
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


class ResourcingRequestReviewView(
    SuccessMessageMixin, FormView, ResourcingRequestBaseView
):
    form_class = ReviewForm
    template_name = "main/partials/review_form.html"
    action_success_message = {
        ReviewAction.APPROVE: "Your approval has been submitted.",
        ReviewAction.CLEAR_APPROVAL: "The approval has been cleared.",
        ReviewAction.REQUEST_CHANGES: "Your request change has been submitted.",
        ReviewAction.COMMENT: "Your comment has been submitted.",
    }

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
        ReviewService.add_review(
            user=self.request.user,
            resourcing_request=self.resourcing_request,
            resourcing_request_url=self.resourcing_request_url,
            action=form.cleaned_data["action"],
            approval_type=form.cleaned_data["approval_type"],
            text=form.cleaned_data["text"],
        )

        super().form_valid(form)

        # Tells HTMX to redirect to the success url.
        return HttpResponse(headers={"HX-Redirect": self.get_success_url()})

    def get_success_url(self):
        return self.resourcing_request.get_absolute_url()

    def get_success_message(self, cleaned_data):
        action = cleaned_data["action"]

        return self.action_success_message[action]


class ResourcingRequestMarkAsCompleteView(ResourcingRequestActionView):
    permission_required = "main.change_resourcingrequest"
    event_type = EventType.COMPLETED

    def can_do_action(self, resourcing_request: ResourcingRequest) -> bool:
        return resourcing_request.can_mark_as_complete

    def action(self, resourcing_request):
        resourcing_request.state = ResourcingRequest.State.COMPLETED
        resourcing_request.save()
