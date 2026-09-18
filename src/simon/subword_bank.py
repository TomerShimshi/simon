import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / "data"


def load_bank() -> dict[str, list[str]]:
    return json.loads((_DATA_DIR / "subword_bank.json").read_text(encoding="utf-8"))


def load_clues() -> dict[str, str]:
    return json.loads((_DATA_DIR / "subword_clues.json").read_text(encoding="utf-8"))
