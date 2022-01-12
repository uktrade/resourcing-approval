from django.db.models import JSONField

import quill.forms.fields as fields
from quill.utils import validate_value


class QuillField(JSONField):
    """A JSON field subclass which validates and stores Quill's delta data format.

    - The default is fixed to an empty dict.
    - The associated form field and widget will normalize empty values to an empty dict.
    - `null=True` is supported if you need it.
    """

    def __init__(self, *args, **kwargs):
        kwargs["default"] = dict
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)

        validate_value(value)

    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": fields.QuillField} | kwargs)
