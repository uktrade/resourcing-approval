from django import template


register = template.Library()


@register.inclusion_tag("main/partials/summary-row.html")
def field_summary(object, field_name):
    field = object._meta.get_field(field_name)

    value = (
        getattr(object, f"get_{field_name}_display")
        if field.choices
        else getattr(object, field_name)
    )

    return {"key": field.verbose_name.capitalize(), "value": value}
