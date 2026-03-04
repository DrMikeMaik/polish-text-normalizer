"""
Polish time pattern expander for TTS preprocessing.

Converts time patterns like 13:45 to spoken Polish:
  13:45 → trzynasta czterdzieści pięć
  8:00  → ósma
  0:30  → zero trzydzieści

Handles 24-hour format (standard in Polish).
"""

import re

# Feminine nominative ordinals for hours (godzina is feminine)
HOUR_NOMINATIVE = {
    0: "zero",
    1: "pierwsza", 2: "druga", 3: "trzecia", 4: "czwarta", 5: "piąta",
    6: "szósta", 7: "siódma", 8: "ósma", 9: "dziewiąta", 10: "dziesiąta",
    11: "jedenasta", 12: "dwunasta", 13: "trzynasta", 14: "czternasta",
    15: "piętnasta", 16: "szesnasta", 17: "siedemnasta", 18: "osiemnasta",
    19: "dziewiętnasta", 20: "dwudziesta", 21: "dwudziesta pierwsza",
    22: "dwudziesta druga", 23: "dwudziesta trzecia", 24: "dwudziesta czwarta",
}

# Feminine genitive ordinals for hours (used with "od ... do ...")
HOUR_GENITIVE = {
    0: "zero",
    1: "pierwszej", 2: "drugiej", 3: "trzeciej", 4: "czwartej", 5: "piątej",
    6: "szóstej", 7: "siódmej", 8: "ósmej", 9: "dziewiątej", 10: "dziesiątej",
    11: "jedenastej", 12: "dwunastej", 13: "trzynastej", 14: "czternastej",
    15: "piętnastej", 16: "szesnastej", 17: "siedemnastej", 18: "osiemnastej",
    19: "dziewiętnastej", 20: "dwudziestej", 21: "dwudziestej pierwszej",
    22: "dwudziestej drugiej", 23: "dwudziestej trzeciej", 24: "dwudziestej czwartej",
}

# Cardinal words for minutes (reuse from num2words logic but inline for independence)
_ONES = ["", "jeden", "dwa", "trzy", "cztery", "pięć",
         "sześć", "siedem", "osiem", "dziewięć"]
_TEENS = ["dziesięć", "jedenaście", "dwanaście", "trzynaście", "czternaście",
          "piętnaście", "szesnaście", "siedemnaście", "osiemnaście", "dziewiętnaście"]
_TENS = ["", "dziesięć", "dwadzieścia", "trzydzieści", "czterdzieści",
         "pięćdziesiąt"]


def _minutes_to_words(m: int) -> str:
    """Convert minutes (0-59) to Polish cardinal words."""
    if m == 0:
        return ""
    if m < 10:
        return _ONES[m]
    if m < 20:
        return _TEENS[m - 10]
    t, o = divmod(m, 10)
    if o == 0:
        return _TENS[t]
    return f"{_TENS[t]} {_ONES[o]}"


def time_to_words(hour: int, minute: int) -> str:
    """Convert hour:minute to spoken Polish.
    
    Examples:
        (13, 45) → "trzynasta czterdzieści pięć"
        (8, 0)   → "ósma"
        (0, 30)  → "zero trzydzieści"
    """
    h_word = HOUR_NOMINATIVE.get(hour, str(hour))
    if minute == 0:
        return h_word
    m_word = _minutes_to_words(minute)
    return f"{h_word} {m_word}"


def time_range_to_words(h1: int, m1: int, h2: int, m2: int) -> str:
    """Convert a time range to spoken Polish with genitive forms.
    
    Example: (14,0, 15,30) → "od czternastej do piętnastej trzydzieści"
    """
    g1 = HOUR_GENITIVE.get(h1, str(h1))
    g2 = HOUR_GENITIVE.get(h2, str(h2))
    if m1 == 0:
        start = g1
    else:
        start = f"{g1} {_minutes_to_words(m1)}"
    if m2 == 0:
        end = g2
    else:
        end = f"{g2} {_minutes_to_words(m2)}"
    return f"od {start} do {end}"


def _valid_time(h: int, m: int) -> bool:
    if h > 24 or m > 59:
        return False
    if h == 24 and m > 0:
        return False
    return True


def expand_times(text: str) -> str:
    """Replace time patterns in text with Polish words.
    
    Handles:
    - Time ranges: 14:00-15:30 → od czternastej do piętnastej trzydzieści
    - Single times: 13:45 → trzynasta czterdzieści pięć
    """
    # First: time ranges (HH:MM-HH:MM)
    def _replace_range(m: re.Match) -> str:
        h1, m1, h2, m2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        if not _valid_time(h1, m1) or not _valid_time(h2, m2):
            return m.group(0)
        return time_range_to_words(h1, m1, h2, m2)

    text = re.sub(
        r'(?<!\d)(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})(?!\d)',
        _replace_range, text,
    )

    # Then: single times (HH:MM)
    def _replace(m: re.Match) -> str:
        hour = int(m.group(1))
        minute = int(m.group(2))
        if not _valid_time(hour, minute):
            return m.group(0)
        return time_to_words(hour, minute)

    return re.sub(r'(?<!\d)(\d{1,2}):(\d{2})(?!\d)', _replace, text)
