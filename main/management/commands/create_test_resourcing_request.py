import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum

from main.models import (
    CestDocument,
    CestRationale,
    FinancialInformation,
    InterimRequest,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)


class Command(BaseCommand):
    help = "Create a test resourcing request"

    def add_arguments(self, parser):
        parser.add_argument("--name", default="John Smith")
        parser.add_argument("--insideir35", default=True)

    def handle(self, *args, **options):
        assert settings.APP_ENV in (
            "local",
            "dev",
        ), "Command can only be ran in a dev environment"

        name = options["name"]
        inside_ir35 = options["insideir35"] == "True"

        resourcing_request = ResourcingRequest.objects.create(
            # Hiring Manager Helen
            requestor_id=2,
            type=ResourcingRequest.Type.NEW,
            full_name=name,
            job_title="Python Developer",
            project_name="JML",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30 * 6),
            is_ir35=inside_ir35,
            # Chief Rache
            chief_id=3,
        )

        financial_information = FinancialInformation(
            resourcing_request=resourcing_request,
            # ID's are taken from the test-chartofaccount.json fixture.
            group_id="1111AA",
            directorate_id="11111A",
            cost_centre_code_id="111113",
            programme_code_id="1111",
            area_of_work=FinancialInformation.AreaOfWork.INVESTMENT,
            total_budget=500_000,
            timesheet_and_expenses_validator="Mr Anthony Manager",
        )

        if inside_ir35:
            financial_information.min_day_rate = 650
            financial_information.max_day_rate = 750
            financial_information.days_required = 120
        else:
            financial_information.project_fees = 100_000

        financial_information.save()

        JobDescription.objects.create(
            resourcing_request=resourcing_request,
            title="Python Developer",
            role_purpose=lorem_ipsum.paragraph(),
            key_accountabilities=lorem_ipsum.paragraph(),
            line_management_responsibility=lorem_ipsum.paragraph(),
            personal_attributes_and_skills=lorem_ipsum.paragraph(),
            essential_and_preferred_experience=lorem_ipsum.paragraph(),
        )

        statement_of_work = StatementOfWork.objects.create(
            resourcing_request=resourcing_request,
            company_name="Supplier company",
            slot_code="1234abcd",
            is_nominated_worker=True,
            hiring_manager_team_leader="Mr Anthony Manager",
            project_description=lorem_ipsum.paragraph(),
            project_code_id="1111",
            notice_period=lorem_ipsum.paragraph(),
            fees=2365,
            exceptional_expenses=lorem_ipsum.paragraph(),
            deliverable_notes=lorem_ipsum.paragraph(),
        )
        for i in range(0, 3):
            module = StatementOfWorkModule.objects.create(
                statement_of_work=statement_of_work,
                module_title=f"Project part {i}",
                completion_date=datetime.date.today() + datetime.timedelta(days=7 * i),
            )
            for j in range(0, 4):
                StatementOfWorkModuleDeliverable.objects.create(
                    statement_of_work_module=module,
                    deliverable_title=f"Report part {j}",
                    deliverable_description=lorem_ipsum.paragraph(),
                    start_date=datetime.date.today(),
                    end_date=datetime.date.today() + datetime.timedelta(days=30 * 6),
                    monthly_fee=654,
                    payment_date=datetime.date.today(),
                )

        InterimRequest.objects.create(
            resourcing_request=resourcing_request,
            uk_based=True,
            overseas_country=None,
            type_of_security_clearance="sc",
            contractor_type="generalist",
            slot_codes="1234abcd",
            equivalent_civil_servant_grade=InterimRequest.CivilServantGrade.G7,
            supplier=InterimRequest.Supplier.GREEN_PARK,
            part_b_business_case=lorem_ipsum.paragraph(),
            part_b_impact=lorem_ipsum.paragraph(),
            part_b_main_reason=lorem_ipsum.paragraph(),
        )

        CestRationale.objects.create(
            resourcing_request=resourcing_request,
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
            agency="Five Stars",
            # Chief Rache
            completed_by_id=3,
            on_behalf_of="DIT",
            date_completed=datetime.date.today(),
            reasons=lorem_ipsum.paragraph(),
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully created test resourcing request")
        )
