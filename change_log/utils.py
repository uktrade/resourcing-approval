def get_instance_value(instance, field):
    """Return a field value from the instance.

    Args:
        instance: Django model instance.
        field: Django field from the instance.

    Returns:
        A value which can be used as a previous value in the change log.
    """

    if hasattr(instance, f"get_{field.name}_display"):
        return getattr(instance, f"get_{field.name}_display")()

    value = getattr(instance, field.name, None)

    if value is None:
        return None

    if field.is_relation:
        return str(value)

    return value
