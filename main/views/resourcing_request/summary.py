from django import forms
from django.db import models
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import capfirst
from django.views.generic import TemplateView

from main.models import (
    FinancialInformation,
    InterimRequest,
    ResourcingRequest,
    StatementOfWork,
)
from main.views.base import ResourcingRequestBaseView


class ModelSummary:
    model: models.Model
    heading: str
    fields: list[str] = []
    stacked_fields: list[str] = []

    def __init__(self, instance, summary_fields):
        self.instance = instance
        self.summary_fields = summary_fields

    @classmethod
    def get_fields(cls):
        return [cls.model._meta.get_field(field) for field in cls.fields]

    @classmethod
    def get_choices(cls):
        return [
            (field.name, capfirst(field.verbose_name)) for field in cls.get_fields()
        ]

    def get_value(self, field_name):
        if hasattr(self.instance, f"get_{field_name}_display"):
            return getattr(self.instance, f"get_{field_name}_display")

        return getattr(self.instance, field_name)

    def get_field_template(self, field_name):
        if field_name in self.stacked_fields:
            return "main/partials/summary/stacked.html"

        return "main/partials/summary/inline.html"

    def render_fields(self):
        for field_name in self.summary_fields:
            template = self.get_field_template(field_name)
            field = self.model._meta.get_field(field_name)

            yield render_to_string(
                template,
                {
                    "name": field.verbose_name,
                    "help_text": field.help_text,
                    "value": self.get_value(field_name),
                },
            )


class ResourcingRequestSummary(ModelSummary):
    model = ResourcingRequest
    heading = "Resourcing request"
    fields = [
        "requestor",
        "state",
        "type",
        "job_title",
        "project_name",
        "portfolio",
        "profession",
        "start_date",
        "end_date",
        "is_ir35",
        "chief",
    ]


class FinancialInformationSummary(ModelSummary):
    model = FinancialInformation
    heading = "Financial information"
    fields = [
        "group",
        "directorate",
        "cost_centre_code",
        "team",
        "programme_code",
        "area_of_work",
        "total_budget",
        "timesheet_and_expenses_validator",
        "second_timesheet_validator",
        "min_day_rate",
        "max_day_rate",
        "days_required",
        "project_fees",
    ]


# TODO: Add support for job description summary.


class StatementOfWorkSummary(ModelSummary):
    model = StatementOfWork
    heading = "Statement of work"
    fields = [
        "company_name",
        "position_code",
        "is_nominated_worker",
        "hiring_manager_team_leader",
        "project_description",
        "project_code",
        "notice_period",
        "fees",
        "exceptional_expenses",
        "deliverable_notes",
    ]
    stacked_fields = [
        "project_description",
        "notice_period",
        "fees",
        "exceptional_expenses",
        "deliverable_notes",
    ]


class InterimRequestSummary(ModelSummary):
    model = InterimRequest
    heading = "Interim request"
    fields = [
        "uk_based",
        "overseas_country",
        "type_of_security_clearance",
        "contractor_type",
        "position_code",
        "equivalent_civil_servant_grade",
        "supplier",
        "part_b_business_case",
        "part_b_impact",
        "part_b_main_reason",
    ]
    stacked_fields = [
        "part_b_business_case",
        "part_b_impact",
        "part_b_main_reason",
    ]


class ResourcingRequestSummaryView(TemplateView, ResourcingRequestBaseView):
    template_name = "main/resourcingrequest_summary_view.html"

    def get_context_data(self, **kwargs):
        summary_fields = self.request.user.summary_fields

        sections = [
            ResourcingRequestSummary(
                instance=self.resourcing_request,
                summary_fields=summary_fields.get("resourcing_request", []),
            )
        ]

        if hasattr(self.resourcing_request, "financial_information"):
            sections.append(
                FinancialInformationSummary(
                    instance=self.resourcing_request.financial_information,
                    summary_fields=summary_fields.get("financial_information", []),
                )
            )

        if hasattr(self.resourcing_request, "statement_of_work"):
            sections.append(
                StatementOfWorkSummary(
                    instance=self.resourcing_request.statement_of_work,
                    summary_fields=summary_fields.get("statement_of_work", []),
                )
            )

        if hasattr(self.resourcing_request, "interim_request"):
            sections.append(
                InterimRequestSummary(
                    instance=self.resourcing_request.interim_request,
                    summary_fields=summary_fields.get("interim_request", []),
                )
            )

        context = {
            "resourcing_request": self.resourcing_request,
            "sections": sections,
            "summary_fields": summary_fields,
        }

        return super().get_context_data(**kwargs) | context


class EditSummaryForm(forms.Form):
    resourcing_request_fields = forms.MultipleChoiceField(
        choices=ResourcingRequestSummary.get_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    financial_information_fields = forms.MultipleChoiceField(
        choices=FinancialInformationSummary.get_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    statement_of_work_fields = forms.MultipleChoiceField(
        choices=StatementOfWorkSummary.get_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    interim_request_fields = forms.MultipleChoiceField(
        choices=InterimRequestSummary.get_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class ResourcingRequestEditSummaryView(TemplateView, ResourcingRequestBaseView):
    template_name = "main/resourcingrequest_summary_edit.html"

    def get_context_data(self, **kwargs):
        fields = self.request.user.summary_fields

        form_data = {
            "resourcing_request_fields": fields.get("resourcing_request", []),
            "financial_information_fields": fields.get("financial_information", []),
            "statement_of_work_fields": fields.get("statement_of_work", []),
            "interim_request_fields": fields.get("interim_request", []),
        }

        context = {
            "resourcing_request": self.resourcing_request,
            "form": EditSummaryForm(data=form_data),
        }

        return super().get_context_data(**kwargs) | context

    def post(self, request, *args, **kwargs):
        data = request.POST

        self.request.user.summary_fields = {
            "resourcing_request": data.getlist("resourcing_request_fields", []),
            "financial_information": data.getlist("financial_information_fields", []),
            "statement_of_work": data.getlist("statement_of_work_fields", []),
            "interim_request": data.getlist("interim_request_fields", []),
        }
        self.request.user.save()

        return redirect(
            reverse(
                "resourcing-request-summary-view",
                kwargs={"resourcing_request_pk": self.resourcing_request.pk},
            )
        )
