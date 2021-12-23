from main.tests.selenium.pages import Page


class ViewResourcingRequest(Page):
    @property
    def id(self):
        return int(self.driver.find_element_by_id("id").get_attribute("value"))
