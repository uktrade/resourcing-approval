import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from main.models import Approval
from main.services.review import ReviewAction, ReviewService


class TestReviewService:
    # Helpers
    def _send_for_approval(self, client, resourcing_request):
        client.post(
            reverse(
                "resourcing-request-send-for-approval",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            )
        )

    def _amend(self, client, resourcing_request):
        client.post(
            reverse(
                "resourcing-request-amend",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            )
        )

    def _send_for_review(self, client, resourcing_request):
        client.post(
            reverse(
                "resourcing-request-send-for-review",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            )
        )

    # Tests
    def test_cannot_be_approved(self, head_of_profession, full_resourcing_request):
        with pytest.raises(
            ValueError, match="The contractor request cannot be approved"
        ):
            ReviewService.add_review(
                user=head_of_profession,
                resourcing_request=full_resourcing_request,
                resourcing_request_url="http://www.example.com",
                action=ReviewAction.APPROVE,
                approval_type=Approval.Type.HEAD_OF_PROFESSION,
                text="LGTM!",
            )

    def test_approve_no_perm(self, client, hiring_manager, full_resourcing_request):
        self._send_for_approval(client, full_resourcing_request)

        full_resourcing_request.refresh_from_db()

        with pytest.raises(
            PermissionDenied,
            match="The user doesn't have permission to give this approval",
        ):
            ReviewService.add_review(
                user=hiring_manager,
                resourcing_request=full_resourcing_request,
                resourcing_request_url="http://www.example.com",
                action=ReviewAction.APPROVE,
                approval_type=Approval.Type.HEAD_OF_PROFESSION,
                text="LGTM!",
            )

    def test_cannot_be_cleared(self, head_of_profession, full_resourcing_request):
        with pytest.raises(ValueError, match="The approval cannot be cleared"):
            ReviewService.add_review(
                user=head_of_profession,
                resourcing_request=full_resourcing_request,
                resourcing_request_url="http://www.example.com",
                action=ReviewAction.CLEAR_APPROVAL,
                approval_type=Approval.Type.HEAD_OF_PROFESSION,
                text="LGTM!",
            )

    def test_clear_no_perm(self, client, hiring_manager, full_resourcing_request):
        self._send_for_approval(client, full_resourcing_request)
        self._amend(client, full_resourcing_request)
        self._send_for_review(client, full_resourcing_request)

        full_resourcing_request.refresh_from_db()

        with pytest.raises(
            PermissionDenied,
            match="The user doesn't have permission to clear approvals",
        ):
            ReviewService.add_review(
                user=hiring_manager,
                resourcing_request=full_resourcing_request,
                resourcing_request_url="http://www.example.com",
                action=ReviewAction.CLEAR_APPROVAL,
                approval_type=Approval.Type.HEAD_OF_PROFESSION,
                text="LGTM!",
            )
