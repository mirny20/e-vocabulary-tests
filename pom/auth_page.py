import allure
from playwright.sync_api import Page, expect

from pom.base_page import BasePage
from pom.theme import Theme


class AuthPage(BasePage):
    URL = "/?#/auth"
    INVALID_CREDENTIALS_ERROR_TEXT = "User not found"

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_field = self.page.get_by_role("textbox", name="Username")
        self.password_field = self.page.get_by_role("textbox", name="Password")
        self.login_button = self.page.get_by_role("button", name="Login")
        self.switch_to_registration_button = self.get_by_role("button", name="switch to registration")

    @allure.step("Open auth page")
    def open(self):
        super().open()

    @allure.step("User fills in username field")
    def fill_in_username(self, username):
        self.username_field.fill(username)

    @allure.step("User clears the username field")
    def clear_username_field(self):
        self.username_field.clear()

    @allure.step("User fills in password field")
    def fill_in_password(self, password):
        self.password_field.fill(password)

    @allure.step("User clears the password field")
    def clear_password_field(self):
        self.password_field.clear()

    @allure.step("User clicks 'Login' button")
    def click_login_button(self):
        self.login_button.click()

    @allure.step("User logs in with creds")
    def perform_login(self, username, password):
        self.fill_in_username(username)
        self.fill_in_password(password)
        self.click_login_button()

    @allure.step("Expect login button to be disabled")
    def expect_login_button_disabled(self):
        current_theme = self.get_current_app_theme()
        colors = {
            Theme.LIGHT: "rgba(0, 0, 0, 0.12)",
            Theme.DARK: "rgba(255, 255, 255, 0.12)"
        }
        expect(self.login_button).to_be_disabled()
        expect(self.login_button).to_have_css("background-color", colors[current_theme])

    @allure.step("Expect login button to be enabled")
    def expect_login_button_enabled(self):
        current_theme = self.get_current_app_theme()
        colors = {
            Theme.LIGHT: "rgb(237, 118, 94)",
            Theme.DARK: "rgb(254, 168, 88)"
        }
        expect(self.login_button).to_have_css("background-color", colors[current_theme])
        expect(self.login_button).to_be_enabled()

    @allure.step("Expect invalid credentials alert toast message")
    def expect_invalid_credentials_error(self, timeout=5000):
        expect(self.alert_toast_message).to_be_visible()
        self.expect_alert_toast_to_have_text(self.INVALID_CREDENTIALS_ERROR_TEXT, timeout)