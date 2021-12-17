class FormMixin:
    """A view mixin for the standard form page form.html."""

    template_name = "main/form.html"
    title: str

    def get_context_data(self, **kwargs):
        context = {"title": self.title}

        return super().get_context_data(**kwargs) | context
