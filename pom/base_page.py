import logging

import allure
from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pom.theme import Theme


class BasePage:
    URL = None

    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self.overlay_loader = ".v-overlay__content .v-progress-circular"
        self.linear_loaders = ".v-progress-linear__indeterminate--active"  # flaky
        self.user_avatar_button = self.page.get_by_role("banner").get_by_role("button")
        self.dropdown_user_menu = (self.page.get_by_role("menu")
                                   .filter(has=self.page.get_by_role("link", name="My account")))
        self.dark_theme_switch = self.page.get_by_role("banner").get_by_role("switch")
        self.alert_toast_message = self.page.get_by_role("alert")

    def __getattr__(self, item):
        return getattr(self.page, item)

    def open(self):
        if not self.URL:
            raise ValueError("URL is not defined for this page")
        self.page.goto(self.URL)

    def wait_until_element_disappears(self, selector: str, timeout: int = 10000,):
        self.page.wait_for_function(
            """
            (selector) => {
                return document.querySelectorAll(selector).length === 0;
            }
            """,
            arg=selector,
            timeout=timeout,
        )

    def wait_any_field_autofocus(self, timeout: int = 3000):
        try:
            self.page.wait_for_function(
                """
                () => {
                    const el = document.activeElement;
                    return el &&
                           el !== document.body &&
                           ['INPUT', 'TEXTAREA'].includes(el.tagName);
                }
                """,
                timeout=timeout,
            )
        except PlaywrightTimeoutError:
            self.logger.warning("Expected autofocus did not occur")

    def wait_for_overlay_loader_to_disappear(self, timeout: int = 10000):
        try:
            self.page.locator(self.overlay_loader).wait_for(state="visible")
            self.wait_until_element_disappears(self.overlay_loader, timeout)
        except PlaywrightTimeoutError:
            self.logger.warning("Expected overlay loader didn't occur or froze")

    def wait_for_full_load(self):
        self.logger.debug("Waiting for full page load")
        self.wait_for_overlay_loader_to_disappear()
        self.wait_any_field_autofocus()

    def get_current_app_theme(self) -> Theme:
        app = self.page.locator("#app")

        if app.evaluate("el => el.classList.contains('theme--dark')"):
            self.logger.debug("The application theme is dark")
            return Theme.DARK

        self.logger.debug("The application theme is light")
        return Theme.LIGHT

    @allure.step("Verify that logged in user email is correct")
    def verify_logged_user_email(self, email):
        self.user_avatar_button.click()
        expect(self.dropdown_user_menu).to_contain_text(email)
        self.user_avatar_button.click()

    @allure.step("Expect alert toast message text to have text {text}")
    def expect_alert_toast_to_have_text(self, text, timeout=5000):
        expect(self.alert_toast_message).to_have_text(text, timeout=timeout)
