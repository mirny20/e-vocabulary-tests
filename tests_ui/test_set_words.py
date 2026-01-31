import allure
import pytest
from playwright.sync_api import Page

from pom.home_page import HomePage
from pom.set_words_tab import SetWordsTab


@allure.title("Add new word to the dictionary (set up word)")
@pytest.mark.regression
def test_set_word(auth_page: Page, temp_word_lifecycle):
    home_page = HomePage(auth_page)
    set_words_tab = SetWordsTab(auth_page)

    home_page.open()
    home_page.switch_to_set_words_tab()

    set_words_tab.fill_word_field_with_translatable_random_word()
    set_words_tab.choose_first_translation_from_dropdown_list()
    set_words_tab.choose_default_theme()
    set_words_tab.click_set_word_button()

    set_words_tab.expect_successfully_added_word_alert()
