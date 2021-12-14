from main.models import (
    CestRationale,
    InterimRequest,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
)
from main.views.supporting_documents import SupportingDocumentDetailView


class JobDescriptionDetailView(SupportingDocumentDetailView):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Job description"


class InterimRequestDetailView(SupportingDocumentDetailView):
    model = InterimRequest
    permission_required = "main.view_interimrequest"
    title = "Interim request"


class CestRationaleDetailView(SupportingDocumentDetailView):
    model = CestRationale
    permission_required = "main.view_cestrationale"
    title = "CEST rationale"


class SdsStatusDeterminationDetailView(SupportingDocumentDetailView):
    model = SdsStatusDetermination
    permission_required = "main.view_sdsstatusdetermination"
    title = "SDS status determination"


class StatementOfWorkDetailView(SupportingDocumentDetailView):
    pk_url_kwarg = "statement_of_work_pk"
    model = StatementOfWork
    template_name = "main/statement_of_work_detail.html"
    permission_required = "main.view_statementofwork"
    title = "Statement of work"

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
