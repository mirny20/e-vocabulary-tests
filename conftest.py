import os

import allure
import pytest
from playwright.sync_api import Browser, Playwright

from pom.auth_page import AuthPage
from pom.home_page import HomePage

USERNAME_MAIN_USER = os.environ['USERNAME_MAIN_USER']
PASSWORD_MAIN_USER = os.environ['PASSWORD_MAIN_USER']
EMAIL_MAIN_USER = os.environ['EMAIL_MAIN_USER']


@pytest.fixture(scope="session")
def base_url():
    return os.getenv(
        "BASE_URL",
        "https://e-vocabulary.vercel.app"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = None
        for fixture_name in ["anon_page", "auth_page"]:  # добавь сюда другие свои Page-фикстуры
            page = item.funcargs.get(fixture_name)
            if page:
                break

        if page:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="screenshot_on_fail",
                attachment_type=allure.attachment_type.PNG
            )


@pytest.fixture(scope="session")
def auth_context(playwright: Playwright, base_url):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    auth_state = f"state_{worker_id}.json"
    page.set_default_timeout(7000)
    auth_page = AuthPage(page)
    home_page = HomePage(page)
    home_page.goto(base_url)
    auth_page.perform_login(USERNAME_MAIN_USER, PASSWORD_MAIN_USER)
    home_page.wait_for_overlay_loader_to_disappear()
    home_page.words_tab.wait_for(state='visible')
    context.storage_state(path=auth_state)
    browser.close()
    yield auth_state
    os.remove(auth_state)


@pytest.fixture
def auth_page(browser: Browser, auth_context, base_url):
    context = browser.new_context(storage_state=auth_context, base_url=base_url)
    home_page = HomePage(context.new_page())
    home_page.set_default_timeout(7000)
    yield home_page
    context.close()


@pytest.fixture
def anon_page(browser: Browser, base_url):
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.set_default_timeout(7000)
    yield page
    context.close()
