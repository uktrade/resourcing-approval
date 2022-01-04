import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

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
    def send_for_approval(self, client, resourcing_request):
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
        r = self.send_for_approval(client, full_resourcing_request)
        assert r.status_code == 302
        full_resourcing_request.refresh_from_db()
        assert (
            full_resourcing_request.state == ResourcingRequest.State.AWAITING_APPROVALS
        )

    def test_busops_cannot_send_for_approval(
        self, client, busops, full_resourcing_request
    ):
        r = self.send_for_approval(client, full_resourcing_request)
        assert r.status_code == 403

    def test_cannot_send_for_approval_twice(
        self, client, hiring_manager, full_resourcing_request
    ):
        r = self.send_for_approval(client, full_resourcing_request)
        assert r.status_code == 302

        with pytest.raises(ValidationError):
            r = self.send_for_approval(client, full_resourcing_request)
