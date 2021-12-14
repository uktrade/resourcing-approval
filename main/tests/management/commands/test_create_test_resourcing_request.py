from django.core.management import call_command

from main.models import ResourcingRequest


def test_command(db):
    count = ResourcingRequest.objects.count()

    call_command("create_test_resourcing_request")

    assert ResourcingRequest.objects.count() == count + 1
