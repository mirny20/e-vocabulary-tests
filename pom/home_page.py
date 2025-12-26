import allure
from playwright.sync_api import Page

from pom.base_page import BasePage


class HomePage(BasePage):
    URL = "/?#/home/"

    def __init__(self, page: Page):
        super().__init__(page)
        ''' Home page tabs locators '''
        self.words_tab = self.page.get_by_role("tab", name="Words", exact=True)
        self.irregular_verbs_tab = self.page.get_by_role("tab", name="Irregular_Verbs")
        self.words_translated_tab = self.page.get_by_role("tab", name="Words_Translated", exact=True)
        self.update_words_tab = self.page.get_by_role("tab", name="Update_words")
        self.set_words_tab = self.page.get_by_role("tab", name="Set_Words")
        self.repeat_words_tab = self.page.get_by_role("tab", name="Repeat_Words", exact=True)
        self.repeat_words_translated_tab = self.page.get_by_role("tab", name="Repeat_Words_Translated")
        self.dictionary_tab = self.page.get_by_role("tab", name="Dictionary", exact=True)
        self.dictionary_translate_tab = self.page.get_by_role("tab", name="Dictionary_Translate")
        self.archive_tab = self.page.get_by_role("tab", name="Archive")

    @allure.step("Open auth page")
    def open(self):
        super().open()

    def switch_to_words_tab(self):
        self.words_tab.click()
        self.wait_any_field_autofocus()

    def switch_to_irregular_verbs_tab(self):
        self.irregular_verbs_tab.click()

    def switch_to_words_translated_tab(self):
        self.words_translated_tab.click()
        self.wait_any_field_autofocus()

    def switch_to_update_words_tab(self):
        self.update_words_tab.click()

    def switch_to_set_words_tab(self):
        self.set_words_tab.click()
        self.wait_any_field_autofocus()

    def switch_to_repeat_words_tab(self):
        self.repeat_words_tab.click()

    def switch_to_repeat_words_translated_tab(self):
        self.repeat_words_translated_tab.click()

    def switch_to_dictionary_tab(self):
        self.dictionary_tab.click()

    def switch_to_dictionary_translate_tab(self):
        self.dictionary_translate_tab.click()

    def switch_to_archive_tab(self):
        self.archive_tab.click()