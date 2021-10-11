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


class JobDescription(models.Model):
    approval = models.OneToOneField(
        "ContractorApproval",
        models.CASCADE,
        related_name="job_description",
    )

    title = models.CharField("Vacancy Title", max_length=255)
    role_purpose = models.TextField(
        help_text=(
            "Use this space to outline what the person is responsible for delivering"
            " and how this contributes to the success of the department. More detail on"
            " this will be added in the next section."
        ),
    )
    key_accountabilities = models.TextField(
        help_text=(
            "Outline what the individual needs to do in order to achieve to"
            " deliverables outlined above."
        ),
    )
    line_management_responsibility = models.TextField()
    personal_attributes_and_skills = models.TextField(
        help_text=(
            "Insert information about what the ideal candidate would be like in their"
            " character and what they’d bring to your team. This will enhance our"
            " search ability and interview quality."
        )
    )
    essential_and_preferred_experience = models.TextField(
        help_text=(
            "You must ensure the successful candidate meets your specification"
            " entirely, so do not put expectations that are not vital."
            "\n\n"
            "The diversity of applicants you receive to roles increases when shorter"
            " lists of personal and experience requirements are listed, which creates a"
            " better pool of candidates to select from at interview."
        )
    )
