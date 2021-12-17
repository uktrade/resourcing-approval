from typing import Union

from django import template
from django.db.models import Model
from django.db.models.fields import Field
from django.db.models.fields.reverse_related import ForeignObjectRel


register = template.Library()


@register.filter
def field(obj: Model, field_name: str) -> Field:
    return obj._meta.get_field(field_name)


@register.filter
def fields(obj: Model) -> list[Union[Field, ForeignObjectRel]]:
    return obj._meta.get_fields()


@register.filter
def verbose_name(field) -> str:
    return getattr(field, "verbose_name", field.name)


@register.filter
def help_text(field) -> str:
    return getattr(field, "help_text", "")


@register.filter
def value(obj: Model, field_name: str) -> str:
    if hasattr(obj, f"get_{field_name}_display"):
        return getattr(obj, f"get_{field_name}_display")()

    return getattr(obj, field_name)
