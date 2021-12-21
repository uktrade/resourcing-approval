from django.urls import reverse
from selenium.webdriver.support.ui import Select

from .page import Page


class DevToolsPage(Page):
    CHANGE_USER_FORM_ID = "change_user"

    def goto(self):
        self.get(reverse("dev_tools:index"))

    def change_user(self, user):
        form_el = self.driver.find_element_by_id(self.CHANGE_USER_FORM_ID)

        user_el = Select(form_el.find_element_by_name("user"))
        user_el.select_by_value(str(user.pk))

        form_el.find_element_by_name("submit").click()
