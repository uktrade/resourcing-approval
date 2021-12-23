from main.tests.selenium.pages import Page
from main.tests.selenium.utils import fill_out_form


class CreateResourcingRequest(Page):
    def create(self, **form_data):
        from .view import ViewResourcingRequest

        form = self.driver.find_element_by_tag_name("form")

        fill_out_form(self.driver, form, **form_data)

        form.find_element_by_name("submit").click()

        return ViewResourcingRequest(self.driver)
