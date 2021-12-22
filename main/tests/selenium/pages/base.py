from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.driver.implicitly_wait(10)

    def find_test_element(self, name: str) -> WebElement:
        """A shortcut method for finding a element by the `data-test-XXX` attribute.

        Args:
            name: The name given to the element, e.g. "foo-bar" -> "data-test-foo-bar"

        Returns:
            The matching web element.
        """
        return self.driver.find_element_by_css_selector(f"[data-test-{name}]")

    def find_test_elements(self, name: str) -> list[WebElement]:
        """A shortcut method for finding elements by the `data-test-XXX` attribute.

        Args:
            name: The name given to the elements, e.g. "foo-bar" -> "data-test-foo-bar"

        Returns:
            A list of matching web elements.
        """
        return self.driver.find_elements_by_css_selector(f"[data-test-{name}]")
