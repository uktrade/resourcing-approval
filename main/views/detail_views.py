from main.views.supporting_forms import SupportingFormDetailView
from main.models import JobDescription, InterimRequest


class JobDescriptionDetailView(SupportingFormDetailView):
    model = JobDescription
    permission_required = "main.view_jobdescription"
    title = "Job description"


class InterimRequestDetailView(SupportingFormDetailView):
    model = InterimRequest
    permission_required = "main.view_jobdescription"
    title = "Interim Request"
