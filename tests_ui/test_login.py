import pytest
from playwright.sync_api import Page

from conftest import USERNAME_MAIN_USER, PASSWORD_MAIN_USER, EMAIL_MAIN_USER
from pom.auth_page import AuthPage
from pom.home_page import HomePage


@pytest.mark.smoke
def test_authentication(anon_page: Page):
    auth_page = AuthPage(anon_page)
    home_page = HomePage(anon_page)
    auth_page.open()
    auth_page.perform_login(USERNAME_MAIN_USER, PASSWORD_MAIN_USER)
    home_page.wait_for_full_load()
    home_page.verify_logged_user_email(EMAIL_MAIN_USER)


@pytest.mark.development
def test_login_button_states(anon_page: Page):
    auth_page = AuthPage(anon_page)
    auth_page.open()
    auth_page.expect_login_button_disabled()
    auth_page.fill_in_username("test")
    auth_page.expect_login_button_disabled()
    auth_page.fill_in_password("test")
    auth_page.expect_login_button_enabled()
    auth_page.clear_username_field()
    auth_page.expect_login_button_disabled()
