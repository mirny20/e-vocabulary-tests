import allure
from playwright.sync_api import Page, Error, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pom.base_page import BasePage


class SetWordsTab(BasePage):
    WORD_ADDED_TOAST_TEXT = "has been added to dictionary"

    def __init__(self, page: Page):
        super().__init__(page)
        self.eng_word_field = self.page.get_by_role("textbox", name="Word")
        self.theme_field = self.page.get_by_role("textbox", name="Theme")
        self.dropdown_list = self.page.locator('[role="listbox"]')
        self.dropdown_list_option = self.page.get_by_role("option")
        self.set_word_button = self.page.get_by_role("button", name="set word")

    @allure.step(f"Fill 'Word (en)' field with word")
    def fill_eng_word_field(self, word):
        self.eng_word_field.fill(word)

    def get_all_translations_from_dropdown_list(self) -> list[str]:
        all_translations = []

        try:
            self.dropdown_list.wait_for(timeout=25000, state="visible")
        except PlaywrightTimeoutError:
            self.logger.warning("Dropdown list with translations wasn't displayed.")
            return all_translations

        for translation in self.dropdown_list_option.all():
            all_translations.append(translation.text_content().rsplit(maxsplit=1)[0].strip())

        return all_translations

    @allure.step(f"Choose translation from 'Translate' field dropdown")
    def choose_translation_from_dropdown_list(self, translation):
        all_translations = self.get_all_translations_from_dropdown_list()

        if translation in all_translations:
            self.dropdown_list_option.get_by_text(translation, exact=True).click()
        else:
            raise RuntimeError(
                f"Translation '{translation}' not found in translation dropdown. "
                f"Available: {all_translations}"
            )

    def fill_in_theme_field(self, theme_name: str):
        self.theme_field.click()
        self.theme_field.fill(theme_name)

    def choose_theme_from_dropdown_list(self, them_name: str):
        self.theme_field.click()
        self.dropdown_list_option.get_by_text(them_name, exact=True).click()

    @allure.step("Choose default theme for word (select from dropdown or create it if necessary)")
    def choose_default_theme(self):
        try:
            self.choose_theme_from_dropdown_list("default_theme")

        except PlaywrightTimeoutError:
            self.logger.warning("Default theme not found, creating it")
            self.fill_in_theme_field("default_theme")

        except Error as e:
            self.logger.error(f"Unexpected error during choosing default theme: {e}")
            raise

    @allure.step("Click 'SET WORD' button")
    def click_set_word_button(self):
        self.set_word_button.click()

    @allure.step("Expect alert of a successfully added word to be displayed with correct text")
    def expect_successfully_added_word_alert(self, word_added: str):
        expect(self.alert_toast_message).to_be_visible()
        self.expect_alert_toast_to_have_text(f"{word_added} {self.WORD_ADDED_TOAST_TEXT}")
