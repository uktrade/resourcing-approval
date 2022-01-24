from typing import Optional


class FormMixin:
    """A view mixin for the standard form page form.html."""

    template_name = "main/form.html"
    title: str
    form_help_text: Optional[str] = None

    def get_context_data(self, **kwargs):
        context = {
            "title": self.title,
            "form_help_text": self.form_help_text,
        }

        return super().get_context_data(**kwargs) | context
