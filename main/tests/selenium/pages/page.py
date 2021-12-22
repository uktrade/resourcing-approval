from main.tests.selenium.constants import BASE_URL

from .base import BasePage


class Page(BasePage):
    def goto_dashboard(self):
        from .dashboard import DashboardPage

        self.driver.find_element_by_link_text("Dashboard").click()

        return DashboardPage(self.driver)

    def get(self, path):
        self.driver.get(BASE_URL + path)
