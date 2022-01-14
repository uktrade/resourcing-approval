from django.forms.fields import JSONField

from quill.forms.widgets import QuillWidget
from quill.utils import validate_value


class QuillField(JSONField):
    widget = QuillWidget

    def validate(self, value):
        super().validate(value)

        validate_value(value)
