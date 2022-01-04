from django.urls import reverse


def test_dashboard_page_loads_successfully(client, hiring_manager):
    r = client.get(reverse("dashboard"))
    assert r.status_code == 200
