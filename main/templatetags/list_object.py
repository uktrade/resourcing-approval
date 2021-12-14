from django import template


register = template.Library()


@register.inclusion_tag("main/partials/detail_list.html")
def object_as_list(object, exclude_list):
    data = {}

    for field in object._meta.fields:
        if field.name not in exclude_list:
            value = (
                getattr(object, f"get_{field.name}_display")
                if hasattr(object, f"get_{field.name}_display")
                else getattr(object, field.name)
            )

            data[field.verbose_name.capitalize()] = value

    return {"display_list": data}
