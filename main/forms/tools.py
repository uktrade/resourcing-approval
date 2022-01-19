from django import forms


class TotalBudgetCalculator(forms.Form):
    daily_rate = forms.IntegerField()
    days = forms.IntegerField()
    months = forms.IntegerField()
    monthly_admin_fee = forms.IntegerField(initial=229)
    nominated = forms.ChoiceField(choices=[("True", "Yes"), ("False", "No")])
    placement_fee = forms.IntegerField(initial=9_000)

    def clean_nominated(self):
        return True if self.cleaned_data["nominated"] == "True" else False
