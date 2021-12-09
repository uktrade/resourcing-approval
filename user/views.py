from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView

from user.models import User


class EditUserView(SuccessMessageMixin, UpdateView):
    model = User
    fields = ["profession"]
    template_name = "user/edit-user.html"
    context_object_name = "user"
    success_message = "User updated"
