import datetime
from uuid import uuid4

from main.tests.selenium.pages.dev_tools import DevToolsPage
from main.models import ResourcingRequest, Profession
from user.models import User


def test_smoke_scenario(live_server, selenium):
    # Setup
    dev_tools = DevToolsPage(selenium)
    dev_tools.goto()

    assert "Dev tools" in selenium.title

    # Login as a hiring manager
    hiring_manager = User.objects.get(username="hiring-manager")

    dev_tools.change_user(hiring_manager)

    assert selenium.find_element_by_link_text(hiring_manager.get_full_name())

    # Goto the dashboard
    dashboard = dev_tools.goto_dashboard()

    assert "Dashboard" in selenium.title

    # Create resourcing request
    create_resourcing_request = dashboard.goto_create_resourcing_request()
    portfolio_uuid = generate_portfolio_uuid()
    view_resourcing_request = create_resourcing_request.create(
        type=ResourcingRequest.Type.NEW.value,
        job_title="Python Developer",
        project_name="JML",
        portfolio=portfolio_uuid,
        profession=Profession.objects.first().pk,
        start_date=datetime.date.today().strftime("%Y-%m-%d"),
        end_date=(datetime.date.today() + datetime.timedelta(days=6 * 30)).strftime(
            "%Y-%m-%d"
        ),
        is_ir35=True,
        chief=User.objects.get(username="chief").pk,
    )

    assert "Python Developer" in selenium.title

    request = ResourcingRequest.objects.get(pk=view_resourcing_request.id)

    assert request.portfolio == portfolio_uuid


def generate_portfolio_uuid():
    return f"selenium-test-{uuid4()}"
