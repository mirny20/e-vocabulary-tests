import allure
import pytest

from pom.words_tab import WordsTab


@allure.title("Type correct word translations into word's card")
@pytest.mark.regression
def test_correct_translation(auth_page, word_with_translation, temp_word_lifecycle):
    words_tab = WordsTab(auth_page)

    words_tab.open_words_tab()
    words_tab.fill_translation_in_word_card(word_with_translation)

    words_tab.expect_word_card_to_have_mistakes_counter(word_with_translation)
    words_tab.expect_word_card_to_have_repeat_label(word_with_translation)
    words_tab.expect_word_card_to_be_hidden(word_with_translation)
    words_tab.reload()
    words_tab.expect_word_card_to_be_hidden(word_with_translation)