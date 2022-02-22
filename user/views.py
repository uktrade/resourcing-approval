from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView

from user.models import User


class EditUserView(SuccessMessageMixin, UpdateView):
    model = User
    fields = ["profession", "preferred_email"]
    template_name = "user/edit-user.html"
    context_object_name = "user"
    success_message = "User updated"

    def get_context_data(self, **kwargs):
        user = self.request.user

        context = {
            "show_profession_warning": (
                user.is_head_of_profession and not user.profession
            ),
            "show_approver_warning": user.is_in_approver_group and not user.is_approver,
        }

        return super().get_context_data(**kwargs) | context
