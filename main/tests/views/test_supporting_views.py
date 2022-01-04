import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    "supporting_document_prefix",
    [
        "financial-information",
        "job-description",
        "statement-of-work",
        "interim-request",
        "cest-rationale",
        "cest-document",
        "sds-status-determination",
    ],
)
def test_hiring_manager_can_view_create_supporting_document(
    client, hiring_manager, resourcing_request, supporting_document_prefix
):
    r = client.get(
        reverse(
            f"{supporting_document_prefix}-create",
            kwargs={"resourcing_request_pk": resourcing_request.pk},
        )
    )
    assert r.status_code == 200
