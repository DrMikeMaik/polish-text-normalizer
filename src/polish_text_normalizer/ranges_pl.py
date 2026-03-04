"""
Polish number range expander for TTS preprocessing.

Converts hyphenated number ranges to spoken Polish:
  8-16       → od osiem do szesnaście  (bare range)
  godz. 8-16 → od ósmej do szesnastej  (hour context)
  str. 5-10  → od pięć do dziesięć     (page context)

Without this, "8-16" becomes "osiemminus szesnaście" — the hyphen
gets read as a minus sign by the number converter.
"""

import re
from .time_pl import HOUR_GENITIVE

# Import num2words for cardinal conversion
from .num2words_pl import number_to_words

# Context words that signal hour ranges (genitive feminine ordinals)
HOUR_CONTEXT = re.compile(
    r'(?:godz\.?|godzina|godziny?|godzin|o|od\s+godz\.?)\s*$',
    re.IGNORECASE,
)

# Context words that signal page ranges
PAGE_CONTEXT = re.compile(
    r'(?:str\.?|stron[aey]?|s\.)\s*$',
    re.IGNORECASE,
)


def _hour_genitive(n: int) -> str:
    """Get genitive feminine ordinal for an hour number."""
    if n in HOUR_GENITIVE:
        return HOUR_GENITIVE[n]
    return number_to_words(n)


def expand_ranges(text: str) -> str:
    """Replace N-M number ranges with spoken Polish.
    
    Context-aware:
    - After hour words (godz., o, godziny): uses feminine genitive ordinals
      "od ósmej do szesnastej"
    - Otherwise: uses cardinals
      "od osiem do szesnaście"
    
    Only matches digit-hyphen-digit patterns where hyphen is flanked by digits,
    to avoid matching negative numbers or compound words.
    """
    def _replace(m: re.Match) -> str:
        prefix = m.group(1) or ""
        a = int(m.group(2))
        b = int(m.group(3))

        # Check if this is really a range (b > a) — otherwise leave it
        # Actually, ranges like 16-8 are unusual but valid (countdown).
        # Let's be permissive and always expand digit-hyphen-digit.

        # Check preceding context for hour words
        text_before = text[:m.start()] + prefix
        if HOUR_CONTEXT.search(text_before):
            a_word = _hour_genitive(a)
            b_word = _hour_genitive(b)
            return f"{prefix}od {a_word} do {b_word}"

        # Default: cardinal range
        a_word = number_to_words(a)
        b_word = number_to_words(b)
        return f"{prefix}od {a_word} do {b_word}"

    # Match: optional whitespace-prefix + digits + hyphen + digits
    # Negative lookbehind for digit/letter to avoid matching inside words
    # The (\s*) captures any space before the first number for context checking
    return re.sub(
        r'(?<![a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\d])(\s*)(\d+)-(\d+)(?!\d)',
        _replace,
        text,
    )
