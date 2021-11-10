from django import template


register = template.Library()

@register.inclusion_tag("main/partials/detail_list.html")
def object_as_list(object, exclude_list=["id", "resourcing_request"]):
    data = []
    for field in object._meta.fields:
        if field.name not in exclude_list:
            data.append((field.verbose_name.capitalize(), getattr(object, field.name)))
    return {"display_list": data}
