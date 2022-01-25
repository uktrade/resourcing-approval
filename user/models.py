from typing import TypedDict

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from main.models import Approval


SummaryConfigFields = dict[str, list[str]]


class SummaryConfig(TypedDict):
    fields: SummaryConfigFields


class User(AbstractUser):
    profession = models.ForeignKey(
        "main.Profession", models.PROTECT, null=True, blank=True
    )

    summary_config = models.JSONField(default=dict)

    def __str__(self):
        return self.get_full_name() or self.get_username()

    def get_absolute_url(self):
        return reverse("user:edit-user", kwargs={"pk": self.pk})

    @property
    def is_approver(self):
        return any(
            self.has_perm(f"main.can_give_{x.value}_approval") for x in Approval.Type
        )

    def has_approval_perm(self, approval_type):
        return self.has_perm(f"main.can_give_{approval_type.value}_approval")

    @property
    def is_head_of_profession(self):
        return self.has_approval_perm(Approval.Type.HEAD_OF_PROFESSION)

    @property
    def is_busops(self):
        return self.has_approval_perm(Approval.Type.BUSOPS)

    @property
    def summary_fields(self) -> SummaryConfigFields:
        return self.summary_config.get("fields", {})

    @summary_fields.setter
    def summary_fields(self, value: SummaryConfigFields) -> None:
        self.summary_config["fields"] = value
