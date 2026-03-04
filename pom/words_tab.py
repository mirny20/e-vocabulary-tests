import allure
from playwright.sync_api import Page, Locator, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pom.base_page import BasePage
from pom.home_page import HomePage


class WordsTab(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.word_card = self.page.locator("[class^='word v-card']")
        self.word_card_unloaded_element = self.page.locator("[class='v-lazy']")
        self.word_card_text = self.word_card.locator("[class^='v-card__title']>span:first-of-type")
        self.pagination_button = self.page.get_by_role("navigation").nth(1).get_by_role("button")
        self.pagination_next_page_button = self.page.get_by_role("button", name="Next page").nth(1)

    @allure.step("Open words tab")
    def open_words_tab(self):
        home_page = HomePage(self.page)
        home_page.open()
        home_page.switch_to_words_tab()

    @allure.step("Fill translation input in the word card")
    def fill_translation_in_word_card(self, word_with_translation: dict):
        word = word_with_translation["word_eng"]
        translation = word_with_translation["translation"]

        self.logger.debug(f"Filling translation '{translation}' for word: '{word}'")

        self._scroll_through_all_word_cards()

        word_card_input_cells = self._get_word_card_input_cells(word)

        for cell, char in zip(word_card_input_cells, translation):
            cell.fill(char)

    @allure.step("Mistakes counter is displayed on the word card")
    def expect_word_card_to_have_mistakes_counter(self, word_with_translation: dict):
        word_card = self.word_card.filter(has_text=word_with_translation["word_eng"])
        expect(word_card).to_contain_text("Mistakes:")

    @allure.step("Repeat label is displayed on the word card")
    def expect_word_card_to_have_repeat_label(self, word_with_translation: dict):
        word_card = self.word_card.filter(has_text=word_with_translation["word_eng"])
        expect(word_card).to_contain_text("need repeat:")

    @allure.step("Expect word card not to be displayed on the 'words' tab")
    def expect_word_card_to_be_hidden(self, word_with_translation: dict, timeout=10000):
        self._scroll_through_all_word_cards()
        word_card = self.word_card.filter(has_text=word_with_translation["word_eng"])
        expect(word_card).to_be_hidden(timeout=timeout)

    def get_words_from_all_cards_on_page(self) -> list[str]:
        all_words = []
        self._scroll_through_all_word_cards()

        for word in self.word_card_text.all():
            all_words.append(word.text_content().split()[0])

        self.logger.debug(f"{len(all_words)} word cards are present on page: {all_words}")

        return all_words

    def _get_word_card_input_cells(self, word: str) -> list[Locator]:
        self._scroll_through_all_word_cards()

        word_card = self.word_card.filter(has_text=word)
        input_cells = word_card.get_by_role("textbox").all()

        return input_cells

    def _scroll_through_all_word_cards(self, max_cards_per_page=10):
        for i in range(max_cards_per_page):
            try:
                self.word_card_unloaded_element.nth(i).scroll_into_view_if_needed()
                expect(self.word_card.nth(i)).to_be_visible()

            except PlaywrightTimeoutError:
                if self._last_words_page_opened():
                    self.logger.debug("Last page of 'Words' tab with less than 10 word cards is displayed")
                    break
                else:
                    self.logger.warning("Failed to load all word cards after scrolling")

    def _last_words_page_opened(self) -> bool:
        self.pagination_next_page_button.scroll_into_view_if_needed()

        pagination_buttons = self.pagination_button.all()
        current_page_att = pagination_buttons[-2].get_attribute("aria-current")

        if current_page_att:
            return True

        return False

