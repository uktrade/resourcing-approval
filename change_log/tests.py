import pytest

from change_log.utils import get_instance_value


class Field:
    def __init__(self, name="foo", is_relation=False):
        self.name = name
        self.is_relation = is_relation


class Instance:
    def __init__(self, value):
        self.value = value

    @property
    def foo(self):
        return self.value


class InstanceWithDisplay(Instance):
    def __init__(self, *args, display, **kwargs):
        super().__init__(*args, **kwargs)

        self.display = display

    def get_foo_display(self):
        return self.display


@pytest.mark.parametrize(
    ["instance", "field", "expected"],
    [
        (Instance(value=42), Field(), 42),
        (Instance(value=42), Field(is_relation=True), "42"),
        (Instance(value=None), Field(), None),
        (InstanceWithDisplay(value=42, display="forty two"), Field(), "forty two"),
    ],
)
def test_get_instance_value(instance, field, expected):
    value = get_instance_value(instance, field)
    assert value == expected
