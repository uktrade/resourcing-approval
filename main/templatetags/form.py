from django import template


register = template.Library()


@register.inclusion_tag("main/partials/forms/field.html")
def field(field):
    return {"field": field}
