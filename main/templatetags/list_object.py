from django import template
from django.utils.text import capfirst


register = template.Library()


@register.inclusion_tag("main/partials/detail_list.html")
def object_as_list(object, exclude_list):
    data = {}

    for field in object._meta.fields:
        if field.name not in exclude_list:
            name = capfirst(field.verbose_name)

            value = (
                getattr(object, f"get_{field.name}_display")
                if hasattr(object, f"get_{field.name}_display")
                else getattr(object, field.name)
            )

            data[name] = value

    return {"display_list": data}
