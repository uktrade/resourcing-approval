from enum import Enum

from django.db import models
from django.db.models import Q
from django.db.models.expressions import F
from django.urls import reverse
from django.utils import timezone


TRUE_FALSE_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class ResourcingApproval(models.Model):
    class Meta:
        permissions = (
            ("can_give_chief_approval", "Can give chief approval"),
            ("can_give_hrbp_approval", "Can give HRBP approval"),
            ("can_give_finance_approval", "Can give finance approval"),
            ("can_give_commercial_approval", "Can give commercial approval"),
        )
        indexes = [models.Index(name="status_index", fields=["status"])]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(
                        status=0,
                        chief_approval__isnull=True,
                        hrbp_approval__isnull=True,
                        finance_approval__isnull=True,
                        commercial_approval__isnull=True,
                    )
                    | Q(
                        status=1,
                    )
                    | Q(
                        status=2,
                        chief_approval=True,
                    )
                    | Q(
                        status=3,
                        chief_approval=True,
                        hrbp_approval=True,
                        finance_approval=True,
                        commercial_approval=True,
                    )
                ),
                name="check_status",
            ),
            models.CheckConstraint(
                check=Q(chief_approval_who=F("chief")), name="check_chief"
            ),
        ]

    class Status(models.IntegerChoices):
        DRAFT = 0, "Draft"
        AWAITING_CHIEF_APPROVAL = 1, "Awaiting chief approval"
        AWAITING_APPROVALS = 2, "Awaiting approvals"
        APPROVED = 3, "Approved"

    class Approval(Enum):
        CHIEF = "chief"
        HRBP = "hrbp"
        FINANCE = "finance"
        COMMERCIAL = "commercial"

    requestor = models.ForeignKey("user.User", models.CASCADE, related_name="approvals")

    status = models.SmallIntegerField(choices=Status.choices, default=Status.DRAFT)

    name = models.CharField(max_length=255)
    is_ir35 = models.BooleanField(
        "Is the role inside IR35?", null=True, choices=TRUE_FALSE_CHOICES
    )
    chief = models.ForeignKey("user.User", models.CASCADE, related_name="+")

    # Approvals
    chief_approval = models.BooleanField(choices=TRUE_FALSE_CHOICES, null=True)
    chief_approval_who = models.ForeignKey(
        "user.User", models.CASCADE, null=True, related_name="+"
    )
    chief_approval_when = models.DateTimeField(null=True)

    hrbp_approval = models.BooleanField(
        "HRBP approval", choices=TRUE_FALSE_CHOICES, null=True
    )
    hrbp_approval_who = models.ForeignKey(
        "user.User", models.CASCADE, null=True, related_name="+"
    )
    hrbp_approval_when = models.DateTimeField(null=True)

    finance_approval = models.BooleanField(choices=TRUE_FALSE_CHOICES, null=True)
    finance_approval_who = models.ForeignKey(
        "user.User", models.CASCADE, null=True, related_name="+"
    )
    finance_approval_when = models.DateTimeField(null=True)

    commercial_approval = models.BooleanField(choices=TRUE_FALSE_CHOICES, null=True)
    commercial_approval_who = models.ForeignKey(
        "user.User", models.CASCADE, null=True, related_name="+"
    )
    commercial_approval_when = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("approval-detail", kwargs={"pk": self.pk})

    @property
    def can_send_to_chief(self):
        if self.status != self.Status.DRAFT:
            return False

        if self.is_ir35 and not self.job_description:
            return False

        if not self.is_ir35 and not self.statement_of_work:
            return False

        return all(
            [
                self.interim_request,
                self.cest_rationale,
                self.sds_status_determination,
            ]
        )

    def send_to_chief(self):
        self.status = self.Status.AWAITING_CHIEF_APPROVAL
        # TODO: Notify chief

    @property
    def can_chief_approve(self):
        return self.status == self.Status.AWAITING_CHIEF_APPROVAL

    def chief_approves(self):
        self.status = self.Status.AWAITING_APPROVALS

    def approve(self, approval, user):
        setattr(self, f"{approval}_approval", True)
        setattr(self, f"{approval}_approval_who", user)
        setattr(self, f"{approval}_approval_when", timezone.now())

        if approval == "chief":
            self.chief_approves()

        if self.approved:
            self.status = self.Status.APPROVED

    def reject(self, approval, user):
        setattr(self, f"{approval}_approval", False)
        setattr(self, f"{approval}_approval_who", user)
        setattr(self, f"{approval}_approval_when", timezone.now())

        if approval == "chief":
            self.status = self.Status.AWAITING_CHIEF_APPROVAL

    @property
    def can_mark_as_draft(self):
        return self.status in (
            self.Status.AWAITING_CHIEF_APPROVAL,
            self.Status.AWAITING_APPROVALS,
        )

    def mark_as_draft(self):
        self.status = self.Status.DRAFT
        self.clear_approvals()

    def clear_approvals(self):
        for approval in self.Approval:
            setattr(self, f"{approval.value}_approval", None)
            setattr(self, f"{approval.value}_approval_who", None)
            setattr(self, f"{approval.value}_approval_when", None)

    @property
    def can_edit(self):
        return self.status == self.Status.DRAFT

    @property
    def can_approve(self):
        return self.status in (
            self.Status.AWAITING_CHIEF_APPROVAL,
            self.Status.AWAITING_APPROVALS,
        )

    @property
    def approvals(self):
        return (
            self.chief_approval,
            self.hrbp_approval,
            self.finance_approval,
            self.commercial_approval,
        )

    @property
    def approved(self):
        return all(self.approvals)


class JobDescription(models.Model):
    approval = models.OneToOneField(
        "ResourcingApproval",
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

    def __str__(self):
        return self.title


class StatementOfWork(models.Model):
    approval = models.OneToOneField(
        "ResourcingApproval",
        models.CASCADE,
        related_name="statement_of_work",
    )

    company_name = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name


class InterimRequest(models.Model):
    approval = models.OneToOneField(
        "ResourcingApproval",
        models.CASCADE,
        related_name="interim_request",
    )

    todo = models.TextField()

    def __str__(self):
        return "Interim request"


class CestRationale(models.Model):
    approval = models.OneToOneField(
        "ResourcingApproval",
        models.CASCADE,
        related_name="cest_rationale",
    )

    todo = models.TextField()

    def __str__(self):
        return "CEST rationale"


class SdsStatusDetermination(models.Model):
    approval = models.OneToOneField(
        "ResourcingApproval",
        models.CASCADE,
        related_name="sds_status_determination",
    )

    todo = models.TextField()

    def __str__(self):
        return "SDS status determination"


class Comment(models.Model):
    approval = models.ForeignKey(
        "ResourcingApproval", models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey("user.User", models.CASCADE, related_name="comments")

    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField("Add a comment")
