"""
Polish currency expander for TTS preprocessing.

Converts currency patterns to spoken Polish forms:
- "5 zł" → "pięć złotych"
- "3,50 zł" → "trzy złote pięćdziesiąt groszy"
- "100 EUR" → "sto euro"
- "25 $" or "$25" → "dwadzieścia pięć dolarów"
"""

import re
from num2words_pl import number_to_words


def _zloty_form(n: int) -> str:
    """Correct grammatical form of 'złoty' for amount n."""
    if n == 1:
        return "złoty"
    last_two = abs(n) % 100
    last_one = abs(n) % 10
    if 10 <= last_two <= 20:
        return "złotych"
    if 2 <= last_one <= 4:
        return "złote"
    return "złotych"


def _grosz_form(n: int) -> str:
    """Correct grammatical form of 'grosz' for amount n."""
    if n == 1:
        return "grosz"
    last_two = abs(n) % 100
    last_one = abs(n) % 10
    if 10 <= last_two <= 20:
        return "groszy"
    if 2 <= last_one <= 4:
        return "grosze"
    return "groszy"


def _generic_currency_form(n: int, one: str, few: str, many: str) -> str:
    """Pick Polish plural form for a generic currency."""
    if n == 1:
        return one
    last_two = abs(n) % 100
    last_one = abs(n) % 10
    if 10 <= last_two <= 20:
        return many
    if 2 <= last_one <= 4:
        return few
    return many


# Currency definitions: symbol/code → (singular, paucal 2-4, plural 5+, subunit_singular, sub_paucal, sub_plural)
# None for subunit means don't break into subunits
CURRENCIES = {
    "zł": ("złoty", "złote", "złotych", "grosz", "grosze", "groszy"),
    "pln": ("złoty", "złote", "złotych", "grosz", "grosze", "groszy"),
    "eur": ("euro", "euro", "euro", "cent", "centy", "centów"),
    "€": ("euro", "euro", "euro", "cent", "centy", "centów"),
    "usd": ("dolar", "dolary", "dolarów", "cent", "centy", "centów"),
    "$": ("dolar", "dolary", "dolarów", "cent", "centy", "centów"),
    "gbp": ("funt", "funty", "funtów", "pens", "pensy", "pensów"),
    "£": ("funt", "funty", "funtów", "pens", "pensy", "pensów"),
    "chf": ("frank", "franki", "franków", None, None, None),
    "czk": ("korona", "korony", "koron", None, None, None),
}

# Pattern: number + currency symbol/code, or symbol + number
# Supports: "5 zł", "5,50 zł", "5.50 EUR", "$25", "€100"
_CURRENCY_AFTER = re.compile(
    r'(\d+(?:[.,]\d{1,2})?)\s*'
    r'(zł|PLN|EUR|€|USD|\$|GBP|£|CHF|CZK)(?=\s|[.,;:!?)\]]|$)',
    re.IGNORECASE,
)

_CURRENCY_BEFORE = re.compile(
    r'(\$|€|£)\s*(\d+(?:[.,]\d{1,2})?)',
)


def expand_currencies(text: str) -> str:
    """Expand currency patterns in Polish text to spoken forms."""

    def _expand(amount_str: str, currency_key: str) -> str:
        currency_key = currency_key.lower()
        if currency_key not in CURRENCIES:
            return None

        one, few, many, sub_one, sub_few, sub_many = CURRENCIES[currency_key]

        # Parse amount
        amount_str = amount_str.replace(',', '.')
        if '.' in amount_str:
            parts = amount_str.split('.')
            main = int(parts[0])
            # Pad or truncate to 2 decimal places
            frac_str = (parts[1] + '00')[:2]
            frac = int(frac_str)
        else:
            main = int(amount_str)
            frac = 0

        result_parts = []

        if main > 0 or frac == 0:
            main_word = number_to_words(main)
            main_form = _generic_currency_form(main, one, few, many)
            result_parts.append(f"{main_word} {main_form}")

        if frac > 0 and sub_one is not None:
            frac_word = number_to_words(frac)
            frac_form = _generic_currency_form(frac, sub_one, sub_few, sub_many)
            result_parts.append(f"{frac_word} {frac_form}")

        return " ".join(result_parts)

    # Replace symbol-before-number patterns first ($25, €100)
    def _repl_before(m: re.Match) -> str:
        symbol = m.group(1)
        amount = m.group(2)
        result = _expand(amount, symbol)
        return result if result else m.group(0)

    text = _CURRENCY_BEFORE.sub(_repl_before, text)

    # Replace number-before-symbol patterns (5 zł, 100 EUR)
    def _repl_after(m: re.Match) -> str:
        amount = m.group(1)
        symbol = m.group(2)
        result = _expand(amount, symbol)
        return result if result else m.group(0)

    text = _CURRENCY_AFTER.sub(_repl_after, text)

    return text


if __name__ == "__main__":
    examples = [
        "Cena: 5 zł",
        "Kosztuje 3,50 zł za sztukę.",
        "Zarobił 1000 EUR w tym miesiącu.",
        "To tylko $25.",
        "Bilet za 100 GBP jest drogi.",
        "Rata wynosi 2500,99 PLN.",
        "1 zł to 100 groszy.",
        "Kurs: 4,50 zł za 1 EUR.",
        "€100 za noc.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {expand_currencies(ex)}")
        print()
