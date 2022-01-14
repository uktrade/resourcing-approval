from main.models import (
    CestRationale,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
)
from main.views.supporting_documents import SupportingDocumentDetailView


class JobDescriptionDetailView(SupportingDocumentDetailView):
    model = JobDescription
    template_name = "main/jobdescription_detail.html"
    permission_required = "main.view_jobdescription"
    title = "Job description"
    stacked_fields = [
        "role_purpose",
        "key_accountabilities",
        "line_management_responsibility",
        "personal_attributes_and_skills",
        "essential_and_preferred_experience",
        "description",
    ]


class CestRationaleDetailView(SupportingDocumentDetailView):
    model = CestRationale
    permission_required = "main.view_cestrationale"
    title = "CEST rationale"
    stacked_fields = [
        "what",
        "how",
        "where",
        "when",
        "personal_service",
        "part_and_parcel",
        "financial_risk",
        "business_on_own_account",
    ]


class SdsStatusDeterminationDetailView(SupportingDocumentDetailView):
    model = SdsStatusDetermination
    permission_required = "main.view_sdsstatusdetermination"
    title = "SDS status determination"
    stacked_fields = ["reasons"]


class StatementOfWorkDetailView(SupportingDocumentDetailView):
    pk_url_kwarg = "statement_of_work_pk"
    model = StatementOfWork
    template_name = "main/statement_of_work_detail.html"
    permission_required = "main.view_statementofwork"
    title = "Statement of work"
    excluded_fields = [
        "id",
        "resourcing_request",
        "modules",
    ]
    stacked_fields = [
        "project_description",
        "notice_period",
        "fees",
        "exceptional_expenses",
        "deliverable_notes",
    ]

    def get_context_data(self, **kwargs):
        context = {
            "my_modules": self.object.modules.all(),
            "deliverable_exclude_list": [
                "id",
                "statement_of_work_module",
                "deliverable_title",
            ],
        }

        return super().get_context_data(**kwargs) | context
