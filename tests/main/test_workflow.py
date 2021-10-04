import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from main.models import ContractorApproval


def client_login():
    user = get_user_model().objects.get(username="john-smith")

    c = Client()
    c.force_login(user)

    return c


def create_approval(client):
    client.post(
        reverse("flow-create"),
        {"workflow_name": "contractor_approval", "flow_name": "Approve John Smith"},
    )

    return ContractorApproval.objects.latest("flow__started")


@pytest.fixture
def client(db):
    return client_login()


@pytest.fixture
def approval(client):
    return create_approval(client)


class TestContractorApprovalWorkflow:
    def test_create(self, db):
        approval_count = ContractorApproval.objects.count()

        client = client_login()
        _ = create_approval(client)

        assert ContractorApproval.objects.count() == approval_count + 1

    def test_query_ir35(self, client, approval):
        assert approval.is_ir35 is None

        client.post(
            reverse("flow-continue", args=[approval.flow.pk]),
            {"uuid": approval.flow.current_task_record.uuid, "is_ir35": True},
        )

        approval.refresh_from_db()

        assert approval.is_ir35 is True
