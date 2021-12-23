from .page import Page


class DashboardPage(Page):
    def goto_create_resourcing_request(self):
        from .resourcing_request.create import CreateResourcingRequest

        self.driver.find_element_by_link_text("Create resourcing request").click()

        return CreateResourcingRequest(self.driver)
