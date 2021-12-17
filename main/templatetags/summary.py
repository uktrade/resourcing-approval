from django import template
from django.utils.text import capfirst


register = template.Library()


@register.inclusion_tag("main/partials/summary-row.html")
def field_summary(object, field_name):
    field = object._meta.get_field(field_name)

    name = capfirst(field.verbose_name)

    value = (
        getattr(object, f"get_{field_name}_display")
        if field.choices
        else getattr(object, field_name)
    )

    return {"key": name, "value": value}
