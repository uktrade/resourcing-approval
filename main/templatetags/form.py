from django import template


register = template.Library()


@register.inclusion_tag("main/partials/forms/field.html")
def field(field, optional_text=None):
    return {
        "field": field,
        "optional_text": optional_text,
    }
