from django.db.models import Q
from django.shortcuts import redirect
from django.urls.base import reverse
from django.views.generic.base import TemplateView

from main.models import ResourcingRequest
from main.utils import get_user_related_approval_types


def index(request):
    return redirect(reverse("dashboard"))


class DashboardView(TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["your_resourcing_requests"] = user.resourcing_requests.all()
        context["awaiting_your_approval"] = self.get_awaiting_approval_context_data()

        if user.is_superuser:
            context["all_resourcing_requests"] = ResourcingRequest.objects.all()

        return context

    def get_awaiting_approval_context_data(self):
        approval_filter = Q()

        for approval_type in get_user_related_approval_types(self.request.user):
            approval_filter |= (
                Q(**{f"{approval_type}_approval__isnull": True})
                | Q(**{f"{approval_type}_approval__approved__isnull": True})
                | Q(**{f"{approval_type}_approval__approved": False})
            )

        query = ResourcingRequest.objects.filter(
            Q(state=ResourcingRequest.State.AWAITING_APPROVALS) & approval_filter & Q()
        ).distinct()

        return query
