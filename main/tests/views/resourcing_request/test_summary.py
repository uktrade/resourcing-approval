from django.urls import reverse

from main.views.resourcing_request.summary import (
    FinancialInformationSummary,
    InterimRequestSummary,
    ResourcingRequestSummary,
    StatementOfWorkSummary,
)


def test_model_summary_fields_exist_on_model():
    model_summary_classes = [
        ResourcingRequestSummary,
        FinancialInformationSummary,
        StatementOfWorkSummary,
        InterimRequestSummary,
    ]

    for cls in model_summary_classes:
        cls.get_fields()


class TestResourcingRequestSummaryView:
    def test_without_summary_fields(self, client, dg_coo, full_resourcing_request):
        r = client.get(
            reverse(
                "resourcing-request-summary-view",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )
        assert r.context["summary_fields"] == {}

    def test_with_summary_fields(self, client, dg_coo, full_resourcing_request):
        dg_coo.summary_fields = {
            "resourcing_request": ["type"],
            "financial_information": ["min_day_rate"],
            "statement_of_work": ["company_name", "fees"],
            "interim_request": ["uk_based"],
        }
        dg_coo.save()

        r = client.get(
            reverse(
                "resourcing-request-summary-view",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )
        html = r.content.decode("utf-8")

        assert "Type" in html
        assert "Minimum anticipated day rate" in html
        assert "Company name" in html
        assert "Project fee and invoicing" in html
        assert "UK based" in html


class TestResourcingRequestEditSummaryView:
    def test_form_loads(self, client, dg_coo, full_resourcing_request):
        r = client.get(
            reverse(
                "resourcing-request-summary-edit",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            )
        )
        assert r.status_code == 200

    def test_submit_form(self, client, dg_coo, full_resourcing_request):
        r = client.post(
            reverse(
                "resourcing-request-summary-edit",
                kwargs={"resourcing_request_pk": full_resourcing_request.pk},
            ),
            data={
                "resourcing_request_fields": ["type"],
                "financial_information_fields": ["min_day_rate"],
                "statement_of_work_fields": ["company_name", "fees"],
                "interim_request_fields": ["uk_based"],
            },
        )
        assert r.status_code == 302
        dg_coo.refresh_from_db()
        assert dg_coo.summary_fields == {
            "resourcing_request": ["type"],
            "financial_information": ["min_day_rate"],
            "statement_of_work": ["company_name", "fees"],
            "interim_request": ["uk_based"],
        }
