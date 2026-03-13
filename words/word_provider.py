import logging
import re
import randword
from deep_translator import LingueeTranslator, GoogleTranslator
from deep_translator.exceptions import ElementNotFoundInGetRequest, TooManyRequests


class WordProvider:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_random_english_word(self, max_attempts=15) -> str:
        pattern = re.compile(r"^[a-z]+$")

        for _ in range(max_attempts):
            word = randword.word()
            if pattern.fullmatch(word):
                self.logger.debug(f"Generated word: {word}")
                return word

        raise RuntimeError("Failed to generate word")

    def get_translation_from_english(self, word) -> str:
        translators = [LingueeTranslator, GoogleTranslator]
        pattern = re.compile(r"^[а-яА-Я]+$")
        last_exception = None

        for translator in translators:
            try:
                translated_word = translator(source='english', target='russian').translate(word)
                self.logger.debug(f"Translation with {translator.__name__}: {translated_word}")
                if pattern.fullmatch(translated_word):
                    return translated_word
                else:
                    self.logger.debug(f"Word '{translated_word}' contains incompatible characters")
            except (ElementNotFoundInGetRequest, TooManyRequests) as e:
                last_exception = e
                self.logger.warning(f"No translation or too many requests with {translator.__name__}, "
                                    f"trying another translator")

        raise RuntimeError(f"No translator succeeded for word '{word}'") from last_exception

    def get_word_with_translation(self, max_attempts=15) -> dict[str, str]:
        result = {
            "word_eng": None,
            "translation": None
        }

        for attempt in range(1, max_attempts + 1):
            try:
                result["word_eng"] = self.get_random_english_word()
                result["translation"] = self.get_translation_from_english(result["word_eng"])
                return result
            except RuntimeError as e:
                self.logger.debug(f"No translator succeeded for word '{result['word_eng']}'. "
                                  f"Attempts left:  {attempt}/{max_attempts}."
                                  f"Reason: {e}")

        raise RuntimeError(f"Failed to get word with translation after {max_attempts} attempts")
