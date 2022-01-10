from django.urls import path
from django.urls.conf import include

from main.views.dashboard import DashboardView, index
from main.views.detail_views import (
    CestRationaleDetailView,
    JobDescriptionDetailView,
    SdsStatusDeterminationDetailView,
    StatementOfWorkDetailView,
)
from main.views.interim_request_views import (
    InterimRequestCreateView,
    InterimRequestDetailView,
    InterimRequestUpdateView,
    load_costcentres,
    load_directorates,
)
from main.views.resourcing_request import (
    ResourcingRequestAddComment,
    ResourcingRequestAmendView,
    ResourcingRequestApprovalView,
    ResourcingRequestCreateView,
    ResourcingRequestDeleteView,
    ResourcingRequestDetailView,
    ResourcingRequestFinishAmendmentsReviewView,
    ResourcingRequestListView,
    ResourcingRequestMarkAsCompleteView,
    ResourcingRequestSendForApprovalView,
    ResourcingRequestSendForReviewView,
    ResourcingRequestUpdateView,
)
from main.views.statement_of_work_views import (
    StatementOfWorkCreateView,
    StatementOfWorkModuleCreateView,
    StatementOfWorkModuleDeleteView,
    StatementOfWorkModuleDeliverableCreateView,
    StatementOfWorkModuleDeliverableDeleteView,
    StatementOfWorkModuleDeliverableUpdateView,
    StatementOfWorkModuleUpdateView,
    StatementOfWorkUpdateView,
)
from main.views.supporting_documents import (
    CestDocumentCreateView,
    CestDocumentUpdateView,
    CestRationaleCreateView,
    CestRationaleUpdateView,
    FinancialInformationCreateView,
    FinancialInformationDetailView,
    FinancialInformationUpdateView,
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
)


def supporting_document_urls(name, create_view, update_view, detail_view=None):
    urls = [
        path("create", create_view.as_view(), name=f"{name}-create"),
        path(
            "<int:supporting_document_pk>/update",
            update_view.as_view(),
            name=f"{name}-update",
        ),
    ]

    if detail_view:
        urls.append(
            path(
                "<int:supporting_document_pk>/",
                detail_view.as_view(),
                name=f"{name}-detail",
            )
        )

    return urls


financial_information_urls = supporting_document_urls(
    "financial-information",
    FinancialInformationCreateView,
    FinancialInformationUpdateView,
    FinancialInformationDetailView,
)

job_description_urls = supporting_document_urls(
    "job-description",
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    JobDescriptionDetailView,
)

statement_of_work_module_deliverable_urls = [
    path(
        "create",
        StatementOfWorkModuleDeliverableCreateView.as_view(),
        name="statement-of-work-module-deliverable-create",
    ),
    path(
        "<int:deliverable_pk>/update",
        StatementOfWorkModuleDeliverableUpdateView.as_view(),
        name="statement-of-work-module-deliverable-update",
    ),
    path(
        "<int:deliverable_pk>/delete",
        StatementOfWorkModuleDeliverableDeleteView.as_view(),
        name="statement-of-work-module-deliverable-delete",
    ),
]

statement_of_work_module_urls = [
    path(
        "create",
        StatementOfWorkModuleCreateView.as_view(),
        name="statement-of-work-module-create",
    ),
    path(
        "<int:module_pk>/update",
        StatementOfWorkModuleUpdateView.as_view(),
        name="statement-of-work-module-update",
    ),
    path(
        "<int:module_pk>/delete",
        StatementOfWorkModuleDeleteView.as_view(),
        name="statement-of-work-module-delete",
    ),
    path(
        "<int:module_pk>/deliverable/",
        include(statement_of_work_module_deliverable_urls),
    ),
]

statement_of_work_urls = [
    path(
        "create", StatementOfWorkCreateView.as_view(), name="statement-of-work-create"
    ),
    path(
        "<int:statement_of_work_pk>/",
        include(
            [
                path(
                    "update",
                    StatementOfWorkUpdateView.as_view(),
                    name="statement-of-work-update",
                ),
                path(
                    "",
                    StatementOfWorkDetailView.as_view(),
                    name="statement-of-work-detail",
                ),
                path("module/", include(statement_of_work_module_urls)),
            ]
        ),
    ),
]

interim_request_urls = supporting_document_urls(
    "interim-request",
    InterimRequestCreateView,
    InterimRequestUpdateView,
    InterimRequestDetailView,
)

cest_rationale_urls = supporting_document_urls(
    "cest-rationale",
    CestRationaleCreateView,
    CestRationaleUpdateView,
    CestRationaleDetailView,
)

cest_document_urls = supporting_document_urls(
    "cest-document",
    CestDocumentCreateView,
    CestDocumentUpdateView,
)

sds_status_determination_urls = supporting_document_urls(
    "sds-status-determination",
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
    SdsStatusDeterminationDetailView,
)

request_urls = [
    path(
        "",
        ResourcingRequestDetailView.as_view(),
        name="resourcing-request-detail",
    ),
    path(
        "update",
        ResourcingRequestUpdateView.as_view(),
        name="resourcing-request-update",
    ),
    path(
        "delete",
        ResourcingRequestDeleteView.as_view(),
        name="resourcing-request-delete",
    ),
    # Supporting documents
    path("financial-information/", include(financial_information_urls)),
    path("job-description/", include(job_description_urls)),
    path("statement-of-work/", include(statement_of_work_urls)),
    path("interim-request/", include(interim_request_urls)),
    path("cest-rationale/", include(cest_rationale_urls)),
    path("cest-document/", include(cest_document_urls)),
    path("sds-status-determination/", include(sds_status_determination_urls)),
    # Actions
    path(
        "send-for-approval",
        ResourcingRequestSendForApprovalView.as_view(),
        name="resourcing-request-send-for-approval",
    ),
    path(
        "amend",
        ResourcingRequestAmendView.as_view(),
        name="resourcing-request-amend",
    ),
    path(
        "send-for-review",
        ResourcingRequestSendForReviewView.as_view(),
        name="resourcing-request-send-for-review",
    ),
    path(
        "finish-amendments-review",
        ResourcingRequestFinishAmendmentsReviewView.as_view(),
        name="resourcing-request-finish-amendments-review",
    ),
    path(
        "add-comment",
        ResourcingRequestAddComment.as_view(),
        name="resourcing-request-add-comment",
    ),
    path(
        "approval",
        ResourcingRequestApprovalView.as_view(),
        name="resourcing-request-approval",
    ),
    path(
        "mark-as-complete",
        ResourcingRequestMarkAsCompleteView.as_view(),
        name="resourcing-request-mark-as-complete",
    ),
]

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Resourcing request
    path(
        "resourcing-request/",
        include(
            [
                path(
                    "",
                    ResourcingRequestListView.as_view(),
                    name="resourcing-request-list",
                ),
                path(
                    "create/",
                    ResourcingRequestCreateView.as_view(),
                    name="resourcing-request-create",
                ),
                path(
                    "<int:resourcing_request_pk>/",
                    include(request_urls),
                ),
            ]
        ),
    ),
    # htmx
    path("htmx/load-directorates/", load_directorates, name="htmx-load-directorates"),
    path("htmx/load-costcentres/", load_costcentres, name="htmx-load-costcentres"),
]
