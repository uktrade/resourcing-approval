from django import template
from django.forms import widgets

register = template.Library()


@register.simple_tag
def add_class(field, *classes) -> str:
    # `field.field` is needed as `field` is a `BoundField`
    field.field.widget.attrs["class"] = " ".join(
        [field.field.widget.attrs.get("class", ""), *classes]
    )

    return ""


@register.simple_tag
def add_gds_input_class(field) -> str:
    widget = field.field.widget

    input_widgets = (widgets.TextInput, widgets.DateInput, widgets.DateTimeInput)

    if isinstance(widget, input_widgets):
        add_class(field, "govuk-input")
    elif isinstance(widget, widgets.Select):
        add_class(field, "govuk-select")
    elif isinstance(widget, widgets.Textarea):
        add_class(field, "govuk-textarea")

    return ""
