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
        context["awaiting_your_approval"] = self._get_awaiting_approval_context_data()
        context["approved_by_you"] = self._get_approved_by_you_context_data()

        if user.has_perm("main.can_give_busops_approval"):
            context["amended_resourcing_requests"] = ResourcingRequest.objects.filter(
                state=ResourcingRequest.State.AMENDMENTS_REVIEW
            )

        return context

    def _get_awaiting_approval_context_data(self):
        approval_filter = Q()

        for approval_type in get_user_related_approval_types(self.request.user):
            approval_filter |= (
                Q(**{f"{approval_type}_approval__isnull": True})
                | Q(**{f"{approval_type}_approval__approved__isnull": True})
                | Q(**{f"{approval_type}_approval__approved": False})
            )

        if not approval_filter:
            return

        query = ResourcingRequest.objects.filter(
            Q(state=ResourcingRequest.State.AWAITING_APPROVALS) & approval_filter
        ).distinct()

        return query

    def _get_approved_by_you_context_data(self):
        return ResourcingRequest.objects.filter(approvals__user=self.request.user)
