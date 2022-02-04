from django.template.defaulttags import register


@register.filter
def get_changes(instance, field_name="change_log"):
    if not hasattr(instance, field_name):
        return {}

    return getattr(instance, field_name).get_changes()


@register.filter
def has_field_previous_value(changes, field):
    return field.name in changes


@register.filter
def get_field_previous_value(changes, field):
    return changes.get(field.name)
