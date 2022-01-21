import datetime
from typing import Any

from django.core.files.base import ContentFile
from django.utils import lorem_ipsum

from main.models import (
    CestDocument,
    FinancialInformation,
    InterimRequest,
    JobDescription,
    ResourcingRequest,
    SdsStatusDetermination,
    StatementOfWork,
    StatementOfWorkModule,
    StatementOfWorkModuleDeliverable,
)


def create_full_test_resourcing_request(
    job_title: str, project_name: str, inside_ir35: bool
) -> ResourcingRequest:
    resourcing_request = ResourcingRequest.objects.create(
        # Hiring Manager Helen
        requestor_id=2,
        type=ResourcingRequest.Type.NEW,
        job_title=job_title,
        project_name=project_name,
        portfolio="Testing",
        profession_id=1,  # Development
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
        team="Live Services",
        programme_code_id="1111",
        area_of_work=FinancialInformation.AreaOfWork.DDAT,
        total_budget=500_000,
        timesheet_and_expenses_validator="Mr Anthony Manager",
        second_timesheet_validator="Mrs Anna Manager",
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
        description={
            "delta": {
                "ops": [
                    {"insert": "Heading 1"},
                    {"insert": "\n", "attributes": {"header": 1}},
                    {"insert": lorem_ipsum.paragraph() + "\n"},
                ]
            }
        },
    )

    statement_of_work = StatementOfWork.objects.create(
        resourcing_request=resourcing_request,
        company_name="Supplier company",
        position_code="1234abcd",
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
        position_code="1234abcd",
        equivalent_civil_servant_grade=InterimRequest.CivilServantGrade.G7,
        supplier=InterimRequest.Supplier.GREEN_PARK,
        part_b_business_case=lorem_ipsum.paragraph(),
        part_b_impact=lorem_ipsum.paragraph(),
        part_b_main_reason=lorem_ipsum.paragraph(),
    )

    cest_document = CestDocument(resourcing_request=resourcing_request)
    cest_document.file.save(
        "lorem-ipsum.txt", ContentFile(lorem_ipsum.paragraph().encode("utf-8"))
    )

    SdsStatusDetermination.objects.create(
        resourcing_request=resourcing_request,
        **create_sds_status_determination_test_data(),
    )

    return resourcing_request


def create_sds_status_determination_test_data() -> dict[str, Any]:
    return {
        "company_name": "A Company",
        "worker_name": "John Smith",
        "agency": "Five Stars",
        "contract_start_date": datetime.date.today(),
        "contract_end_date": datetime.date.today() + datetime.timedelta(days=30 * 6),
        "on_behalf_of": "DIT",
        "date_completed": datetime.date.today(),
        "reasons": lorem_ipsum.paragraph(),
    }
