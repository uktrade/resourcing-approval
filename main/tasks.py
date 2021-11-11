import logging
from functools import partial
from typing import Optional

from celery import group, shared_task
from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient

from main.constants import ApproverGroup
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


@shared_task
def notify_approvers(
    resourcing_request_pk: int,
    resourcing_request_url: str,
    approval_pk: Optional[int] = None,
) -> None:
    """Send a notification to the relevant approvers.

    Order of notifications:
        `Head of Profession -> Chief -> BusOps -> [HRBP, Finance, Commercial]`
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

    send_to_group = partial(
        _send_ready_for_approval_notification_to_group, personalisation=personalisation
    )

    # Notify the head of profession group that the request has been send for approval.
    if not approval:
        send_to_group(ApproverGroup.HEAD_OF_PROFESSION)

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

    # Do nothing if the request does not have the correct approvals.
    if not resourcing_request.has_prerequisite_approvals(approval.type):
        return

    # Notify the correct approvers that the request is ready for their approval.
    if (
        approval.type == approval.Type.HEAD_OF_PROFESSION
        and not resourcing_request.chief_approval
    ):
        send_notification.delay(
            to=resourcing_request.chief.email,
            template_id=settings.GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID,
            personalisation={
                **personalisation,
                "first_name": resourcing_request.chief.first_name,
            },
        )
    elif (
        approval.type == approval.Type.CHIEF and not resourcing_request.busops_approval
    ):
        send_to_group(ApproverGroup.BUSOPS)
    elif approval.type == approval.Type.BUSOPS:
        if not resourcing_request.hrbp_approval:
            send_to_group(ApproverGroup.HRBP)
        if not resourcing_request.finance_approval:
            send_to_group(ApproverGroup.FINANCE)
        if not resourcing_request.commercial_approval:
            send_to_group(ApproverGroup.COMMERCIAL)


def _send_ready_for_approval_notification_to_group(
    approver_group: ApproverGroup, personalisation=None
) -> None:
    if personalisation is None:
        personalisation = {}

    group(
        (
            send_notification.s(
                to=user.email,
                template_id=settings.GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID,
                personalisation={
                    **personalisation,
                    "first_name": user.first_name,
                },
            )
            for user in User.objects.filter(groups__name=approver_group.value)
        )
    ).apply_async()
