from .non_prod import *  # noqa: F403
from .paas import *  # noqa: F403


init_sentry()  # noqa: F405

ALLOWED_HOSTS = [
    "resourcing-approval-dev.london.cloudapps.digital",
    "contractor-approval-dev.london.cloudapps.digital",
]
