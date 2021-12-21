from main.tests.selenium.pages.dev_tools import DevToolsPage
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
    dev_tools.goto_dashboard()

    assert "Dashboard" in selenium.title
