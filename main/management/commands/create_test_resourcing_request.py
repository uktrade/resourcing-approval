import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from django.core.files.base import ContentFile

from main.models import (
    CestDocument,
    CestRationale,
    InterimRequest,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
)


class Command(BaseCommand):
    help = "Create a test resourcing request"

    def add_arguments(self, parser):
        parser.add_argument("--name", default="John Smith")

    def handle(self, *args, **options):
        assert settings.APP_ENV in (
            "local",
            "dev",
        ), "Command can only be ran in a dev environment"

        name = options["name"]

        resourcing_request = ResourcingRequest.objects.create(
            # Hiring Manager Helen
            requestor_id=2,
            name=name,
            is_ir35=True,
            # Chief Rache
            chief_id=3,
        )

        JobDescription.objects.create(
            resourcing_request=resourcing_request,
            title="Python Developer",
            role_purpose=lorem_ipsum.paragraph(),
            key_accountabilities=lorem_ipsum.paragraph(),
            line_management_responsibility=lorem_ipsum.paragraph(),
            personal_attributes_and_skills=lorem_ipsum.paragraph(),
            essential_and_preferred_experience=lorem_ipsum.paragraph(),
        )

        InterimRequest.objects.create(
            resourcing_request=resourcing_request,
            project_name_role_title="Testing",
            new_requirement=True,
            name_of_contractor=name,
            uk_based=True,
            overseas_country=None,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30 * 6),
            type_of_security_clearance="sc",
            contractor_type="generalist",
            part_b_business_case=lorem_ipsum.paragraph(),
            part_b_impact=lorem_ipsum.paragraph(),
            part_b_main_reason=lorem_ipsum.paragraph(),
            # ID's are taken from the test-chartofaccount.json fixture.
            group_id="1111AA",
            directorate_id="11111A",
            cost_centre_code_id="111113",
            slot_codes="1234abcd",
        )

        CestRationale.objects.create(
            resourcing_request=resourcing_request,
            role_start_date=datetime.date.today(),
            role_end_date=datetime.date.today() + datetime.timedelta(days=30 * 6),
            worker_name=name,
            cover_for_perm_role=True,
            role_description=lorem_ipsum.paragraph(),
            what="Python Developer",
            how="From agency",
            where="Remote",
            when="Soon",
            personal_service=lorem_ipsum.paragraph(),
            part_and_parcel=lorem_ipsum.paragraph(),
            financial_risk=lorem_ipsum.paragraph(),
            business_on_own_account=lorem_ipsum.paragraph(),
            supply_chain="Test supply chain",
        )

        cest_document = CestDocument(resourcing_request=resourcing_request)
        cest_document.file.save(
            "lorem-ipsum.txt", ContentFile(lorem_ipsum.paragraph().encode("utf-8"))
        )

        SdsStatusDetermination.objects.create(
            resourcing_request=resourcing_request,
            company_name="A Company",
            worker_name=name,
            agency="Five Stars",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30 * 6),
            # Chief Rache
            completed_by_id=3,
            on_behalf_of="DIT",
            date_completed=datetime.date.today(),
            reasons=lorem_ipsum.paragraph(),
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully created test resourcing request")
        )
