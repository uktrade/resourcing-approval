from django.views import View

from main.models import ResourcingRequest


class ResourcingRequestBaseView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.resourcing_request = (
            ResourcingRequest.objects.select_related_approvals().get(
                pk=self.kwargs["resourcing_request_pk"]
            )
        )

        self.resourcing_request_url = self.request.build_absolute_uri(
            self.resourcing_request.get_absolute_url()
        )
