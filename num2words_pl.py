"""
Polish number-to-words converter for TTS preprocessing.

Converts digits in text to their Polish word equivalents so the VITS model
doesn't silently drop them. Handles:
- Cardinals (42 → czterdzieści dwa)
- Ordinals with suffixes (3. → trzeci) — basic, nominative masculine
- Decimals (3.14 → trzy przecinek czternaście)
- Negative numbers (-5 → minus pięć)
- Large numbers up to 10^18
- Year-like numbers (1989 → tysiąc dziewięćset osiemdziesiąt dziewięć)
- Percentages (50% → pięćdziesiąt procent)
"""

import re

ONES = [
    "", "jeden", "dwa", "trzy", "cztery", "pięć",
    "sześć", "siedem", "osiem", "dziewięć",
]

TEENS = [
    "dziesięć", "jedenaście", "dwanaście", "trzynaście", "czternaście",
    "piętnaście", "szesnaście", "siedemnaście", "osiemnaście", "dziewiętnaście",
]

TENS = [
    "", "dziesięć", "dwadzieścia", "trzydzieści", "czterdzieści",
    "pięćdziesiąt", "sześćdziesiąt", "siedemdziesiąt", "osiemdziesiąt",
    "dziewięćdziesiąt",
]

HUNDREDS = [
    "", "sto", "dwieście", "trzysta", "czterysta", "pięćset",
    "sześćset", "siedemset", "osiemset", "dziewięćset",
]

# (singular, paucal 2-4, plural 5+)
SCALE = [
    ("", "", ""),
    ("tysiąc", "tysiące", "tysięcy"),
    ("milion", "miliony", "milionów"),
    ("miliard", "miliardy", "miliardów"),
    ("bilion", "biliony", "bilionów"),
    ("biliard", "biliardy", "biliardów"),
]

# Basic ordinals (nominative masculine) for 1-31 — covers dates and common cases
ORDINALS = {
    1: "pierwszy", 2: "drugi", 3: "trzeci", 4: "czwarty", 5: "piąty",
    6: "szósty", 7: "siódmy", 8: "ósmy", 9: "dziewiąty", 10: "dziesiąty",
    11: "jedenasty", 12: "dwunasty", 13: "trzynasty", 14: "czternasty",
    15: "piętnasty", 16: "szesnasty", 17: "siedemnasty", 18: "osiemnasty",
    19: "dziewiętnasty", 20: "dwudziesty", 21: "dwudziesty pierwszy",
    22: "dwudziesty drugi", 23: "dwudziesty trzeci", 24: "dwudziesty czwarty",
    25: "dwudziesty piąty", 26: "dwudziesty szósty", 27: "dwudziesty siódmy",
    28: "dwudziesty ósmy", 29: "dwudziesty dziewiąty", 30: "trzydziesty",
    31: "trzydziesty pierwszy",
}


def _plural_form(n: int, forms: tuple[str, str, str]) -> str:
    """Pick correct Polish plural form for a number."""
    singular, paucal, plural = forms
    if n == 1:
        return singular
    last_two = n % 100
    last_one = n % 10
    if 10 <= last_two <= 20:
        return plural
    if 2 <= last_one <= 4:
        return paucal
    return plural


def _int_to_words(n: int) -> str:
    """Convert a non-negative integer to Polish words."""
    if n == 0:
        return "zero"

    parts = []
    scale_idx = 0

    while n > 0:
        group = n % 1000
        n //= 1000

        if group > 0 and scale_idx < len(SCALE):
            group_words = _group_to_words(group)
            scale_word = ""
            if scale_idx > 0:
                scale_word = _plural_form(group, SCALE[scale_idx])
                # For "tysiąc" (1000), don't say "jeden tysiąc"
                if group == 1 and scale_idx >= 1:
                    group_words = ""

            chunk = f"{group_words} {scale_word}".strip()
            parts.append(chunk)

        scale_idx += 1

    return " ".join(reversed(parts))


def _group_to_words(n: int) -> str:
    """Convert a number 1-999 to Polish words."""
    if n == 0:
        return ""

    h = n // 100
    rest = n % 100
    t = rest // 10
    o = rest % 10

    parts = []
    if h > 0:
        parts.append(HUNDREDS[h])

    if rest == 0:
        pass
    elif rest < 10:
        parts.append(ONES[rest])
    elif rest < 20:
        parts.append(TEENS[rest - 10])
    else:
        parts.append(TENS[t])
        if o > 0:
            parts.append(ONES[o])

    return " ".join(parts)


def number_to_words(n: int) -> str:
    """Convert an integer (positive, negative, or zero) to Polish words."""
    if n < 0:
        return "minus " + _int_to_words(-n)
    return _int_to_words(n)


def preprocess_numbers(text: str) -> str:
    """Replace numeric tokens in text with Polish words.
    
    Handles: integers, decimals, percentages, ordinals (N.), negative numbers.
    """
    def _replace_match(m: re.Match) -> str:
        full = m.group(0)

        # Percentage: 50%
        if full.endswith('%'):
            num_str = full[:-1].replace(',', '.')
            try:
                val = float(num_str)
                if val == int(val):
                    return number_to_words(int(val)) + " procent"
                else:
                    return _decimal_to_words(num_str) + " procent"
            except ValueError:
                return full

        # Ordinal: 3. (digit(s) followed by period at word boundary or end)
        if re.match(r'^-?\d+\.$', full):
            try:
                n = int(full[:-1])
                if n in ORDINALS:
                    return ORDINALS[n]
                # Fall through to cardinal for numbers outside ordinal range
                return number_to_words(n)
            except ValueError:
                return full

        # Decimal: 3.14 or 3,14
        if '.' in full or ',' in full:
            return _decimal_to_words(full)

        # Plain integer
        try:
            return number_to_words(int(full))
        except ValueError:
            return full

    # Two-pass approach for ordinal vs cardinal disambiguation:
    # Pass 1: Handle genuine ordinals (list items at start of line/sentence)
    # Pass 2: Handle everything else as cardinal
    
    # Ordinal: number+period at START of line (list item pattern like "1. punkt")
    def _replace_ordinal(m: re.Match) -> str:
        n = int(m.group(1))
        if n in ORDINALS:
            return ORDINALS[n]
        return number_to_words(n) + "."
    
    text = re.sub(
        r'(?:^|(?<=\n))(\d+)\.(?=\s)',  # only at line start
        _replace_ordinal,
        text,
    )
    
    # Cardinal pass: all remaining numbers (N. at end → cardinal + period kept)
    def _replace_cardinal(m: re.Match) -> str:
        full = m.group(0)
        
        # Percentage: 50%
        if full.endswith('%'):
            num_str = full[:-1].replace(',', '.')
            try:
                val = float(num_str)
                if val == int(val):
                    return number_to_words(int(val)) + " procent"
                else:
                    return _decimal_to_words(num_str) + " procent"
            except ValueError:
                return full
        
        # Number followed by period (sentence-ending) → cardinal + period
        if re.match(r'^-?\d+\.$', full):
            try:
                n = int(full[:-1])
                return number_to_words(n) + "."
            except ValueError:
                return full
        
        # Decimal: 3.14 or 3,14
        if ',' in full:
            return _decimal_to_words(full)
        if '.' in full:
            return _decimal_to_words(full)
        
        # Plain integer
        try:
            return number_to_words(int(full))
        except ValueError:
            return full
    
    text = re.sub(
        r'\d+\.(?=\s|$)'          # number + period before space/end
        r'|-?\d+(?:[.,]\d+)?%?',  # numbers with optional decimal and %
        _replace_cardinal,
        text,
    )
    return text


def _decimal_to_words(s: str) -> str:
    """Convert a decimal string like '3.14' or '3,14' to Polish words."""
    s = s.replace(',', '.')
    try:
        parts = s.split('.')
        integer_part = number_to_words(int(parts[0]))
        # Fractional part: read as integer (3.14 → "trzy przecinek czternaście")
        frac_str = parts[1]
        frac_int = int(frac_str)
        fractional_part = number_to_words(frac_int)
        return f"{integer_part} przecinek {fractional_part}"
    except (ValueError, IndexError):
        return s
