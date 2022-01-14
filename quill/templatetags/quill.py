from django import template
from django.forms.widgets import Media

from quill.constants import CSS, JS


register = template.Library()


@register.simple_tag
def quill_media() -> str:
    return Media(js=JS, css=CSS).render()
