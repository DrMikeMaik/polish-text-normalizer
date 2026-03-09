"""
Special character expander for Polish TTS.

Converts standalone symbols and special characters to their spoken Polish forms.
Handles: math operators, brackets, common symbols, punctuation marks that need
to be vocalized rather than treated as silence.

This runs BEFORE emails/URLs in the pipeline (so we don't mangle @ in emails)
— actually no, it runs AFTER emails/URLs (emails already converted to words),
and AFTER most other steps, but BEFORE final number conversion.

Position in pipeline: after ranges, before numbers.
By this point, emails/URLs/currencies/etc. are already expanded to words,
so we only catch leftover symbols in running text.
"""

import re


# Symbol → spoken Polish form
# Only symbols that make sense to vocalize in TTS context
SYMBOL_MAP = {
    # Math operators
    '+': 'plus',
    '=': 'równa się',
    '≠': 'nie równa się',
    '≈': 'w przybliżeniu',
    '±': 'plus minus',
    '×': 'razy',
    '÷': 'dzielone przez',
    '≤': 'mniejsze lub równe',
    '≥': 'większe lub równe',
    '<': 'mniejsze niż',
    '>': 'większe niż',
    '‰': 'promil',
    '∞': 'nieskończoność',

    # Common symbols
    '§': 'paragraf',
    '©': 'prawa autorskie',
    '®': 'znak zastrzeżony',
    '™': 'znak towarowy',
    '°': 'stopni',
    '…': '',  # ellipsis → just a pause (handled by TTS)
    '&': 'i',
    '*': 'gwiazdka',
    '#': 'hasz',
    '~': 'tylda',
    '^': 'daszek',
    '|': 'kreska pionowa',
    '\\': 'ukośnik odwrotny',

    # Arrows
    '→': 'strzałka w prawo',
    '←': 'strzałka w lewo',
    '↑': 'strzałka w górę',
    '↓': 'strzałka w dół',
    '⇒': 'wynika',
}

# Bracket pairs — expand to opening/closing words
BRACKET_OPEN = {
    '(': '',   # natural pause, TTS handles parentheses as pauses
    '[': '',
    '{': '',
}
BRACKET_CLOSE = {
    ')': '',
    ']': '',
    '}': '',
}


def _expand_math_expression(match: re.Match) -> str:
    """Expand a simple math expression like 2+3=5 or a<b."""
    text = match.group(0)
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in SYMBOL_MAP:
            word = SYMBOL_MAP[ch]
            if word:
                result.append(f' {word} ')
        else:
            result.append(ch)
        i += 1
    return ''.join(result)


def expand_special_chars(text: str) -> str:
    """Expand special characters to spoken Polish forms.
    
    Strategy:
    - Math operators between numbers/words: expand to Polish words
    - Standalone symbols: expand to Polish words
    - Brackets: remove (TTS treats pauses naturally)
    - Ellipsis: remove (TTS pauses at sentence boundaries)
    - Degree symbol: special handling with numbers (20° → dwadzieścia stopni)
    """
    # 1. Handle degree symbol with number: 20° or 20°C
    # Keep the number, replace ° with " stopni", handle C/F suffix
    text = re.sub(
        r'(\d)°C\b',
        r'\1 stopni Celsjusza',
        text,
    )
    text = re.sub(
        r'(\d)°F\b',
        r'\1 stopni Fahrenheita',
        text,
    )
    text = re.sub(
        r'(\d)°(?![CF\w])',
        r'\1 stopni',
        text,
    )

    # 2. Handle standalone percent sign (not preceded by a digit — those are
    #    handled by num2words_pl or ranges_pl)
    text = re.sub(r'(?<!\d)%', 'procent', text)

    # 3. Handle section symbol with number: § 5, §5
    text = re.sub(
        r'§\s*(\d)',
        r'paragraf \1',
        text,
    )

    # 4. Handle math operators between numbers: 2+3, a<b, x=5
    # Expand operators that appear between word chars
    for symbol, word in [
        ('≠', 'nie równa się'),
        ('≈', 'w przybliżeniu'),
        ('±', 'plus minus'),
        ('×', 'razy'),
        ('÷', 'dzielone przez'),
        ('≤', 'mniejsze lub równe'),
        ('≥', 'większe lub równe'),
        ('⇒', 'wynika'),
        ('→', 'strzałka w prawo'),
        ('←', 'strzałka w lewo'),
        ('↑', 'strzałka w górę'),
        ('↓', 'strzałka w dół'),
        ('∞', 'nieskończoność'),
    ]:
        text = text.replace(symbol, f' {word} ')

    # 5. Handle = between word/number chars: x=5, 2+3=5
    text = re.sub(r'(?<=\w)=(?=\w)', ' równa się ', text)
    # Standalone = 
    text = re.sub(r'(?<!\w)=(?!\w)', ' równa się ', text)

    # 6. Handle + between/near numbers: 2+3
    text = re.sub(r'(?<=\d)\+(?=\d)', ' plus ', text)
    # Standalone + (not in phone numbers — those are already expanded)
    text = re.sub(r'(?<![+\w])\+(?!\d{2})', ' plus ', text)

    # 7. Handle < > between word chars  
    text = re.sub(r'(?<=\w)<(?=\w)', ' mniejsze niż ', text)
    text = re.sub(r'(?<=\w)>(?=\w)', ' większe niż ', text)
    # Standalone < >
    text = re.sub(r'(?<!\w)<(?!\w)', ' mniejsze niż ', text)
    text = re.sub(r'(?<!\w)>(?!\w)', ' większe niż ', text)

    # 8. Handle & between words: rock & roll
    text = re.sub(r'\s&\s', ' i ', text)

    # 9. Handle common standalone symbols
    for symbol, word in [
        ('©', 'prawa autorskie'),
        ('®', 'znak zastrzeżony'),
        ('™', 'znak towarowy'),
        ('‰', 'promil'),
    ]:
        text = text.replace(symbol, f' {word} ')

    # 10. Handle dashes — em-dash and en-dash → regular hyphen/pause
    # Em-dash (—) and en-dash (–) used as parenthetical or range separators
    # Replace with comma-pause for natural TTS rhythm
    text = re.sub(r'\s*—\s*', ', ', text)  # em-dash → pause
    text = re.sub(r'(\d)\s*–\s*(\d)', r'\1 do \2', text)  # en-dash between digits → "do" (range: 2020–2025)
    text = re.sub(r'(?<!\d)\s*–\s*(?!\d)', ', ', text)  # en-dash between non-digits → pause

    # 11. Handle quotation marks — strip all variants
    # Polish uses „..." and «...», plus standard "..." and '...'
    for q in ['\u201e', '\u201c', '\u201d', '"', '\u00ab', '\u00bb', '\u2039', '\u203a', '\u2018', '\u2019', '\u201a', '\u201b']:
        text = text.replace(q, ' ')

    # 12. Handle fraction symbols
    fraction_map = {
        '½': 'jedna druga',
        '⅓': 'jedna trzecia',
        '⅔': 'dwie trzecie',
        '¼': 'jedna czwarta',
        '¾': 'trzy czwarte',
        '⅕': 'jedna piąta',
        '⅖': 'dwie piąte',
        '⅗': 'trzy piąte',
        '⅘': 'cztery piąte',
        '⅙': 'jedna szósta',
        '⅚': 'pięć szóstych',
        '⅛': 'jedna ósma',
        '⅜': 'trzy ósme',
        '⅝': 'pięć ósmych',
        '⅞': 'siedem ósmych',
    }
    for symbol, word in fraction_map.items():
        text = text.replace(symbol, f' {word} ')

    # 13. Remove brackets — TTS handles pauses at commas/sentence boundaries
    for bracket in ['(', ')', '[', ']', '{', '}']:
        text = text.replace(bracket, ' ')

    # 14. Handle ellipsis → nothing (TTS pauses naturally)
    text = text.replace('…', ' ')

    # 15. Handle remaining * # ~ ^ | \ only if standalone (not in URLs etc.)
    text = re.sub(r'(?<=\s)\*(?=\s)', ' gwiazdka ', text)
    text = re.sub(r'(?<=\s)#(?=\s)', ' hasz ', text)
    text = re.sub(r'(?<=\s)~(?=\s)', ' tylda ', text)
    text = re.sub(r'(?<=\s)\^(?=\s)', ' daszek ', text)
    text = re.sub(r'(?<=\s)\|(?=\s)', ' kreska pionowa ', text)
    text = re.sub(r'(?<=\s)\\(?=\s)', ' ukośnik odwrotny ', text)

    # 16. Clean up multiple spaces
    text = re.sub(r'  +', ' ', text)
    text = text.strip()

    return text
