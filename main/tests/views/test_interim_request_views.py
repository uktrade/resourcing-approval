from django.urls import reverse


class TestInterimRequestCreateView:
    def test_form_validation(self, client, hiring_manager, resourcing_request):
        form_data = {
            "uk_based": False,
        }

        r = client.post(
            reverse(
                "interim-request-create",
                kwargs={"resourcing_request_pk": resourcing_request.pk},
            ),
            data=form_data,
        )

        assert r.status_code == 200
        assert r.context["form"].errors.as_data()["overseas_country"]
