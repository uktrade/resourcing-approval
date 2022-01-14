import pytest
from django.core.exceptions import ValidationError

from quill.utils import validate_value


@pytest.mark.parametrize(
    "value",
    [
        {"delta": {"ops": []}},
        {},
        None,
    ],
)
def test_validate_value_with_valid_value(value):
    assert validate_value(value) is None


@pytest.mark.parametrize(
    ["value", "message"],
    [
        ([], "Value must be a object."),
        ({"not_delta": {}}, "Value object must have a delta key."),
    ],
)
def test_validate_value_with_invalid_value(value, message):
    with pytest.raises(ValidationError, match=message):
        validate_value(value)
