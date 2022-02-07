import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from main import tasks
from main.models import ResourcingRequest
from main.services.resourcing_request import create_sds_status_determination_test_data
from main.tests.conftest import login
from main.tests.constants import USERNAME_APPROVAL_ORDER


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


class TestResourcingRequestApprovalView:
    @pytest.fixture(autouse=True)
    def _setup(self, client, hiring_manager, full_resourcing_request):
        client.post(
            reverse(
                "resourcing-request-send-for-approval",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )

    def _approval(
        self,
        client,
        resourcing_request,
        type: str,
        approved: bool,
        reason: str = None,
        follow: bool = False,
    ):
        return client.post(
            reverse(
                "resourcing-request-approval",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            ),
            data={
                "type": type,
                "approved": approved,
                "reason": reason,
            },
            follow=follow,
        )

    def test_can_add_approval(
        self, client, head_of_profession, full_resourcing_request
    ):
        r = self._approval(
            client,
            full_resourcing_request,
            type="head_of_profession",
            approved=True,
            reason="LGTM!",
        )
        assert r.status_code == 302
        full_resourcing_request.refresh_from_db()
        assert full_resourcing_request.head_of_profession_approval

    def test_requestor_is_notified_of_approval(
        self, client, head_of_profession, full_resourcing_request, settings
    ):
        self._approval(
            client,
            full_resourcing_request,
            type="head_of_profession",
            approved=True,
            reason="LGTM!",
        )

        approval_notifications = [
            x
            for x in tasks.TEST_NOTIFICATION_BOX
            if x["template_id"] == settings.GOVUK_NOTIFY_APPROVAL_TEMPLATE_ID
        ]

        # 1 comment left notification was sent to the requestor
        assert len(approval_notifications) == 1
        assert (
            approval_notifications[0]["personalisation"]["approved_or_rejected"]
            == "approved"
        )

    def test_confirmation_message(
        self, client, head_of_profession, full_resourcing_request
    ):
        r = self._approval(
            client,
            full_resourcing_request,
            type="head_of_profession",
            approved=True,
            reason="LGTM!",
            follow=True,
        )
        assert r.status_code == 200
        assert r.context["messages"]


def test_scenario_mark_as_complete(client, full_resourcing_request):
    # remove the status determination statement form
    full_resourcing_request.sds_status_determination.delete()

    # send for approval
    login(client, "hiring-manager")
    client.post(
        reverse(
            "resourcing-request-send-for-approval",
            kwargs={"resourcing_request_pk": full_resourcing_request.pk},
        )
    )

    # give all approvals
    for username, approval_type in USERNAME_APPROVAL_ORDER:
        login(client, username)
        client.post(
            reverse(
                "resourcing-request-approval",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            ),
            data={
                "type": approval_type.value,
                "approved": True,
            },
        )

    full_resourcing_request.refresh_from_db()
    assert full_resourcing_request.state == ResourcingRequest.State.APPROVED

    login(client, "hiring-manager")

    # check we can't mark as complete without the status determination statement
    with pytest.raises(ValidationError):
        client.post(
            reverse(
                "resourcing-request-mark-as-complete",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )

    # add back the status determination statement form
    client.post(
        reverse(
            "sds-status-determination-create",
            kwargs={"resourcing_request_pk": full_resourcing_request.pk},
        ),
        data=create_sds_status_determination_test_data(),
    )
    # mark as complete
    client.post(
        reverse(
            "resourcing-request-mark-as-complete",
            kwargs={"resourcing_request_pk": full_resourcing_request.pk},
        )
    )

    full_resourcing_request.refresh_from_db()
    assert full_resourcing_request.state == ResourcingRequest.State.COMPLETED
