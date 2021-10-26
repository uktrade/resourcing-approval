from main.models import Approval


def get_user_related_approval_types(user):
    for approval_type in Approval.Type:
        if user.has_perm(f"main.can_give_{approval_type.value}_approval"):
            yield approval_type
