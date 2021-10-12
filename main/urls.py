from django.urls import path
from django.urls.conf import include

from main.views import (
    ApprovalAddComment,
    ApprovalApproveRejectView,
    ApprovalChangeStatusView,
    ApprovalCreateView,
    ApprovalDeleteView,
    ApprovalDetailView,
    ApprovalListView,
    ApprovalUpdateView,
    CestRationaleCreateView,
    CestRationaleUpdateView,
    InterimRequestCreateView,
    InterimRequestUpdateView,
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
    StatementOfWorkCreateView,
    StatementOfWorkUpdateView,
)

approval_urls = [
    path("create/", ApprovalCreateView.as_view(), name="approval-create"),
    path("<int:pk>/", ApprovalDetailView.as_view(), name="approval-detail"),
    path("<int:pk>/update", ApprovalUpdateView.as_view(), name="approval-update"),
    path("<int:pk>/delete", ApprovalDeleteView.as_view(), name="approval-delete"),
    path(
        "<int:pk>/approve",
        ApprovalApproveRejectView.as_view(),
        {"approved": True},
        name="approval-approve",
    ),
    path(
        "<int:pk>/reject",
        ApprovalApproveRejectView.as_view(),
        {"approved": False},
        name="approval-reject",
    ),
    path(
        "<int:pk>/change-status",
        ApprovalChangeStatusView.as_view(),
        name="approval-change-status",
    ),
    path(
        "<int:pk>/add-comment",
        ApprovalAddComment.as_view(),
        name="approval-add-comment",
    ),
]


def document_urls(create_view, update_view, name_prefix):
    return [
        path(
            "create",
            create_view.as_view(),
            name=f"{name_prefix}-create",
        ),
        path(
            "<int:pk>/update",
            update_view.as_view(),
            name=f"{name_prefix}-update",
        ),
    ]


job_description_urls = document_urls(
    JobDescriptionCreateView,
    JobDescriptionUpdateView,
    "job-description",
)

statement_of_work_urls = document_urls(
    StatementOfWorkCreateView,
    StatementOfWorkUpdateView,
    "statement-of-work",
)

interim_request_urls = document_urls(
    InterimRequestCreateView,
    InterimRequestUpdateView,
    "interim-request",
)

cest_rationale_urls = document_urls(
    CestRationaleCreateView,
    CestRationaleUpdateView,
    "cest-rationale",
)

sds_status_determination_urls = document_urls(
    SdsStatusDeterminationCreateView,
    SdsStatusDeterminationUpdateView,
    "sds-status-determination",
)

urlpatterns = [
    path("", ApprovalListView.as_view(), name="approval-list"),
    path("approval/", include(approval_urls)),
    path("job-description/", include(job_description_urls)),
    path("statement-of-work/", include(statement_of_work_urls)),
    path("interim-request/", include(interim_request_urls)),
    path("cest-rationale/", include(cest_rationale_urls)),
    path("sds-status-determination/", include(sds_status_determination_urls)),
]
