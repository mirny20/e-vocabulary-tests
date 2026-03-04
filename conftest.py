import logging
import os

import allure
import pytest
from playwright.sync_api import Browser, Playwright, Page
from pytest_playwright.pytest_playwright import browser

from pom.auth_page import AuthPage
from pom.home_page import HomePage
from pom.set_words_tab import SetWordsTab
from pom.words_tab import WordsTab
from words import word_storage

USERNAME_MAIN_USER = os.environ['USERNAME_MAIN_USER']
PASSWORD_MAIN_USER = os.environ['PASSWORD_MAIN_USER']
EMAIL_MAIN_USER = os.environ['EMAIL_MAIN_USER']
logger = logging.getLogger(__name__)


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


@pytest.fixture
def word_with_translation(playwright, base_url):
    browser = playwright.chromium.launch()
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    auth_state = f"state_{worker_id}.json"

    context = browser.new_context(storage_state=auth_state, base_url=base_url)
    page = context.new_page()

    set_words_tab = SetWordsTab(page)
    words_tab = WordsTab(page)

    words_tab.open_words_tab()

    words_from_storage = word_storage.load_words_from_file()
    user_words = words_tab.get_words_from_all_cards_on_page()

    word_with_translation = {}

    for word in words_from_storage:
        if word["word_eng"] in user_words:
            logger.info(f"Word '{word}' founded in word storage")
            word_with_translation = word
            break

    if not word_with_translation:
        logger.info(f"No suitable word was found in the word storage. Adding new word with 'set word' functionality'")
        set_words_tab.open_set_words_tab()
        set_words_tab.fill_word_field_with_translatable_random_word()
        set_words_tab.choose_first_translation_from_dropdown_list()
        set_words_tab.choose_default_theme()
        set_words_tab.click_set_word_button()

        word_with_translation = word_storage.load_word_from_temp_word_file()
        logger.info(f"Word {word_with_translation} was added to dictionary")

    if word_with_translation:
        logger.info(f"Yielding {word_with_translation}")
        yield word_with_translation

    context.close()
    browser.close()