"""One-off, offline content-generation pipeline for the sub-word game.

Not run at app runtime, not unit tested (matches the sibling word_compiliotns
project's fetch scripts). Downloads kaikki.org's Hebrew Wiktionary extract
(real, editorially-reviewed dictionary entries) purely as a temporary
validator, computes a base_word -> [valid sub-words] mapping, and writes the
small resulting bank to src/simon/data/subword_bank.json. The big dictionary
itself is never shipped with the app or queried at runtime.

Usage:
    python scripts/generate_subword_bank.py [--source path/to/kaikki.jsonl]

If --source is omitted, downloads the dataset from kaikki.org into a local
cache file (scripts/.cache/kaikki_he_raw.jsonl) and reuses it on subsequent
runs.
"""

import argparse
import collections
import json
import sys
import unicodedata
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simon.hebrew_letters import to_base_form  # noqa: E402

KAIKKI_URL = "https://kaikki.org/dictionary/Hebrew/kaikki.org-dictionary-Hebrew.jsonl"
CACHE_PATH = Path(__file__).resolve().parent / ".cache" / "kaikki_he_raw.jsonl"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "src" / "simon" / "data" / "subword_bank.json"

HEBREW_LETTERS = set("אבגדהוזחטיכלמנסעפצקרשתךםןףץ")

BASE_WORD_POS = {"noun", "adj"}
# Verb lemmas (infinitives) are allowed as sub-words, but conjugated verb
# *forms* are only pulled in selectively (see FORM_TAGS_INCLUDE below) --
# past/future tense forms across every person/gender/number are the
# overwhelming majority of a verb's forms and are individually "real"
# dictionary entries, but they'd flood the results with obscure fragments
# (e.g. "תאמרן", "ותרא") that aren't satisfying, recognizable finds for a
# word-recall exercise. Imperative and present-tense forms are common,
# everyday words worth including (e.g. the imperative "הבט" = "look!").
SUBWORD_POS = {"noun", "adj", "adv", "pron", "num", "conj", "prep", "intj", "det", "verb"}
FORM_TAGS_INCLUDE = {"imperative"}

MIN_BASE_LEN = 5
MAX_BASE_LEN = 7
MIN_SUBWORD_LEN = 2
MIN_SUBWORDS_PER_BASE = 3
MAX_SUBWORDS_PER_BASE = 20


def _is_clean_hebrew(word: str) -> bool:
    return bool(word) and all(ch in HEBREW_LETTERS for ch in word)


def _strip_niqqud(word: str) -> str:
    """Removes Hebrew vowel-point (niqqud) combining marks, e.g. turning
    the vowelized imperative form "הַבֵּט" into the plain "הבט" that a
    player would actually type/tap."""
    return "".join(ch for ch in word if not unicodedata.combining(ch))


def _download(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {KAIKKI_URL} -> {dest}")
    urllib.request.urlretrieve(KAIKKI_URL, dest)


def load_dictionary(source: Path) -> dict[str, str]:
    """Returns {normalized_form: display_form} for every clean, single-word
    entry whose part of speech is in SUBWORD_POS, plus (for those same
    entries) any inflected forms tagged with FORM_TAGS_INCLUDE -- e.g. a
    verb's imperative/present forms, which are common everyday words even
    though the wiktextract dump only lists the infinitive as the top-level
    "word". Forms come with niqqud (vowel points) and must be stripped
    before use. First occurrence wins on collision (collisions are rare)."""
    dictionary: dict[str, str] = {}
    with source.open(encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            pos = entry.get("pos")
            if pos not in SUBWORD_POS:
                continue

            word = entry.get("word", "")
            if _is_clean_hebrew(word):
                dictionary.setdefault(to_base_form(word), word)

            for form in entry.get("forms", []):
                if not FORM_TAGS_INCLUDE.intersection(form.get("tags", [])):
                    continue
                form_word = _strip_niqqud(form.get("form", ""))
                if _is_clean_hebrew(form_word):
                    dictionary.setdefault(to_base_form(form_word), form_word)
    return dictionary


def load_base_word_candidates(source: Path) -> list[str]:
    """Distinct noun/adjective display-form words in the target length
    range, used as candidate base words."""
    candidates: set[str] = set()
    with source.open(encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            pos = entry.get("pos")
            word = entry.get("word", "")
            if pos not in BASE_WORD_POS or not _is_clean_hebrew(word):
                continue
            if MIN_BASE_LEN <= len(word) <= MAX_BASE_LEN:
                candidates.add(word)
    return sorted(candidates)


def find_subwords(base_word: str, dictionary: dict[str, str]) -> list[str]:
    """Every dictionary word (any part of speech) whose letters are a
    sub-multiset of base_word's letters -- i.e. can be spelled using only
    letters available in base_word, respecting how many times each letter
    appears. Anagram-style: any subset, any order, matching how the tile-tap
    UI lets the player tap letters in whichever order they like."""
    base_key = to_base_form(base_word)
    base_counts = collections.Counter(base_key)
    found = []
    for key, display in dictionary.items():
        if display == base_word or not (MIN_SUBWORD_LEN <= len(key) <= len(base_key)):
            continue
        candidate_counts = collections.Counter(key)
        if all(count <= base_counts[letter] for letter, count in candidate_counts.items()):
            found.append(display)
    return sorted(found)


def build_bank(source: Path) -> dict[str, list[str]]:
    dictionary = load_dictionary(source)
    base_candidates = load_base_word_candidates(source)
    print(f"{len(dictionary)} dictionary words, {len(base_candidates)} base-word candidates")

    bank: dict[str, list[str]] = {}
    for base_word in base_candidates:
        subwords = find_subwords(base_word, dictionary)
        if MIN_SUBWORDS_PER_BASE <= len(subwords) <= MAX_SUBWORDS_PER_BASE:
            bank[base_word] = subwords
    return bank


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=None, help="Path to a local kaikki JSONL file")
    args = parser.parse_args()

    source = args.source or CACHE_PATH
    if not source.exists():
        _download(source)

    bank = build_bank(source)
    print(f"{len(bank)} base words with >= {MIN_SUBWORDS_PER_BASE} sub-words")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
