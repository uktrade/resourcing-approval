import pytest
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse

from main import tasks
from main.models import Approval, ResourcingRequest
from main.services.review import ReviewAction
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


# The add comment view was replaced with the review view. I'm going to leave this as is
# for the time being as it groups the comment tests together.
class TestResourcingRequestAddCommentView:
    # Helpers
    def _add_comment(self, client, resourcing_request, text: str):
        return client.post(
            reverse(
                "resourcing-request-review",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            ),
            data={"action": ReviewAction.COMMENT.value, "text": text},
        )

    # Tests
    def test_can_add_comment(self, client, hiring_manager, full_resourcing_request):
        text = "This is a test comment."
        r = self._add_comment(client, full_resourcing_request, text=text)
        assert r.status_code == 200
        assert full_resourcing_request.comments.last().text == text

    def test_notification_is_sent(
        self, client, hiring_manager, full_resourcing_request
    ):
        text = "This is a test comment."
        self._add_comment(client, full_resourcing_request, text=text)
        assert len(tasks.TEST_NOTIFICATION_BOX) == 1
        assert tasks.TEST_NOTIFICATION_BOX[0]["personalisation"]["commenter"]


class TestResourcingRequestReviewView:
    @pytest.fixture(autouse=True)
    def _setup(self, client, hiring_manager, full_resourcing_request):
        self.client = client

        self.client.post(
            reverse(
                "resourcing-request-send-for-approval",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )

    def _review(
        self,
        resourcing_request,
        action: ReviewAction,
        approval_type: Approval.Type,
        text: str = None,
        follow: bool = False,
    ):
        return self.client.post(
            reverse(
                "resourcing-request-review",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            ),
            data={
                "action": action.value,
                "approval_type": approval_type.value,
                "text": text,
            },
            follow=follow,
        )

    def _approve(
        self,
        resourcing_request,
        approval_type: str,
        text: str = None,
        follow: bool = False,
    ):
        return self._review(
            resourcing_request=resourcing_request,
            action=ReviewAction.APPROVE,
            approval_type=Approval.Type(approval_type),
            text=text,
            follow=follow,
        )

    def test_can_add_approval(self, head_of_profession, full_resourcing_request):
        r = self._approve(
            full_resourcing_request,
            approval_type="head_of_profession",
            text="LGTM!",
        )
        assert r.status_code == 200
        full_resourcing_request.refresh_from_db()
        assert full_resourcing_request.head_of_profession_approval

    def test_requestor_is_notified_of_approval(
        self, head_of_profession, full_resourcing_request, settings
    ):
        self._approve(
            full_resourcing_request,
            approval_type="head_of_profession",
            text="LGTM!",
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

    def test_confirmation_message(self, head_of_profession, full_resourcing_request):
        r = self._approve(
            full_resourcing_request,
            approval_type="head_of_profession",
            text="LGTM!",
            follow=True,
        )
        assert r.status_code == 200
        assert messages.get_messages(r.wsgi_request)


def test_scenario_mark_as_complete(client, full_resourcing_request):
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
                "resourcing-request-review",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            ),
            data={
                "action": ReviewAction.APPROVE.value,
                "approval_type": approval_type.value,
            },
        )

    full_resourcing_request.refresh_from_db()
    assert full_resourcing_request.state == ResourcingRequest.State.APPROVED

    login(client, "hiring-manager")

    # mark as complete
    client.post(
        reverse(
            "resourcing-request-mark-as-complete",
            kwargs={"resourcing_request_pk": full_resourcing_request.pk},
        )
    )

    full_resourcing_request.refresh_from_db()
    assert full_resourcing_request.state == ResourcingRequest.State.COMPLETED
