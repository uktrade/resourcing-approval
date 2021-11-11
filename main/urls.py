from django.urls import path
from django.urls.conf import include

from main.views.dashboard import DashboardView, index
from main.views.detail_views import (
    CestRationaleDetailView,
    InterimRequestDetailView,
    JobDescriptionDetailView,
    SdsStatusDeterminationDetailView,
)
from main.views.interim_request_views import (
    InterimRequestCreateView,
    InterimRequestUpdateView,
    load_costcentres,
    load_directorates,
)
from main.views.resourcing_request import (
    ResourcingRequestAddApproval,
    ResourcingRequestAddComment,
    ResourcingRequestAmendView,
    ResourcingRequestClearApprovalView,
    ResourcingRequestCreateView,
    ResourcingRequestDeleteView,
    ResourcingRequestDetailView,
    ResourcingRequestFinishAmendmentsReviewView,
    ResourcingRequestSendForApprovalView,
    ResourcingRequestSendForReviewView,
    ResourcingRequestUpdateView,
)
from main.views.statement_of_work_views import (
    StatementOfWorkCreateView,
    StatementOfWorkModuleCreateView,
    StatementOfWorkModuleDeliverableCreateView,
    StatementOfWorkModuleDeliverableUpdateView,
    StatementOfWorkModuleUpdateView,
    StatementOfWorkUpdateView,
)
from main.views.supporting_forms import (
    CestDocumentCreateView,
    CestDocumentUpdateView,
    CestRationaleCreateView,
    CestRationaleUpdateView,
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
)


request_urls = [
    path(
        "create/",
        ResourcingRequestCreateView.as_view(),
        name="resourcing-request-create",
    ),
    path(
        "<int:pk>/",
        ResourcingRequestDetailView.as_view(),
        name="resourcing-request-detail",
    ),
    path(
        "<int:pk>/update",
        ResourcingRequestUpdateView.as_view(),
        name="resourcing-request-update",
    ),
    path(
        "<int:pk>/delete",
        ResourcingRequestDeleteView.as_view(),
        name="resourcing-request-delete",
    ),
    path(
        "<int:pk>/send-for-approval",
        ResourcingRequestSendForApprovalView.as_view(),
        name="resourcing-request-send-for-approval",
    ),
    path(
        "<int:pk>/amend",
        ResourcingRequestAmendView.as_view(),
        name="resourcing-request-amend",
    ),
    path(
        "<int:pk>/send-for-review",
        ResourcingRequestSendForReviewView.as_view(),
        name="resourcing-request-send-for-review",
    ),
    path(
        "<int:pk>/clear-approval",
        ResourcingRequestClearApprovalView.as_view(),
        name="resourcing-request-clear-approval",
    ),
    path(
        "<int:pk>/finish-amendments-review",
        ResourcingRequestFinishAmendmentsReviewView.as_view(),
        name="resourcing-request-finish-amendments-review",
    ),
    path(
        "<int:pk>/add-approval",
        ResourcingRequestAddApproval.as_view(),
        name="resourcing-request-add-approval",
    ),
    path(
        "<int:pk>/add-comment",
        ResourcingRequestAddComment.as_view(),
        name="resourcing-request-add-comment",
    ),
]


def document_urls(create_view, update_view, name_prefix, parent_key=""):
    return [
        path(
            f"create{parent_key}",
            create_view.as_view(),
            name=f"{name_prefix}-create",
        ),
        path(
            "<int:pk>/update",
            update_view.as_view(),
            name=f"{name_prefix}-update",
        ),
    ]


def details_document_urls(
    detail_view, create_view, update_view, name_prefix, parent_key=""
):
    return [
        path(
            f"create{parent_key}",
            create_view.as_view(),
            name=f"{name_prefix}-create",
        ),
        path(
            "<int:pk>/update",
            update_view.as_view(),
            name=f"{name_prefix}-update",
        ),
        path(
            "<int:pk>/detail",
            detail_view.as_view(),
            name=f"{name_prefix}-detail",
        ),
    ]


job_description_urls = details_document_urls(
    JobDescriptionDetailView,
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    "job-description",
)

statement_of_work_urls = document_urls(
    StatementOfWorkCreateView,
    StatementOfWorkUpdateView,
    "statement-of-work",
)


statement_of_work__module_urls = document_urls(
    StatementOfWorkModuleCreateView,
    StatementOfWorkModuleUpdateView,
    "statement-of-work-module",
    "/<int:parent_pk>",
)

statement_of_work__module_deliverable_urls = document_urls(
    StatementOfWorkModuleDeliverableCreateView,
    StatementOfWorkModuleDeliverableUpdateView,
    "statement-of-work-module-deliverable",
    "/<int:parent_pk>",
)


interim_request_urls = details_document_urls(
    InterimRequestDetailView,
    InterimRequestCreateView,
    InterimRequestUpdateView,
    "interim-request",
)

cest_rationale_urls = details_document_urls(
    CestRationaleDetailView,
    CestRationaleCreateView,
    CestRationaleUpdateView,
    "cest-rationale",
)

cest_document_urls = document_urls(
    CestDocumentCreateView,
    CestDocumentUpdateView,
    "cest-document",
)

sds_status_determination_urls = details_document_urls(
    SdsStatusDeterminationDetailView,
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
    "sds-status-determination",
)

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("resourcing-request/", include(request_urls)),
    path("job-description/", include(job_description_urls)),
    path("statement-of-work/", include(statement_of_work_urls)),
    path(
        "statement-of-work-module-deliverable/",
        include(statement_of_work__module_deliverable_urls),
    ),
    path("statement-of-work-module/", include(statement_of_work__module_urls)),
    path("interim-request/", include(interim_request_urls)),
    path("cest-rationale/", include(cest_rationale_urls)),
    path("cest-document/", include(cest_document_urls)),
    path("sds-status-determination/", include(sds_status_determination_urls)),
    path("htmx/load-directorates/", load_directorates, name="htmx-load-directorates"),
    path("htmx/load-costcentres/", load_costcentres, name="htmx-load-costcentres"),
]
