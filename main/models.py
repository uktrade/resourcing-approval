import datetime

from django.db import models
from django.urls import reverse

from chartofaccount.models import (
    CostCentre,
    DepartmentalGroup,
    Directorate,
    ProgrammeCode,
    ProjectCode,
)


TRUE_FALSE_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


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
        indexes = [models.Index(name="state_index", fields=["state"])]

    class State(models.IntegerChoices):
        DRAFT = 0, "Draft"
        AWAITING_APPROVALS = 1, "Awaiting approvals"
        APPROVED = 2, "Approved"

    requestor = models.ForeignKey(
        "user.User", models.CASCADE, related_name="resourcing_requests"
    )

    state = models.SmallIntegerField(choices=State.choices, default=State.DRAFT)

    name = models.CharField(max_length=255)
    is_ir35 = models.BooleanField(
        "Is the role inside IR35?", null=True, choices=TRUE_FALSE_CHOICES
    )
    chief = models.ForeignKey("user.User", models.CASCADE, related_name="+")

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

    objects = ResourcingRequestQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("resourcing-request-detail", kwargs={"pk": self.pk})

    @property
    def is_draft(self):
        return self.state == self.State.DRAFT

    @property
    def is_awaiting_approvals(self):
        return self.state == self.State.AWAITING_APPROVALS

    @property
    def required_supporting_forms(self):
        if self.is_ir35:
            yield self.job_description
        else:
            yield self.statement_of_work

        yield from (
            self.interim_request,
            self.cest_rationale,
            self.sds_status_determination,
        )

    @property
    def is_complete(self):
        return all(self.required_supporting_forms)

    @property
    def can_send_for_approval(self):
        return self.is_complete and self.state == self.State.DRAFT

    @property
    def can_update(self):
        return self.state == self.State.DRAFT

    @property
    def can_approve(self):
        return self.state == self.State.AWAITING_APPROVALS

    def get_approvals(self):
        return {
            Approval.Type.HEAD_OF_PROFESSION: self.head_of_profession_approval,
            Approval.Type.CHIEF: self.chief_approval,
            Approval.Type.BUSOPS: self.busops_approval,
            Approval.Type.HRBP: self.hrbp_approval,
            Approval.Type.FINANCE: self.finance_approval,
            Approval.Type.COMMERCIAL: self.commercial_approval,
        }

    def get_is_approved(self):
        return all(x and x.approved for x in self.get_approvals().values())


class Approval(models.Model):
    class Meta:
        permissions = (
            (
                "can_give_head_of_profession_approval",
                "Can give head of profession approval",
            ),
            ("can_give_busops_approval", "Can give BusOps approval"),
            ("can_give_chief_approval", "Can give chief approval"),
            ("can_give_hrbp_approval", "Can give HRBP approval"),
            ("can_give_finance_approval", "Can give finance approval"),
            ("can_give_commercial_approval", "Can give commercial approval"),
        )
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["type"])]

    class Type(models.TextChoices):
        HEAD_OF_PROFESSION = "head_of_profession", "Head of Profession"
        BUSOPS = "busops", "BusOps"
        CHIEF = "chief", "Chief"
        HRBP = "hrbp", "HRBP"
        FINANCE = "finance", "Finance"
        COMMERCIAL = "commercial", "Commercial"

    resourcing_request = models.ForeignKey(
        "ResourcingRequest", models.CASCADE, related_name="approvals"
    )
    user = models.ForeignKey("user.User", models.CASCADE, related_name="+")
    reason = models.OneToOneField(
        "Comment", models.CASCADE, null=True, related_name="reason"
    )

    type = models.CharField(choices=Type.choices, max_length=20)
    approved = models.BooleanField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class JobDescription(models.Model):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
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
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="statement_of_work",
    )

    company_name = models.CharField(max_length=255)
    slot_code = models.CharField(max_length=30)
    is_nominated_worker = models.BooleanField(
        "Did DDaT find them or not?", null=True, choices=TRUE_FALSE_CHOICES
    )
    hiring_manager_team_leader = models.CharField(
        "Hiring manager / Team lead (if different)", max_length=255
    )
    role = models.CharField(max_length=255)
    project_description = models.TextField()

    group = models.ForeignKey(
        DepartmentalGroup,
        on_delete=models.CASCADE,
        related_name="+",
    )

    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.CASCADE,
        related_name="+",
    )

    cost_centre_code = models.ForeignKey(
        CostCentre,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Cost Centre/Team",
    )

    programme_code = models.ForeignKey(
        ProgrammeCode,
        on_delete=models.CASCADE,
        related_name="+",
    )

    project_code = models.ForeignKey(
        ProjectCode,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    start_date = models.DateField()
    end_date = models.DateField()
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
        return self.company_name


class StatementOfWorkModule(models.Model):
    module_title = models.CharField(max_length=255)
    completion_date = models.DateField()
    statement_of_work = models.ForeignKey(
        StatementOfWork,
        on_delete=models.CASCADE,
        related_name="modules",
    )

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
        return self.module_count > 0

    def __str__(self):
        return self.module_title


class StatementOfWorkModuleDeliverable(models.Model):
    deliverable_title = models.CharField(max_length=255)
    deliverable_description = models.TextField()

    start_date = models.DateField()
    end_date = models.DateField()
    monthly_fee = models.DecimalField(max_digits=9, decimal_places=2)
    payment_date = models.DateField()
    statement_of_work_module = models.ForeignKey(
        StatementOfWorkModule,
        on_delete=models.CASCADE,
        related_name="deliverables",
    )

    @property
    def resourcing_request(self):
        return self.statement_of_work_module.resourcing_request

    @property
    def resourcing_request_id(self):
        return self.statement_of_work_module.resourcing_request_id

    def __str__(self):
        return self.deliverable_title


class InterimRequest(models.Model):
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

    project_name_role_title = models.CharField(
        max_length=255, verbose_name="Project name/ Title of the Role"
    )
    new_requirement = models.BooleanField(
        verbose_name="New", choices=TRUE_FALSE_CHOICES
    )
    name_of_contractor = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="If Nominated Worker - please provide Name of the contractor",
    )
    uk_based = models.BooleanField(
        default=True, verbose_name="UK based", choices=TRUE_FALSE_CHOICES
    )
    overseas_country = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="if Overseas which Country"
    )
    start_date = models.DateField(verbose_name="Anticipated Start Date")
    end_date = models.DateField(verbose_name="Anticipated End Date")
    type_of_security_clearance = models.CharField(
        max_length=50,
        choices=SECURITY_CLEARANCE_CHOICES,
        verbose_name="Level of Security clearance required",
    )
    contractor_type = models.CharField(
        max_length=50,
        choices=CONTRACTOR_TYPE_CHOICES,
        verbose_name="Category of Interim",
    )
    part_b_business_case = models.TextField(
        verbose_name="Business Case",
        help_text=("Please detail why the interim resource is required"),
    )
    part_b_impact = models.TextField(
        verbose_name="Impact",
        help_text="What would be the impact of not filling this requirement.",
    )
    part_b_main_reason = models.TextField(
        verbose_name="",
        help_text="What are the main reasons why this role has not been filled by a substantive Civil Servant. Please detail the strategic workforce plan for this role after the assignment end date:",
    )

    group = models.ForeignKey(
        DepartmentalGroup,
        on_delete=models.CASCADE,
        related_name="+",
    )

    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.CASCADE,
        related_name="+",
    )

    cost_centre_code = models.ForeignKey(
        CostCentre,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Cost Centre/Team",
    )

    slot_codes = models.CharField(max_length=255)

    def __str__(self):
        return "Interim request"


class CestRationale(models.Model):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="cest_rationale",
    )
    role_start_date = models.DateField()
    role_end_date = models.DateField()
    worker_name = models.CharField(max_length=50, blank=True, null=True)
    cover_for_perm_role = models.BooleanField(choices=TRUE_FALSE_CHOICES)
    role_description = models.TextField()
    what = models.CharField(max_length=50, verbose_name="Control & Direction: what")
    how = models.CharField(max_length=50, verbose_name="Control & Direction: how")
    where = models.CharField(max_length=50, verbose_name="Control & Direction: where")
    when = models.CharField(max_length=50, verbose_name="Control & Direction: when")
    personal_service = models.TextField()
    part_and_parcel = models.TextField()
    financial_risk = models.TextField()
    business_on_own_account = models.TextField()
    supply_chain = models.CharField(max_length=255)

    def __str__(self):
        return "CEST rationale"


class SdsStatusDetermination(models.Model):
    resourcing_request = models.OneToOneField(
        "ResourcingRequest",
        models.CASCADE,
        related_name="sds_status_determination",
    )
    company_name = models.CharField(max_length=255)
    worker_name = models.CharField(max_length=255)
    agency = models.CharField(max_length=255)
    start_date = models.DateField(verbose_name="Contract/Extension Start Date")
    end_date = models.DateField(verbose_name="Contract End Date")
    completed_by  = models.ForeignKey("user.User", models.CASCADE, related_name="+")
    on_behalf_of = models.CharField(max_length=255)
    date_completed = models.DateField(default=datetime.date.today)
    reasons = models.TextField()

    def __str__(self):
        return "SDS status determination"


class Comment(models.Model):
    resourcing_request = models.ForeignKey(
        "ResourcingRequest", models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey("user.User", models.CASCADE, related_name="comments")

    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField("Add a comment")
