from django.core.exceptions import ValidationError


def validate_value(value):
    if value is None:
        return

    if value == {}:
        return

    if not isinstance(value, dict):
        raise ValidationError(
            "Value must be a object.",
            code="invalid",
            params={"value": value},
        )

    if "delta" not in value:
        raise ValidationError(
            "Value object must have a delta key.",
            code="invalid",
            params={"value": value},
        )


def extract_text(value) -> str:
    if value in ({}, None):
        return ""

    ops = value["delta"]["ops"]

    text = []
    for op in ops:
        text.append(op["insert"])

    return "".join(text)
