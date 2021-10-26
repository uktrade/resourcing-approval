from .base import *


# Remove staff SSO and activate dev tools
MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")
MIDDLEWARE.append("dev_tools.middleware.DevToolsLoginRequiredMiddleware")
AUTHENTICATION_BACKENDS.remove("authbroker_client.backends.AuthbrokerBackend")
LOGIN_URL = reverse_lazy("dev_tools:index")
