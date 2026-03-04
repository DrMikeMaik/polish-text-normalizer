"""
Polish date pattern expander for TTS preprocessing.

Converts date patterns to spoken Polish:
- DD.MM.YYYY → "dwudziestego siódmego lutego dwa tysiące dwadzieścia sześć"
- DD.MM → "dwudziestego siódmego lutego"
- DD/MM/YYYY, DD/MM → same as dot format
- YYYY-MM-DD (ISO) → same output
- "27 lutego 2026" → "dwudziestego siódmego lutego dwa tysiące dwadzieścia sześć"
- "27 lutego" → "dwudziestego siódmego lutego"

Days use genitive ordinals, months use genitive names, years use cardinals.
"""

import re
from num2words_pl import number_to_words

# Day ordinals in genitive case (1-31)
DAY_GENITIVE = {
    1: "pierwszego", 2: "drugiego", 3: "trzeciego", 4: "czwartego",
    5: "piątego", 6: "szóstego", 7: "siódmego", 8: "ósmego",
    9: "dziewiątego", 10: "dziesiątego", 11: "jedenastego",
    12: "dwunastego", 13: "trzynastego", 14: "czternastego",
    15: "piętnastego", 16: "szesnastego", 17: "siedemnastego",
    18: "osiemnastego", 19: "dziewiętnastego", 20: "dwudziestego",
    21: "dwudziestego pierwszego", 22: "dwudziestego drugiego",
    23: "dwudziestego trzeciego", 24: "dwudziestego czwartego",
    25: "dwudziestego piątego", 26: "dwudziestego szóstego",
    27: "dwudziestego siódmego", 28: "dwudziestego ósmego",
    29: "dwudziestego dziewiątego", 30: "trzydziestego",
    31: "trzydziestego pierwszego",
}

# Month names in genitive case
MONTHS_GENITIVE = {
    1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
    5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
    9: "września", 10: "października", 11: "listopada", 12: "grudnia",
}

# Month names in nominative (for matching text months)
MONTH_NAME_TO_NUM = {
    "styczeń": 1, "stycznia": 1, "styczniu": 1,
    "luty": 2, "lutego": 2, "lutym": 2,
    "marzec": 3, "marca": 3, "marcu": 3,
    "kwiecień": 4, "kwietnia": 4, "kwietniu": 4,
    "maj": 5, "maja": 5, "maju": 5,
    "czerwiec": 6, "czerwca": 6, "czerwcu": 6,
    "lipiec": 7, "lipca": 7, "lipcu": 7,
    "sierpień": 8, "sierpnia": 8, "sierpniu": 8,
    "wrzesień": 9, "września": 9, "wrześniu": 9,
    "październik": 10, "października": 10, "październiku": 10,
    "listopad": 11, "listopada": 11, "listopadzie": 11,
    "grudzień": 12, "grudnia": 12, "grudniu": 12,
}


def _format_date(day: int, month: int, year: int | None = None) -> str | None:
    """Format a validated date as spoken Polish."""
    if day < 1 or day > 31 or month < 1 or month > 12:
        return None
    
    day_word = DAY_GENITIVE.get(day)
    month_word = MONTHS_GENITIVE.get(month)
    if not day_word or not month_word:
        return None
    
    parts = [day_word, month_word]
    if year is not None:
        parts.append(number_to_words(year))
    
    return " ".join(parts)


def expand_dates(text: str) -> str:
    """Expand date patterns in text to spoken Polish."""
    
    # ISO format: YYYY-MM-DD (4-digit year to avoid false positives)
    def _replace_iso(m: re.Match) -> str:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        result = _format_date(day, month, year)
        return result if result else m.group(0)
    
    text = re.sub(
        r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',
        _replace_iso,
        text,
    )
    
    # DD.MM.YYYY or DD/MM/YYYY (with 4-digit year)
    def _replace_dmy_full(m: re.Match) -> str:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        result = _format_date(day, month, year)
        return result if result else m.group(0)
    
    text = re.sub(
        r'\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b',
        _replace_dmy_full,
        text,
    )
    
    # DD.MM or DD/MM (no year — only when both parts are valid date components)
    def _replace_dmy_short(m: re.Match) -> str:
        day, month = int(m.group(1)), int(m.group(2))
        result = _format_date(day, month)
        return result if result else m.group(0)
    
    text = re.sub(
        r'\b(\d{1,2})[./](\d{1,2})\b(?!\.\d)',  # negative lookahead: not DD.MM.YYYY
        _replace_dmy_short,
        text,
    )
    
    # DD month_name YYYY or DD month_name (text month)
    month_pattern = '|'.join(re.escape(m) for m in sorted(MONTH_NAME_TO_NUM.keys(), key=len, reverse=True))
    
    def _replace_text_date(m: re.Match) -> str:
        day = int(m.group(1))
        month_name = m.group(2).lower()
        year_str = m.group(3)
        
        month = MONTH_NAME_TO_NUM.get(month_name)
        if not month or day < 1 or day > 31:
            return m.group(0)
        
        year = int(year_str) if year_str else None
        result = _format_date(day, month, year)
        return result if result else m.group(0)
    
    text = re.sub(
        rf'\b(\d{{1,2}})\s+({month_pattern})(?:\s+(\d{{4}}))?(?=\b|$)',
        _replace_text_date,
        text,
        flags=re.IGNORECASE,
    )
    
    return text


if __name__ == "__main__":
    examples = [
        "Spotkanie 27.02.2026 o godzinie 10.",
        "Termin: 1.01.2025",
        "Data: 2026-02-28",
        "Wydarzenie 15/06/2024 w Warszawie.",
        "Urodziny 5 marca 2026 roku.",
        "Spotkanie 12 stycznia o 15:00.",
        "Impreza 31.12 w Krakowie.",
        "Święto 25/12 to Boże Narodzenie.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {expand_dates(ex)}")
        print()
