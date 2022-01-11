from django import template
from django.contrib.humanize.templatetags.humanize import intcomma


register = template.Library()


@register.filter
def currency(number: float) -> str:
    return f"£{intcomma(number)}"
