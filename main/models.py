import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import date, truncatechars
from django.urls import reverse
from django.utils.safestring import mark_safe

from change_log.models import ChangeLogRelation
from chartofaccount.models import (
    CostCentre,
    DepartmentalGroup,
    Directorate,
    ProgrammeCode,
    ProjectCode,
)
from main.templatetags.currency import currency
from quill.db.models.fields import QuillField
from quill.forms.widgets import QuillWidget
from quill.utils import extract_text


if TYPE_CHECKING:
    from user.models import User


TRUE_FALSE_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class Profession(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ResourcingRequestQuerySet(models.QuerySet):
    def select_related_approvals(self):
        return self.select_related(
            "head_of_profession_approval",
            "chief_approval",
            "busops_approval",
            "hrbp_approval",
            "finance_approval",
            "commercial_approval",
        )


class ResourcingRequest(models.Model):
    class Meta:
        permissions = (
            ("view_all_resourcingrequests", "Can view all resourcing requests"),
        )
        indexes = [models.Index(name="state_index", fields=["state"])]

    class State(models.IntegerChoices):
        DRAFT = 0, "Draft"
        AWAITING_APPROVALS = 1, "Awaiting approvals"
        AMENDING = 2, "Amending"
        AMENDMENTS_REVIEW = 3, "Amendments review"
        APPROVED = 4, "Approved"
        COMPLETED = 5, "Completed"

    class Type(models.IntegerChoices):
        NEW = 1, "New"

    requestor = models.ForeignKey(
        "user.User", models.CASCADE, related_name="resourcing_requests"
    )

    state = models.SmallIntegerField(
        "Status", choices=State.choices, default=State.DRAFT
    )

    type = models.SmallIntegerField(choices=Type.choices, default=Type.NEW)
    job_title = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    portfolio = models.CharField(max_length=50, null=True, blank=True)
    profession = models.ForeignKey("Profession", models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    is_ir35 = models.BooleanField(
        "Is the role inside IR35?",
        null=True,
        choices=TRUE_FALSE_CHOICES,
        help_text=mark_safe(
            "IR35 covers off-payroll working rules. So inside IR35 contractors not on"
            " the payroll pay broadly the same Income Tax and National Insurance"
            " contributions as employees. You can read more about IR35"
            ' <a class="govuk-link" href="https://www.gov.uk/guidance/understanding-off-payroll-working-ir35" target="_blank">here</a>.'
        ),
    )
    chief = models.ForeignKey(
        "user.User", models.CASCADE, verbose_name="Chief/SMT sponsor", related_name="+"
    )

    # Approvals
    head_of_profession_approval = models.OneToOneField(
        "Approval",
        models.SET_NULL,
        related_name="head_of_profession_approval",
        null=True,
    )
    chief_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="chief_approval", null=True
    )
    busops_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="busops_approval", null=True
    )
    hrbp_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="hrbp_approval", null=True
    )
    finance_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="finance_approval", null=True
    )
    commercial_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="commercial_approval", null=True
    )
    director_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="director_approval", null=True
    )
    dg_coo_approval = models.OneToOneField(
        "Approval", models.SET_NULL, related_name="dg_coo_approval", null=True
    )

    event_log = GenericRelation("event_log.Event")
    change_log = ChangeLogRelation("change_log.Change")

    objects = ResourcingRequestQuerySet.as_manager()

    def __str__(self):
        return f"{self.job_title} for {self.project_name}"

    def get_absolute_url(self):
        return reverse(
            "resourcing-request-detail", kwargs={"resourcing_request_pk": self.pk}
        )

    @property
    def is_draft(self) -> bool:
        """Return whether the resourcing request is in draft."""
        return self.state == self.State.DRAFT

    @property
    def is_awaiting_approvals(self) -> bool:
        """Return whether the resourcing request is awaiting approvals."""
        return self.state == self.State.AWAITING_APPROVALS

    @property
    def is_amending(self) -> bool:
        """Return whether the resourcing request is being amended."""
        return self.state == self.State.AMENDING

    @property
    def is_amendments_review(self) -> bool:
        """Return whether the resourcing request is in amendments review."""
        return self.state == self.State.AMENDMENTS_REVIEW

    @property
    def is_approved(self) -> bool:
        """Return whether the resourcing request has been approved."""
        return self.state == self.State.APPROVED

    @property
    def is_completed(self) -> bool:
        """Return whether the resourcing request is completed."""
        return self.state == self.State.COMPLETED

    @property
    def required_supporting_forms(self):
        yield hasattr(self, "financial_information")

        if self.is_ir35:
            yield hasattr(self, "job_description")
        else:
            if hasattr(self, "statement_of_work"):
                yield self.statement_of_work.is_statement_of_work_valid
            else:
                yield False

        yield from (
            hasattr(self, "interim_request"),
            hasattr(self, "cest_document"),
            hasattr(self, "sds_status_determination"),
        )

    @property
    def is_complete(self):
        return all(self.required_supporting_forms)

    @property
    def can_send_for_approval(self) -> bool:
        """Return whether we can send this resourcing request for approval."""
        return self.is_complete and self.state == self.State.DRAFT

    @property
    def can_update(self) -> bool:
        """Return whether we can update this resourcing request."""
        return self.state in (self.State.DRAFT, self.State.AMENDING)

    @property
    def can_amend(self) -> bool:
        """Return whether we can amend this resourcing request."""
        return self.state in (
            self.State.AWAITING_APPROVALS,
            self.State.AMENDMENTS_REVIEW,
        )

    @property
    def can_send_for_review(self) -> bool:
        """Return whether we can send this resourcing request for review."""
        return self.state == self.State.AMENDING

    @property
    def can_clear_approval(self) -> bool:
        """Return whether an approval can be cleared."""
        return self.state == self.State.AMENDMENTS_REVIEW

    @property
    def can_finish_amendments_review(self) -> bool:
        """Return whether we can finish the amendments review"""
        return self.state == self.State.AMENDMENTS_REVIEW

    @property
    def can_approve(self):
        return self.state == self.State.AWAITING_APPROVALS

    @property
    def can_mark_as_complete(self):
        return self.is_approved

    def get_approval(self, approval_type):
        return getattr(self, f"{approval_type.value}_approval")

    def get_approvals(self):
        return {
            Approval.Type.HEAD_OF_PROFESSION: self.head_of_profession_approval,
            Approval.Type.CHIEF: self.chief_approval,
            Approval.Type.BUSOPS: self.busops_approval,
            Approval.Type.HRBP: self.hrbp_approval,
            Approval.Type.FINANCE: self.finance_approval,
            Approval.Type.COMMERCIAL: self.commercial_approval,
            Approval.Type.DIRECTOR: self.director_approval,
            Approval.Type.DG_COO: self.dg_coo_approval,
        }

    def get_is_approved(self):
        return all(x and x.approved for x in self.get_approvals().values())

    def can_user_approve(self, user: "User") -> bool:
        """Return whether the user can approve this resourcing request."""
        if self.can_approve:
            if user.is_superuser:
                return True

            # Is the user the correct head of profession?
            if user.is_head_of_profession and user.profession == self.profession:
                return True

            # Is the user another type of approver?
            if not user.is_head_of_profession and user.is_approver:
                return True

        # If in review (can clear approval), is the user from busops?
        if self.can_clear_approval and user.is_busops:
            return True

        return False


class Approval(models.Model):
    class Meta:
        permissions = (
            (
                "can_give_head_of_profession_approval",
                "Can give head of profession approval",
            ),
            ("can_give_busops_approval", "Can give workforce planning approval"),
            ("can_give_chief_approval", "Can give chief approval"),
            ("can_give_hrbp_approval", "Can give HR business partners approval"),
            ("can_give_finance_approval", "Can give finance approval"),
            ("can_give_commercial_approval", "Can give commercial approval"),
            ("can_give_director_approval", "Can give director approval"),
            (
                "can_give_dg_coo_approval",
                "Can give DG COO approval",
            ),
        )
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["type"])]

    class Type(models.TextChoices):
        HEAD_OF_PROFESSION = "head_of_profession", "Head of Profession"
        CHIEF = "chief", "Chief"
        BUSOPS = "busops", "Workforce Planning"
        HRBP = "hrbp", "HR Business Partners"
        FINANCE = "finance", "Finance"
        COMMERCIAL = "commercial", "Commercial"
        # Jason Kitcat at time of writing.
        DIRECTOR = "director", "Director"
        # Catherine Vaughan at time of writing.
        DG_COO = "dg_coo", "DG COO"

    ORDER = [
        [Type.HEAD_OF_PROFESSION],
        [Type.CHIEF],
        [Type.BUSOPS],
        [
            Type.HRBP,
            Type.FINANCE,
            Type.COMMERCIAL,
        ],
        [Type.DIRECTOR],
        [Type.DG_COO],
    ]

    resourcing_request = models.ForeignKey(
        "ResourcingRequest", models.CASCADE, related_name="approvals"
    )
    user = models.ForeignKey("user.User", models.CASCADE, related_name="+")
    reason = models.OneToOneField(
        "Comment",
        models.CASCADE,
        null=True,
        related_name="reason",
        verbose_name="Additional information",
        help_text=(
            "If you don't approve the case and need more information or want to"
            " approve with a conditional change add your note and select 'Reviewed'."
        ),
    )

    type = models.CharField("role", choices=Type.choices, max_length=20)
    approved = models.BooleanField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class SupportingInformation(models.Model):
    class Meta:
        abstract = True

    change_log = ChangeLogRelation("change_log.Change")


class JobDescription(models.Model):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="job_description",
    )

    description = QuillField()

    def __str__(self):
        return truncatechars(extract_text(self.description).replace("\n", " "), 40)

    def get_absolute_url(self):
        return reverse(
            "job-description-detail",
            kwargs={
                "resourcing_request_pk": self.resourcing_request.pk,
                "supporting_document_pk": self.pk,
            },
        )

    def get_description_display(self):
        return QuillWidget().render(
            "description",
            json.dumps(self.description),
            attrs={"read_only": True},
        )


class FinancialInformation(SupportingInformation):
    class AreaOfWork(models.TextChoices):
        DDAT = "ddat", "DDaT"

    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="financial_information",
    )

    group = models.ForeignKey(
        DepartmentalGroup,
        on_delete=models.PROTECT,
        related_name="+",
    )
    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.PROTECT,
        related_name="+",
    )
    cost_centre_code = models.ForeignKey(
        CostCentre,
        models.PROTECT,
        verbose_name="Cost Centre/Team",
        related_name="+",
    )
    team = models.CharField(max_length=64)
    programme_code = models.ForeignKey(
        ProgrammeCode,
        models.PROTECT,
        related_name="+",
    )
    area_of_work = models.CharField(
        "Area of work for VAT reclaim", max_length=255, choices=AreaOfWork.choices
    )
    total_budget = models.IntegerField(
        "Total Budget, including sourcing fees, expenses and interim labour cost"
    )
    timesheet_and_expenses_validator = models.CharField(
        "name of the first timesheet and expenses validator", max_length=255
    )
    second_timesheet_validator = models.CharField(
        "name of the second timesheet and expenses validator", max_length=255
    )
    min_day_rate = models.IntegerField(
        "Minimum anticipated day rate", null=True, blank=True
    )
    max_day_rate = models.IntegerField(
        "Maximum anticipated day rate", null=True, blank=True
    )
    days_required = models.IntegerField(
        "Total number of days required", null=True, blank=True
    )
    project_fees = models.IntegerField(
        "Total project fees (exclude VAT)", null=True, blank=True
    )

    def __str__(self) -> str:
        text = [f"Cost centre: {self.cost_centre_code}"]

        if self.resourcing_request.is_ir35:
            text.append(
                f"Day rate: {currency(self.min_day_rate)}"
                f" - {currency(self.max_day_rate)}"
            )
        else:
            text.append(f"Project fees: {currency(self.project_fees)}")

        return " / ".join(text)

    def get_absolute_url(self):
        return reverse(
            "financial-information-detail",
            kwargs={
                "resourcing_request_pk": self.resourcing_request.pk,
                "supporting_document_pk": self.pk,
            },
        )

    def get_total_budget_display(self):
        return currency(self.total_budget)

    def get_min_day_rate_display(self):
        return currency(self.min_day_rate)

    def get_max_day_rate_display(self):
        return currency(self.max_day_rate)

    def get_project_fees_display(self):
        return currency(self.project_fees)


class StatementOfWork(SupportingInformation):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="statement_of_work",
    )

    company_name = models.CharField(max_length=255)
    position_code = models.CharField(max_length=30)
    is_nominated_worker = models.BooleanField(
        "Did DDaT find them or not?", null=True, choices=TRUE_FALSE_CHOICES
    )
    hiring_manager_team_leader = models.CharField(
        "Hiring manager / Team lead (if different)", max_length=255
    )
    project_description = models.TextField()

    project_code = models.ForeignKey(
        ProjectCode,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    notice_period = models.TextField()
    fees = models.TextField("Project fee and invoicing")
    exceptional_expenses = models.TextField()
    deliverable_notes = models.TextField()

    @property
    def module_count(self) -> int:
        return self.modules.all().count()

    @property
    def is_statement_of_work_valid(self) -> bool:
        # Check that there is at least one module defined,
        # and every module defined has at least one deliverable.
        if self.module_count == 0:
            return False
        for module in self.modules.all():
            if not module.is_module_valid:
                return False
        return True

    def __str__(self):
        return (
            f"Company name: {self.company_name} / Position code: {self.position_code}"
        )

    def get_absolute_url(self):
        return reverse(
            "statement-of-work-detail",
            kwargs={
                "resourcing_request_pk": self.resourcing_request.pk,
                "statement_of_work_pk": self.pk,
            },
        )


class StatementOfWorkModule(SupportingInformation):
    statement_of_work = models.ForeignKey(
        StatementOfWork,
        on_delete=models.CASCADE,
        related_name="modules",
    )

    module_title = models.CharField(max_length=255)
    completion_date = models.DateField()

    @property
    def resourcing_request(self):
        return self.statement_of_work.resourcing_request

    @property
    def resourcing_request_id(self):
        return self.statement_of_work.resourcing_request_id

    @property
    def deliverable_count(self) -> int:
        return self.deliverables.all().count()

    @property
    def is_module_valid(self) -> bool:
        # Check that there is at least one deliverable defined,
        return self.deliverable_count > 0

    @property
    def get_deliverables(self):
        return self.deliverables.all()

    def __str__(self):
        return self.module_title

    def get_absolute_url(self):
        return self.statement_of_work.get_absolute_url()


class StatementOfWorkModuleDeliverable(SupportingInformation):
    statement_of_work_module = models.ForeignKey(
        StatementOfWorkModule,
        on_delete=models.CASCADE,
        related_name="deliverables",
    )

    deliverable_title = models.CharField(max_length=255)
    deliverable_description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_fee = models.DecimalField(max_digits=9, decimal_places=2)
    payment_date = models.DateField()

    @property
    def resourcing_request(self):
        return self.statement_of_work_module.resourcing_request

    @property
    def resourcing_request_id(self):
        return self.statement_of_work_module.resourcing_request_id

    def __str__(self):
        return self.deliverable_title

    def get_absolute_url(self):
        return self.statement_of_work_module.statement_of_work.get_absolute_url()


class InterimRequest(SupportingInformation):
    class CivilServantGrade(models.TextChoices):
        AO = "AO", "AO"
        EO = "EO", "EO"
        HEO = "HEO", "HEO"
        SEO = "SEO", "SEO"
        G6 = "G6", "G6"
        G7 = "G7", "G7"

    class Supplier(models.TextChoices):
        GREEN_PARK = "green park", "Green Park"
        PSR = "psr", "PSR"

    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="interim_request",
    )

    CONTRACTOR_TYPE_GENERALIST = "generalist"
    CONTRACTOR_TYPE_SPECIALIST = "specialist"
    CONTRACTOR_TYPE_CHOICES = [
        (CONTRACTOR_TYPE_GENERALIST, "Generalist"),
        (CONTRACTOR_TYPE_SPECIALIST, "Specialist"),
    ]
    SECURITY_CLEARANCE_BPSS = "BPSS"
    SECURITY_CLEARANCE_SC = "sc"
    SECURITY_CLEARANCE_DV = "dv"
    SECURITY_CLEARANCE_CTC = "ctc"
    SECURITY_CLEARANCE_CHOICES = [
        (SECURITY_CLEARANCE_BPSS, "BPSS"),
        (SECURITY_CLEARANCE_SC, "SC"),
        (SECURITY_CLEARANCE_DV, "DV"),
        (SECURITY_CLEARANCE_CTC, "CTC"),
    ]

    uk_based = models.BooleanField(
        default=True, verbose_name="UK based", choices=TRUE_FALSE_CHOICES
    )
    overseas_country = models.ForeignKey(
        "countries.Country",
        on_delete=models.PROTECT,
        verbose_name="if overseas which country?",
        null=True,
        blank=True,
    )
    type_of_security_clearance = models.CharField(
        max_length=50,
        choices=SECURITY_CLEARANCE_CHOICES,
        verbose_name="Level of security clearance required",
    )
    contractor_type = models.CharField(
        max_length=50,
        choices=CONTRACTOR_TYPE_CHOICES,
        verbose_name="Type of interim required",
    )
    position_code = models.CharField(max_length=30)
    equivalent_civil_servant_grade = models.CharField(
        max_length=4, choices=CivilServantGrade.choices
    )
    supplier = models.CharField(max_length=20, choices=Supplier.choices)
    part_b_business_case = models.TextField(
        verbose_name="Business case",
        help_text="Explain why an interim resource is needed.",
    )
    part_b_impact = models.TextField(
        verbose_name="Impact",
        help_text="Explain the impact of not getting this resource.",
    )
    part_b_main_reason = models.TextField(
        verbose_name="Justification",
        help_text=(
            "Why has this role not been filled by a substantive civil servant? What is"
            " the strategic workforce plan for this role after the contract end date?"
        ),
    )

    def __str__(self):
        return (
            f"Security clearance: {self.get_type_of_security_clearance_display()}"
            f" / Contractor type: {self.get_contractor_type_display()}"
        )

    def get_absolute_url(self):
        return reverse(
            "interim-request-detail",
            kwargs={
                "resourcing_request_pk": self.resourcing_request.pk,
                "supporting_document_pk": self.pk,
            },
        )


def resourcing_request_directory_path(instance, filename):
    return f"resourcing_request/{instance.resourcing_request.pk}/{filename}"


class CestDocument(models.Model):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="cest_document",
    )

    file = models.FileField(
        upload_to=resourcing_request_directory_path,
        validators=[FileExtensionValidator(["pdf"])],
        help_text=mark_safe(
            'Use the <a class="govuk-link" target="_blank" href="https://www.gov.uk/guidance/check-employment-status-for-tax">CEST tool</a>'
            ", this will generate a PDF which should be uploaded here."
            "<br>The link to the current file will time out after 5 minutes."
            " If it has timed out, refresh the page to update the link."
        ),
    )

    def __str__(self):
        return Path(self.file.name).name

    def get_absolute_url(self):
        return reverse(
            "resourcing-request-detail",
            kwargs={"resourcing_request_pk": self.resourcing_request.pk},
        )


class SdsStatusDetermination(SupportingInformation):
    class Meta:
        verbose_name = "status determination statement (SDS)"

    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="sds_status_determination",
    )

    company_name = models.CharField(max_length=255)
    worker_name = models.CharField("worker's name", max_length=255)
    agency = models.CharField(max_length=255)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    on_behalf_of = models.CharField(max_length=255)
    date_completed = models.DateField(default=datetime.date.today)
    reasons = models.TextField()

    def __str__(self):
        return (
            f"Start date: {date(self.contract_start_date, 'DATE_FORMAT')}"
            f" / End date: {date(self.contract_end_date, 'DATE_FORMAT')}"
        )

    def get_absolute_url(self):
        return reverse(
            "sds-status-determination-detail",
            kwargs={
                "resourcing_request_pk": self.resourcing_request.pk,
                "supporting_document_pk": self.pk,
            },
        )


class Comment(models.Model):
    class Meta:
        ordering = ["-timestamp"]

    resourcing_request = models.ForeignKey(
        "ResourcingRequest", models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey("user.User", models.CASCADE, related_name="comments")

    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(
        "Add a comment",
        help_text=(
            "You can provide additional information at any stage of the process,"
            " by adding a comment."
        ),
    )
