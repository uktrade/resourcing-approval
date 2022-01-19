from django.shortcuts import render

from main.forms.tools import TotalBudgetCalculator


def total_budget_calculator(request):
    context = {}

    if request.method == "GET":
        form = TotalBudgetCalculator(initial=request.GET)
    elif request.method == "POST":
        form = TotalBudgetCalculator(data=request.POST)

        if form.is_valid():
            data = form.cleaned_data

            context["total"] = (
                (data["daily_rate"] * data["days"])
                + (data["monthly_admin_fee"] * data["months"])
                + (data["placement_fee"] if data["nominated"] else 0)
            )

    context["form"] = form

    return render(
        request, "main/partials/total-budget-calculator.html", context=context
    )
