from .non_prod import *  # noqa: F403


init_sentry()  # noqa: F405

ALLOWED_HOSTS = [
    "resourcing-approval-dev.london.cloudapps.digital",
    "resourcing-approval.dev.uktrade.digital",
]
