from .base import *  # noqa: F403
from .paas import *  # noqa: F403


init_sentry()  # noqa: F405

ALLOWED_HOSTS = [
    "resourcing-approval.london.cloudapps.digital",
    "contractor-approval.london.cloudapps.digital",
    "get-contractor-approval.trade.gov.uk",
]
