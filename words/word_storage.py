import json
import os
from pathlib import Path

FILE_PATH = Path(__file__).parent / "data" / "words.json"


def get_temp_word_file_path() -> Path:
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    return Path(__file__).parent / "data" / f"temp_word_{worker_id}.json"


def load_words_from_file() -> list[dict]:
    if not FILE_PATH.exists():
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("words", [])


def save_words_to_file(data: list[dict]):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"words": data},
            file,
            ensure_ascii=False,
            indent=2
        )


def add_word(word: dict):
    data = load_words_from_file()
    data.append(word)
    save_words_to_file(data)


def load_word_from_temp_word_file() -> dict:
    file_path = get_temp_word_file_path()

    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_temp_eng_word(word: str):
    file_path = get_temp_word_file_path()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "word_eng": word,
                "translation": None
            },
            file,
            ensure_ascii=False,
            indent=2
        )


def save_temp_translation(translation: str):
    file_path = get_temp_word_file_path()

    data = load_word_from_temp_word_file()
    data["translation"] = translation

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def clear_temp_word_file():
    file_path = get_temp_word_file_path()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump({}, file, ensure_ascii=False, indent=2)