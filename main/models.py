from django.db import models


TRUE_FALSE_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class ContractorApproval(models.Model):
    flow = models.OneToOneField(
        "django_workflow_engine.Flow",
        models.CASCADE,
        related_name="contractor_approval",
    )

    is_ir35 = models.BooleanField(null=True, choices=TRUE_FALSE_CHOICES)
