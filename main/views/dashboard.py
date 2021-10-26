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

        return context

    def get_awaiting_approval_context_data(self):
        query = ResourcingRequest.objects.filter(
            Q(state=ResourcingRequest.State.AWAITING_APPROVALS)
            & Q(approvals__type__in=get_user_related_approval_types(self.request.user))
            & (Q(approvals__approved__isnull=True) | Q(approvals__approved=False))
        ).distinct()

        return query
