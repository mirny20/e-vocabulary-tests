import json
from pathlib import Path

FILE_PATH = Path(__file__).parent / "data" / "words.json"


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