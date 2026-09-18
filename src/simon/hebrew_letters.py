"""Hebrew final-letter (sofit) form handling.

Five Hebrew letters change shape when they are the last letter of a word:
כ->ך, מ->ם, נ->ן, פ->ף, צ->ץ. A dictionary word spelled with the final form
and a letter tile identified by its non-final form refer to the same
underlying letter -- so every comparison in this app normalizes to the
non-final form first, and the final-form substitution is only ever applied
cosmetically, to the last character, when displaying a finished word.
"""

FINAL_TO_BASE = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}
BASE_TO_FINAL = {base: final for final, base in FINAL_TO_BASE.items()}


def to_base_form(text: str) -> str:
    """Maps every character to its non-final form (no-op for non-sofit
    characters). Use this to build comparison keys."""
    return "".join(FINAL_TO_BASE.get(ch, ch) for ch in text)


def to_display_form(text: str) -> str:
    """Maps only the last character to its final form if applicable,
    leaving the rest of the string untouched. Use this when presenting a
    validated word to the player."""
    if not text:
        return text
    return text[:-1] + BASE_TO_FINAL.get(text[-1], text[-1])
