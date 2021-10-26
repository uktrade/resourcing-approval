from django.contrib.auth.models import AbstractUser

from main.models import Approval


class User(AbstractUser):
    def __str__(self):
        return self.get_full_name() or self.get_username()

    @property
    def is_approver(self):
        return any(
            self.has_perm(f"main.can_give_{x.value}_approval") for x in Approval.Type
        )

    def has_approval_perm(self, approval_type):
        return self.has_perm(f"main.can_give_{approval_type.value}_approval")
