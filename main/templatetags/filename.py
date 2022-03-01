from pathlib import Path

from django import template


register = template.Library()


@register.filter
def filename(value):
    return Path(value.file.name).name
