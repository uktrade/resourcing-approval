import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from main import tasks
from main.models import ResourcingRequest


class TestResourcingRequestCreateView:
    def test_hiring_manager_can_view(self, client, hiring_manager):
        r = client.get(reverse("resourcing-request-create"))
        assert r.status_code == 200


class TestResourcingRequestListView:
    def test_busops_can_view(self, client, busops):
        r = client.get(reverse("resourcing-request-list"))
        assert r.status_code == 200

    def test_hiring_manager_cannot_view(self, client, hiring_manager):
        r = client.get(reverse("resourcing-request-list"))
        assert r.status_code == 403


class TestResourcingRequestDetailView:
    def test_hiring_manager_can_view(self, client, hiring_manager, resourcing_request):
        r = client.get(
            reverse(
                "resourcing-request-detail",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            )
        )
        assert r.status_code == 200


class TestResourcingRequestSendForApprovalView:
    # Helpers
    def _send_for_approval(self, client, resourcing_request):
        return client.post(
            reverse(
                "resourcing-request-send-for-approval",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            )
        )

    # Tests
    def test_hiring_manager_can_send_for_approval(
        self, client, hiring_manager, full_resourcing_request
    ):
        r = self._send_for_approval(client, full_resourcing_request)
        assert r.status_code == 302
        full_resourcing_request.refresh_from_db()
        assert (
            full_resourcing_request.state == ResourcingRequest.State.AWAITING_APPROVALS
        )

    def test_busops_cannot_send_for_approval(
        self, client, busops, full_resourcing_request
    ):
        r = self._send_for_approval(client, full_resourcing_request)
        assert r.status_code == 403

    def test_cannot_send_for_approval_twice(
        self, client, hiring_manager, full_resourcing_request
    ):
        r = self._send_for_approval(client, full_resourcing_request)
        assert r.status_code == 302

        with pytest.raises(ValidationError):
            r = self._send_for_approval(client, full_resourcing_request)


class TestResourcingRequestAddCommentView:
    # Helpers
    def _add_comment(self, client, resourcing_request, text: str):
        return client.post(
            reverse(
                "resourcing-request-add-comment",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            ),
            data={"text": text},
        )

    # Tests
    def test_can_add_comment(self, client, hiring_manager, full_resourcing_request):
        text = "This is a test comment."
        r = self._add_comment(client, full_resourcing_request, text=text)
        assert r.status_code == 302
        assert full_resourcing_request.comments.last().text == text

    def test_notification_is_sent(
        self, client, hiring_manager, full_resourcing_request
    ):
        text = "This is a test comment."
        self._add_comment(client, full_resourcing_request, text=text)
        assert len(tasks.TEST_NOTIFICATION_BOX) == 1
        assert tasks.TEST_NOTIFICATION_BOX[0]["personalisation"]["commenter"]
