import os

import allure
import pytest
from playwright.sync_api import Browser, Playwright, Page

from pom.auth_page import AuthPage
from pom.home_page import HomePage
from words import word_storage

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

    setattr(item, "rep_" + rep.when, rep)

    if rep.when != "call" or rep.outcome == "passed":
        return

    page = None

    for arg in item.funcargs.values():
        if isinstance(arg, Page):
            page = arg
            break

        if hasattr(arg, "page") and isinstance(arg.page, Page):
            page = arg.page
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
    browser = playwright.chromium.launch()
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.set_default_timeout(7000)

    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    auth_state = f"state_{worker_id}.json"

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


@pytest.fixture
def temp_word_lifecycle(request):
    yield

    if request.node.rep_call.passed:
        temp_word = word_storage.load_word_from_temp_word_file()
        if temp_word:
            word_storage.add_word(temp_word)

    word_storage.clear_temp_word_file()
