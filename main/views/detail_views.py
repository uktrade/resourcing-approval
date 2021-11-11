from main.models import (
    CestRationale,
    InterimRequest,
    JobDescription,
    SdsStatusDetermination,
    StatementOfWork,
)
from main.views.supporting_forms import SupportingFormDetailView


class JobDescriptionDetailView(SupportingFormDetailView):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Job description"


class InterimRequestDetailView(SupportingFormDetailView):
    model = InterimRequest
    permission_required = "main.view_interimrequest"
    title = "Interim Request"


class CestRationaleDetailView(SupportingFormDetailView):
    model = CestRationale
    permission_required = "main.view_cestrationale"
    title = "CEST Rationale"


class SdsStatusDeterminationDetailView(SupportingFormDetailView):
    model = SdsStatusDetermination
    permission_required = "main.view_sdsstatusdetermination"
    title = "SDS Status Determination"


class StatementOfWorkDetailView(SupportingFormDetailView):
    model = StatementOfWork
    permission_required = "main.view_statementofwork"
    title = "Statement of Work"
    template_name = "main/statement_of_work_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_modules"] = self.object.modules.all()
        exclude_list = ["id", "statement_of_work_module", "deliverable_title"]
        context["deliverable_exclude_list"] = exclude_list
        return context
