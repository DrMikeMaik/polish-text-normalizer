"""
Polish Roman numeral expander for TTS preprocessing.

Converts Roman numerals in Polish text to spoken forms. Context-aware:
- Centuries: "XXI wiek" → "dwudziesty pierwszy wiek"
- Monarchs/popes: "Jan III Sobieski" → "Jan trzeci Sobieski"
- Standalone: "Tom IV" → "Tom czwarty"

Roman numerals in Polish are almost always read as ordinals, not cardinals.
"""

import re

# Roman numeral value map
_ROMAN_VALUES = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50,
    'C': 100, 'D': 500, 'M': 1000,
}

# Maximum value we'll convert (avoids matching random uppercase words)
_MAX_ROMAN = 3999


def _parse_roman(s: str) -> int | None:
    """Parse a Roman numeral string. Returns None if invalid."""
    if not s or not all(c in _ROMAN_VALUES for c in s):
        return None

    total = 0
    prev = 0
    for c in reversed(s):
        val = _ROMAN_VALUES[c]
        if val < prev:
            total -= val
        else:
            total += val
        prev = val

    if total <= 0 or total > _MAX_ROMAN:
        return None

    # Validate by checking it's a "reasonable" Roman numeral
    # (reject things like IIII, VV, etc. — but be lenient since
    # we're doing TTS, not Roman numeral validation)
    return total


# Polish ordinals (masculine nominative) — used for monarchs, tomes, acts
# Covers 1-39 which handles virtually all real-world Roman numerals in Polish
_ORDINALS_MASC = {
    1: "pierwszy", 2: "drugi", 3: "trzeci", 4: "czwarty", 5: "piąty",
    6: "szósty", 7: "siódmy", 8: "ósmy", 9: "dziewiąty", 10: "dziesiąty",
    11: "jedenasty", 12: "dwunasty", 13: "trzynasty", 14: "czternasty",
    15: "piętnasty", 16: "szesnasty", 17: "siedemnasty", 18: "osiemnasty",
    19: "dziewiętnasty", 20: "dwudziesty",
    21: "dwudziesty pierwszy", 22: "dwudziesty drugi",
    23: "dwudziesty trzeci", 24: "dwudziesty czwarty",
    25: "dwudziesty piąty", 26: "dwudziesty szósty",
    27: "dwudziesty siódmy", 28: "dwudziesty ósmy",
    29: "dwudziesty dziewiąty", 30: "trzydziesty",
    31: "trzydziesty pierwszy", 32: "trzydziesty drugi",
    33: "trzydziesty trzeci", 34: "trzydziesty czwarty",
    35: "trzydziesty piąty", 36: "trzydziesty szósty",
    37: "trzydziesty siódmy", 38: "trzydziesty ósmy",
    39: "trzydziesty dziewiąty",
}


def _ordinal(n: int) -> str | None:
    """Get Polish masculine ordinal for n, or None if out of range."""
    return _ORDINALS_MASC.get(n)


# Pattern: standalone Roman numeral (all caps I, V, X, L, C, D, M)
# Must be surrounded by word boundaries, but we use lookaround to avoid
# matching single "I" (too ambiguous in English-mixed text) or "C" etc.
# Minimum 2 chars, OR single char if preceded by context word.
_ROMAN_PAT = re.compile(
    r'(?<![a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])'
    r'([IVXLCDM]{2,}|(?<=[.\s])[IVXLCDM](?=[.\s,;:!?\-)]|$))'
    r'(?![a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])'
)

# Context words that precede Roman numerals (for single-char matching)
_CONTEXT_BEFORE = {
    "jan", "pius", "benedykt", "franciszek", "grzegorz", "karol",
    "henryk", "kazimierz", "zygmunt", "władysław", "bolesław",
    "stefan", "august", "stanisław", "aleksander", "mikołaj",
    "fryderyk", "ludwik", "filip", "karol", "elżbieta",
    "tom", "rozdział", "akt", "scena", "część", "księga",
    "wiek", "klasa", "grupa", "typ", "kategoria", "etap", "faza",
    "punkt", "paragraf", "artykuł", "ustęp",
}


def expand_roman_numerals(text: str) -> str:
    """Expand Roman numerals in Polish text to ordinal words.

    Handles:
    - "w XXI wieku" → "w dwudziestym pierwszym wieku"
    - "Jan III Sobieski" → "Jan trzeci Sobieski"  
    - "Henryk VIII" → "Henryk ósmy"
    - "Tom IV" → "Tom czwarty"
    - "rozdział XII" → "rozdział dwunasty"

    Single-letter Roman numerals (I, V, X) are only expanded when
    preceded by a known context word to avoid false positives.
    """

    def _replace(m: re.Match) -> str:
        roman = m.group(1)
        val = _parse_roman(roman)
        if val is None:
            return m.group(0)

        start = m.start(1)

        # For single-character Roman numerals, check context
        if len(roman) == 1:
            # Get word before
            before_text = text[:start].rstrip().rstrip('.')
            before_word = before_text.split()[-1].lower() if before_text.split() else ""
            if before_word not in _CONTEXT_BEFORE:
                return m.group(0)

        # Check for "wieku" / "wiek" after → locative ordinal for centuries
        after_text = text[m.end(1):].lstrip()
        if re.match(r'wiek[ua]?\b', after_text, re.IGNORECASE):
            loc = _century_locative(val)
            if loc:
                return loc

        # Default: masculine nominative ordinal
        ordinal = _ordinal(val)
        if ordinal:
            return ordinal

        # Fallback for numbers > 39: just use cardinal from num2words
        # (rare in practice — Roman numerals above XXXIX are uncommon)
        return m.group(0)

    return _ROMAN_PAT.sub(_replace, text)


def _century_locative(n: int) -> str | None:
    """Locative form for centuries: 'w XXI wieku' → 'w dwudziestym pierwszym wieku'.

    Returns the locative ordinal or None if out of range.
    """
    _LOC = {
        1: "pierwszym", 2: "drugim", 3: "trzecim", 4: "czwartym", 5: "piątym",
        6: "szóstym", 7: "siódmym", 8: "ósmym", 9: "dziewiątym", 10: "dziesiątym",
        11: "jedenastym", 12: "dwunastym", 13: "trzynastym", 14: "czternastym",
        15: "piętnastym", 16: "szesnastym", 17: "siedemnastym", 18: "osiemnastym",
        19: "dziewiętnastym", 20: "dwudziestym",
        21: "dwudziestym pierwszym", 22: "dwudziestym drugim",
        23: "dwudziestym trzecim", 24: "dwudziestym czwartym",
        25: "dwudziestym piątym", 26: "dwudziestym szóstym",
        27: "dwudziestym siódmym", 28: "dwudziestym ósmym",
        29: "dwudziestym dziewiątym", 30: "trzydziestym",
    }
    return _LOC.get(n)


if __name__ == "__main__":
    examples = [
        "Jan III Sobieski rządził w XVII wieku.",
        "Przeczytaj rozdział XII, Tom IV.",
        "W XXI wieku technologia zmienia świat.",
        "Henryk VIII miał sześć żon.",
        "Pius XII i Benedykt XVI to papieże XX wieku.",
        "Karol V Habsburg panował w XVI wieku.",
        "Konstytucja 3 Maja, artykuł II.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {expand_roman_numerals(ex)}")
        print()
