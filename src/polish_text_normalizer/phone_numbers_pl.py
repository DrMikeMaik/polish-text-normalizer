"""
Polish phone number expander for TTS preprocessing.

Converts phone number patterns to digit-by-digit spoken Polish:
- +48 512 345 678 → "plus czterdzieści osiem, pięć jeden dwa, trzy cztery pięć, sześć siedem osiem"
- 512 345 678 → "pięć jeden dwa, trzy cztery pięć, sześć siedem osiem"
- 512-345-678 → same
- (22) 123 45 67 → "dwadzieścia dwa, jeden dwa trzy, cztery pięć, sześć siedem"
- 112, 997, 998, 999 → read as numbers (emergency)

Digit groups are separated by commas for natural TTS pausing.
"""

import re

DIGIT_WORDS = {
    "0": "zero", "1": "jeden", "2": "dwa", "3": "trzy", "4": "cztery",
    "5": "pięć", "6": "sześć", "7": "siedem", "8": "osiem", "9": "dziewięć",
}

# Country codes: read as a number
COUNTRY_CODE_WORDS = {
    "48": "czterdzieści osiem",
    "1": "jeden",
    "44": "czterdzieści cztery",
    "49": "czterdzieści dziewięć",
    "33": "trzydzieści trzy",
    "39": "trzydzieści dziewięć",
    "34": "trzydzieści cztery",
    "380": "trzysta osiemdziesiąt",
    "420": "czterysta dwadzieścia",
    "421": "czterysta dwadzieścia jeden",
}

# Emergency & short service numbers (read as whole numbers)
from .num2words_pl import number_to_words

EMERGENCY_NUMBERS = {"112", "997", "998", "999", "116000", "116111", "116123"}


def _digits_to_words(digits: str) -> str:
    """Convert a string of digits to space-separated Polish words."""
    return " ".join(DIGIT_WORDS[d] for d in digits if d in DIGIT_WORDS)


def _groups_to_words(groups: list[str]) -> str:
    """Convert digit groups to spoken Polish, comma-separated."""
    spoken = []
    for g in groups:
        words = _digits_to_words(g)
        if words:
            spoken.append(words)
    return ", ".join(spoken)


def expand_phone_numbers(text: str) -> str:
    """Expand phone number patterns in text to spoken Polish."""

    # +CC XXX XXX XXX (country code + 9 digits in groups of 3)
    def _replace_intl_3x3(m: re.Match) -> str:
        cc = m.group(1)
        groups = [m.group(2), m.group(3), m.group(4)]
        cc_word = COUNTRY_CODE_WORDS.get(cc, _digits_to_words(cc))
        return f"plus {cc_word}, {_groups_to_words(groups)}"

    text = re.sub(
        r'\+(\d{1,3})[\s\-](\d{3})[\s\-](\d{3})[\s\-](\d{3})\b',
        _replace_intl_3x3,
        text,
    )

    # +CC XX XXX XX XX (country code + landline format)
    def _replace_intl_land(m: re.Match) -> str:
        cc = m.group(1)
        groups = [m.group(2), m.group(3), m.group(4), m.group(5)]
        cc_word = COUNTRY_CODE_WORDS.get(cc, _digits_to_words(cc))
        return f"plus {cc_word}, {_groups_to_words(groups)}"

    text = re.sub(
        r'\+(\d{1,3})[\s\-](\d{2})[\s\-](\d{3})[\s\-](\d{2})[\s\-](\d{2})\b',
        _replace_intl_land,
        text,
    )

    # (XX) XXX XX XX — landline with area code in parens
    def _replace_landline_parens(m: re.Match) -> str:
        area = m.group(1)
        groups = [area, m.group(2), m.group(3), m.group(4)]
        return _groups_to_words(groups)

    text = re.sub(
        r'\((\d{2})\)\s*(\d{3})[\s\-](\d{2})[\s\-](\d{2})\b',
        _replace_landline_parens,
        text,
    )

    # XXX XXX XXX or XXX-XXX-XXX — 9-digit mobile
    def _replace_mobile(m: re.Match) -> str:
        groups = [m.group(1), m.group(2), m.group(3)]
        return _groups_to_words(groups)

    text = re.sub(
        r'(?<!\d)(\d{3})[\s\-](\d{3})[\s\-](\d{3})(?!\d)',
        _replace_mobile,
        text,
    )

    # XX XXX XX XX — 9-digit landline (area + 7 digits)
    def _replace_landline(m: re.Match) -> str:
        groups = [m.group(1), m.group(2), m.group(3), m.group(4)]
        return _groups_to_words(groups)

    text = re.sub(
        r'(?<!\d)(\d{2})[\s\-](\d{3})[\s\-](\d{2})[\s\-](\d{2})(?!\d)',
        _replace_landline,
        text,
    )

    return text


if __name__ == "__main__":
    examples = [
        "Zadzwoń pod +48 512 345 678.",
        "Numer: 512 345 678",
        "Telefon: 512-345-678",
        "Biuro: (22) 123 45 67",
        "Kontakt: 22 123 45 67",
        "Dzwoń +48 22 567 89 01",
        "Pogotowie: 999, policja: 997, straż: 998.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {expand_phone_numbers(ex)}")
        print()
