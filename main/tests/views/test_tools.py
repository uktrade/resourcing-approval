import pytest
from django.urls import reverse


class TestTotalBudgetCalculator:
    def test_get(self, client, hiring_manager):
        r = client.get(reverse("htmx-total-budget-calculator"))
        assert r.context["form"]

    @pytest.mark.parametrize(
        ["nominated", "total"],
        [
            ("True", 70374),
            ("False", 61374),
        ],
    )
    def test_post_valid_nominated(self, client, hiring_manager, nominated, total):
        data = {
            "daily_rate": 500,
            "days": 120,
            "months": 6,
            "monthly_admin_fee": 229,
            "placement_fee": 9_000,
            "nominated": nominated,
        }
        r = client.post(reverse("htmx-total-budget-calculator"), data=data)
        assert r.context["total"] == total
