from enum import Enum
from typing import Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied

from main.models import Approval, Comment, ResourcingRequest
from main.services.event_log import EventLogService, EventType
from main.tasks import notify_approvers, send_notification
from user.models import User


class ReviewAction(Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"
    CLEAR_APPROVAL = "clear_approval"


class ReviewService:
    @staticmethod
    def add_review(
        user: User,
        resourcing_request: ResourcingRequest,
        resourcing_request_url: str,
        action: ReviewAction,
        approval_type: Optional[Approval.Type],
        text: Optional[str],
    ) -> None:
        """Add a review to the given resourcing request.

        This method assumes that the arguments have come from a valid ReviewForm.

        Args:
            user: Who submitted the review.
            resourcing_request: The given resourcing request.
            resourcing_request_url: URL for the given resourcing request.
            action: What review action are we taking.
            approval_type: If approving or clearing, what type of approval.
            text: Related text with the review.

        Raises:
            ValueError: If the review is invalid and we need to know about it.
        """
        if action == ReviewAction.APPROVE:
            if not resourcing_request.can_approve:
                raise ValueError("The contractor request cannot be approved")

            if not user.has_approval_perm(approval_type):
                raise PermissionDenied(
                    "The user doesn't have permission to give this approval"
                )

        if action == ReviewAction.CLEAR_APPROVAL:
            if not resourcing_request.can_clear_approval:
                raise ValueError("The approval cannot be cleared")

            if not user.has_approval_perm(Approval.Type.BUSOPS):
                raise PermissionDenied(
                    "The user doesn't have permission to clear approvals"
                )

        if action in (ReviewAction.APPROVE, ReviewAction.CLEAR_APPROVAL):
            if resourcing_request.get_is_approved():
                raise ValueError("The contractor request has already been approved")

        if action in (ReviewAction.REQUEST_CHANGES, ReviewAction.COMMENT):
            if not user.has_perm("main.add_comment"):
                raise PermissionDenied("The user doesn't have permission to comment")

        comment = None

        if text:
            comment = Comment.objects.create(
                resourcing_request=resourcing_request,
                user=user,
                text=text,
            )

        if action in (ReviewAction.APPROVE, ReviewAction.CLEAR_APPROVAL):
            approved: Optional[bool] = True

            if action == ReviewAction.CLEAR_APPROVAL:
                approved = None

            approval = Approval.objects.create(
                resourcing_request=resourcing_request,
                user=user,
                reason=comment,
                type=approval_type,
                approved=approved,
            )

            setattr(resourcing_request, f"{approval_type}_approval", approval)

            EventLogService.add_event(
                content_object=resourcing_request,
                user=user,
                event_type=(
                    EventType.GROUP_APPROVED if approved else EventType.APPROVAL_CLEARED
                ),
                event_context={"group": Approval.Type(approval.type).label},
            )

            if resourcing_request.get_is_approved():
                resourcing_request.state = resourcing_request.State.APPROVED

                EventLogService.add_event(
                    content_object=resourcing_request,
                    user=user,
                    event_type=EventType.APPROVED,
                )

            resourcing_request.save()

        if action == ReviewAction.APPROVE:
            notify_approvers.delay(
                resourcing_request.pk,
                resourcing_request_url,
                approval.pk,
            )

            send_notification.delay(
                email_address=resourcing_request.requestor.contact_email,
                template_id=settings.GOVUK_NOTIFY_APPROVAL_TEMPLATE_ID,
                personalisation={
                    "first_name": resourcing_request.requestor.first_name,
                    "approved_or_rejected": "approved" if approved else "rejected",
                    "approver": user.get_full_name(),
                    "resourcing_request_url": resourcing_request_url,
                },
            )

        if action in (ReviewAction.COMMENT, ReviewAction.REQUEST_CHANGES):
            send_notification.delay(
                email_address=resourcing_request.requestor.contact_email,
                template_id=settings.GOVUK_NOTIFY_COMMENT_LEFT_TEMPLATE_ID,
                personalisation={
                    "first_name": resourcing_request.requestor.first_name,
                    "commenter": user.get_full_name(),
                    "resourcing_request_url": resourcing_request_url,
                },
            )

            EventLogService.add_event(
                content_object=resourcing_request,
                user=user,
                event_type=EventType.COMMENTED,
            )
