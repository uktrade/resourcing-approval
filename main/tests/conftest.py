import datetime

import pytest
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from main.models import ResourcingRequest
from user.models import User


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "test-chartofaccount.json")
        call_command("create_groups")
        call_command("loaddata", "test-users.json")


@pytest.fixture
def admin_user(db):
    return User.objects.get(username="admin")


@pytest.fixture
def resourcing_request(db):
    c = Client()

    hiring_manager = login(c, "hiring-manager")
    c.post(
        reverse("resourcing-request-create"),
        {
            "requestor": hiring_manager.pk,
            "type": ResourcingRequest.Type.NEW.value,
            "full_name": "John Smith",
            "job_title": "Python Developer",
            "project_name": "Testing",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=30 * 6),
            "is_ir35": True,
            "chief": User.objects.get(username="chief").pk,
        },
    )

    return ResourcingRequest.objects.last()


def login(client, username):
    user = User.objects.get(username=username)
    client.force_login(user)

    return user
