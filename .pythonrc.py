from types import SimpleNamespace

from main.models import ResourcingRequest  # noqa: F401
from user.models import User  # noqa: F401


user = SimpleNamespace(
    **{user.username.replace("-", "_"): user for user in User.objects.all()}
)
