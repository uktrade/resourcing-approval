from django import template


register = template.Library()


@register.inclusion_tag("main/partials/detail_list.html")
def object_as_list(object, exclude_list):
    data = {}
    for field in object._meta.fields:
        if field.name not in exclude_list:
            data[field.verbose_name.capitalize()] = getattr(object, field.name)
    return {"display_list": data}
