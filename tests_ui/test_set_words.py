import pytest
from playwright.sync_api import Page

from pom.home_page import HomePage
from pom.set_words_tab import SetWordsTab


@pytest.mark.regression
def test_set_words(auth_page: Page, generated_word: dict):
    home_page = HomePage(auth_page)
    set_words_tab = SetWordsTab(auth_page)

    home_page.open()
    home_page.switch_to_set_words_tab()

    set_words_tab.fill_eng_word_field(generated_word["word_eng"])
    set_words_tab.choose_translation_from_dropdown_list(generated_word["translation"])
    set_words_tab.choose_default_theme()
    set_words_tab.click_set_word_button()

    set_words_tab.expect_successfully_added_word_alert(generated_word["word_eng"])
