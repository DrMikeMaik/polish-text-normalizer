"""
Unified Polish text normalizer for TTS preprocessing.

Chains all text normalization steps in the correct order:
1. Email/URL expansion (jan@x.pl → jan małpa x kropka pl)
2. Abbreviation expansion (dr → doktor, np. → na przykład)
3. Currency expansion (5 zł → pięć złotych)
4. Roman numeral expansion (XXI wiek → dwudziesty pierwszy wiek)
5. Date expansion (27.02.2026 → dwudziestego siódmego lutego...)
6. Time expansion (13:45 → trzynasta czterdzieści pięć)
7. Phone number expansion (512 345 678 → pięć jeden dwa, trzy cztery pięć, ...)
8. Range expansion (8-16 → od osiem do szesnaście)
9. Special character expansion (§ 5 → paragraf 5, 20°C → 20 stopni Celsjusza)
10. Number-to-words conversion (42 → czterdzieści dwa)

This is the single entry point for TTS text preprocessing.
Import `normalize_polish_text` instead of calling individual modules.
"""

import re

from .abbreviations_pl import expand_abbreviations
from .currency_pl import expand_currencies
from .roman_numerals_pl import expand_roman_numerals
from .dates_pl import expand_dates
from .time_pl import expand_times
from .ranges_pl import expand_ranges
from .phone_numbers_pl import expand_phone_numbers
from .emails_urls_pl import expand_emails_urls, restore_placeholders
from .special_chars_pl import expand_special_chars
from .num2words_pl import preprocess_numbers

# Matches space-separated digit groups like "2 500 000" or "12 345"
_GROUPED_NUMBER_RE = re.compile(r'\b(\d{1,3})((?:\s\d{3})+)\b')


def _collapse_grouped_numbers(text: str) -> str:
    """Collapse space-separated digit groups into contiguous numbers.

    "2 500 000" → "2500000", "12 345" → "12345".
    Only collapses when the pattern is unambiguous (1-3 leading digits
    followed by groups of exactly 3 digits separated by single spaces).
    """
    def _join(m: re.Match) -> str:
        return m.group(1) + m.group(2).replace(" ", "")

    return _GROUPED_NUMBER_RE.sub(_join, text)


def normalize_polish_text(text: str) -> str:
    """Normalize Polish text for TTS synthesis.

    Order matters:
    - Phone numbers first (before grouped-number collapsing eats digit groups)
    - Collapse grouped numbers (2 500 000 → 2500000, after phones extracted)
    - Emails/URLs (before dots/symbols get mangled; uses placeholders)
    - Abbreviations (so "ok. 50 zł" becomes "około 50 zł", not mangled)
    - Currencies (so "50 zł" becomes "pięćdziesiąt złotych")
    - Roman numerals (before generic number conversion)
    - Dates (27.02.2026 before dots get mangled)
    - Times (13:45 before the colon gets mangled)
    - Ranges (8-16 before hyphen becomes "minus")
    - Special chars (§, °, math ops, brackets — after structured patterns)
    - Numbers last (catches any remaining digits)
    - Restore email/URL placeholders (swap back spoken forms)
    """
    text = expand_phone_numbers(text)
    text = _collapse_grouped_numbers(text)
    text = expand_emails_urls(text)
    text = expand_abbreviations(text)
    text = expand_currencies(text)
    text = expand_roman_numerals(text)
    text = expand_dates(text)
    text = expand_times(text)
    text = expand_ranges(text)
    text = expand_special_chars(text)
    text = preprocess_numbers(text)
    text = restore_placeholders(text)
    return text


if __name__ == "__main__":
    examples = [
        "Dr Nowak, ul. Długa 15, godz. 8-16.",
        "Ok. 3,5 mln osób, tj. ok. 10% populacji.",
        "Spotkanie w pn. o godz. 10, m.in. z prof. Kowalskim.",
        "Gen. Anders dowodził ok. 50 tys. żołnierzy.",
        "Jan III Sobieski rządził w XVII wieku.",
        "Cena: 5,99 zł za sztukę, tj. ok. $2.",
        "W XXI wieku wydano ok. 100 EUR na osobę.",
        "Pociąg o 13:45, godz. 8-16 czynne.",
        "Spotkanie 14:00-15:30 w sali 5.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {normalize_polish_text(ex)}")
        print()
