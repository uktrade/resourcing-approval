import logging

from celery import shared_task
from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient


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
