from django import forms
from django.forms import widgets

from main.models import InterimRequest


class InterimRequestNewForm(forms.ModelForm):
    date_error_msg = "Anticipated end date cannot be before anticipated start date"

    class Meta:
        model = InterimRequest
        fields = "__all__"
        widgets = {"resourcing_request": widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resourcing_request"].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        uk_based = cleaned_data.get("uk_based")
        overseas_country = cleaned_data.get("overseas_country")

        if not uk_based and not overseas_country:
            self.add_error(
                "overseas_country",
                "You must select a country when the role is not UK based.",
            )

        return cleaned_data
