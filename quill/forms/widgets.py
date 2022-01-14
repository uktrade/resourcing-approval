from django.forms.widgets import Widget

from quill.constants import CSS, JS


class QuillWidget(Widget):
    class Media:
        js = JS
        css = CSS

    template_name = "quill/widget.html"

    def get_context(self, name, value, attrs):
        context = {
            "name": name,
            "module": f"quill_{name.replace('-', '_')}",
        }

        return super().get_context(name, value, attrs) | context
