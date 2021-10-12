from django.db.models.signals import pre_save
from django.dispatch import receiver

from main.models import ContractorApproval


@receiver(pre_save, sender=ContractorApproval)
def contractor_approval_pre_save(sender, instance, **kwargs):
    # TODO: Why do we need to use `int` here?
    if int(instance.status) == instance.Status.DRAFT:
        instance.clear_approvals()

    if instance.chief != instance.chief_approval_who:
        instance.chief_approval = None
        instance.chief_approval_who = None
        instance.chief_approval_when = None
