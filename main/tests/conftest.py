import datetime

import pytest
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from main import tasks
from main.models import ResourcingRequest
from main.services.resourcing_request import create_full_test_resourcing_request
from user.models import User


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "test-chartofaccount.json")
        # The `create_groups` command must run before we load the `test-users.json`
        # fixture.
        call_command("create_groups")
        call_command("loaddata", "test-users.json")


@pytest.fixture
def admin_user(db):
    return User.objects.get(username="admin")


@pytest.fixture
def hiring_manager(db, client):
    return login(client, "hiring-manager")


@pytest.fixture
def head_of_profession(db, client):
    return login(client, "head-of-profession")


@pytest.fixture
def busops(db, client):
    return login(client, "busops")


@pytest.fixture
def resourcing_request(db):
    c = Client()

    hiring_manager = login(c, "hiring-manager")
    c.post(
        reverse("resourcing-request-create"),
        {
            "requestor": hiring_manager.pk,
            "type": ResourcingRequest.Type.NEW.value,
            "job_title": "Python Developer",
            "project_name": "Testing",
            "profession": 1,  # Development
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=30 * 6),
            "is_ir35": True,
            "chief": User.objects.get(username="chief").pk,
        },
    )

    resourcing_request = ResourcingRequest.objects.last()
    assert resourcing_request

    return resourcing_request


@pytest.fixture
def full_resourcing_request(db):
    return create_full_test_resourcing_request(
        job_title="Python Developer",
        project_name="Unit Test",
        inside_ir35=True,
    )


def login(client, username):
    user = User.objects.get(username=username)
    client.force_login(user)

    return user


@pytest.fixture(autouse=True)
def _empty_test_notification_box():
    tasks.TEST_NOTIFICATION_BOX = []
