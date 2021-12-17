import logging
from functools import partial
from typing import Any, Optional

from celery import group, shared_task
from django.conf import settings
from django.db.models.query_utils import Q
from notifications_python_client.notifications import NotificationsAPIClient

from main.constants import APPROVAL_TYPE_TO_GROUP, ApproverGroup
from main.models import Approval, ResourcingRequest
from user.models import User


logger = logging.getLogger(__name__)


@shared_task
def send_notification(to, template_id, personalisation=None):
    if personalisation is None:
        personalisation = {}

    if settings.APP_ENV in ("local", "test"):
        logging.info(
            "\n".join(
                (
                    f"GOVUK_NOTIFY_API_KEY={settings.GOVUK_NOTIFY_API_KEY}",
                    f"to={to}",
                    f"template_id={template_id}",
                    f"personalisation={personalisation}",
                )
            )
        )

        return

    notifications_client = NotificationsAPIClient(settings.GOVUK_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=to, template_id=template_id, personalisation=personalisation
    )


def send_group_notification(
    approver_group: ApproverGroup,
    user_filter: Optional[Q] = None,
    *,
    template_id: str,
    personalisation: Optional[dict[str, Any]] = None,
) -> None:
    if personalisation is None:
        personalisation = {}

    users = User.objects.filter(groups__name=approver_group.value)

    if user_filter:
        users = users.filter(user_filter)

    tasks = [
        send_notification.s(
            to=user.email,
            template_id=template_id,
            personalisation={
                **personalisation,
                "first_name": user.first_name,
            },
        )
        for user in users
    ]

    group(tasks).apply_async()


@shared_task
def notify_approvers(
    resourcing_request_pk: int,
    resourcing_request_url: str,
    approval_pk: Optional[int] = None,
) -> None:
    """Send a notification to the relevant approvers.

    Order of notifications:
        `Head of Profession -> Chief -> BusOps -> [HRBP, Finance, Commercial] -> Director -> DG COO`
    """

    resourcing_request: ResourcingRequest = (
        ResourcingRequest.objects.select_related_approvals().get(
            pk=resourcing_request_pk
        )
    )
    approval: Optional[Approval] = (
        Approval.objects.get(pk=approval_pk) if approval_pk else None
    )

    personalisation = {"resourcing_request_url": resourcing_request_url}

    send_ready_for_approval_group_notification = partial(
        send_group_notification,
        template_id=settings.GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID,
        personalisation=personalisation,
    )

    # Notify the head of profession group that the request has been send for approval.
    if not approval:
        send_ready_for_approval_group_notification(
            ApproverGroup.HEAD_OF_PROFESSION,
            Q(profession=resourcing_request.profession),
        )

        return

    # Notify the requestor that the request has been approved.
    if resourcing_request.is_approved:
        send_notification.delay(
            to=resourcing_request.requestor.email,
            template_id=settings.GOVUK_NOTIFY_APPROVED_TEMPLATE_ID,
            personalisation={
                **personalisation,
                "first_name": resourcing_request.requestor.first_name,
            },
        )

        return

    approval_index = next(
        i for i, approvals in enumerate(Approval.ORDER) if approval.type in approvals
    )

    # Do nothing if the request does not have the correct approvals.
    for approvals in Approval.ORDER[: approval_index + 1]:
        for approval_type in approvals:
            if resourcing_request.get_approval(approval_type) is None:
                return

    # Notify the correct approvers that the request is ready for their approval.
    try:
        next_approval_types = Approval.ORDER[approval_index + 1]
    except IndexError:
        next_approval_types = []

    for next_approval_type in next_approval_types:
        if resourcing_request.get_approval(next_approval_type) is not None:
            continue

        if next_approval_type == Approval.Type.CHIEF:
            send_notification.delay(
                to=resourcing_request.chief.email,
                template_id=settings.GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID,
                personalisation={
                    **personalisation,
                    "first_name": resourcing_request.chief.first_name,
                },
            )
        else:
            send_ready_for_approval_group_notification(
                APPROVAL_TYPE_TO_GROUP[next_approval_type]
            )
