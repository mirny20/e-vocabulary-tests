import allure
from playwright.sync_api import Page, Error, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pom.base_page import BasePage
from words import word_storage
from words.word_provider import WordProvider


class SetWordsTab(BasePage):
    WORD_ADDED_TOAST_TEXT = "has been added to dictionary"
    WORD_ALREADY_EXIST_ERROR_TEXT = "This word already exist"

    def __init__(self, page: Page):
        super().__init__(page)
        self.eng_word_field = self.page.get_by_role("textbox", name="Word")
        self.theme_field = self.page.get_by_role("textbox", name="Theme")
        self.dropdown_list = self.page.locator('[role="listbox"]')
        self.dropdown_list_option = self.page.get_by_role("option")
        self.dropdown_option_translation = self.dropdown_list_option.locator(".v-chip__content").first
        self.set_word_button = self.page.get_by_role("button", name="set word")
        self.word_field_alert = self.page.locator(".v-input__control").filter(has_text="Word").get_by_role("alert")

    @allure.step(f"Fill 'Word (en)' field with word")
    def fill_eng_word_field(self, word: str):
        self.eng_word_field.fill(word)

    def dropdown_list_has_available_translations(self) -> bool:
        try:
            self.dropdown_list.wait_for(timeout=15000, state="visible")
            return self.dropdown_list_option.count() > 0
        except PlaywrightTimeoutError:
            return False

    def get_all_translations_from_dropdown_list(self) -> list[str]:
        all_translations = []

        try:
            self.dropdown_list.wait_for(timeout=15000, state="visible")
        except PlaywrightTimeoutError:
            self.logger.warning("Dropdown list with translations wasn't displayed.")
            return all_translations

        for translation in self.dropdown_option_translation.all():
            all_translations.append(translation.text_content().strip())

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

    def choose_theme_from_dropdown_list(self, theme_name: str):
        self.theme_field.click()
        self.dropdown_list_option.get_by_text(theme_name, exact=True).click()

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
    def expect_successfully_added_word_alert(self):
        added_word = word_storage.load_word_from_temp_word_file()["word_eng"]
        expect(self.alert_toast_message).to_be_visible()
        self.expect_alert_toast_to_have_text(f"{added_word} {self.WORD_ADDED_TOAST_TEXT}")

    @allure.step("Fill the 'word' field with valid translatable random word")
    def fill_word_field_with_translatable_random_word(self, max_attempts=5):
        for _ in range(max_attempts):
            self.fill_word_field_with_random_word()

            if self.word_already_exist_error_is_displayed():
                self.logger.debug("Generated word already exists, trying another one")
                continue

            if not self.dropdown_list_has_available_translations():
                self.logger.debug("No translation for word, trying another one")
                continue

            return

        raise RuntimeError("Failed to find valid translatable word")

    def fill_word_field_with_random_word(self):
        word_provider = WordProvider()
        random_word = word_provider.get_random_english_word()
        self.fill_eng_word_field(random_word)
        word_storage.save_temp_eng_word(random_word)

    @allure.step("Choose first translation that appeared in the 'Translation' field")
    def choose_first_translation_from_dropdown_list(self):
        translation = self.get_all_translations_from_dropdown_list()[0]
        self.choose_translation_from_dropdown_list(translation)
        word_storage.save_temp_translation(translation)

    def word_already_exist_error_is_displayed(self) -> bool:
        return self.word_field_alert.get_by_text(self.WORD_ALREADY_EXIST_ERROR_TEXT).is_visible()