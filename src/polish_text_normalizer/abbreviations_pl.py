"""
Polish abbreviation expander for TTS preprocessing.

Expands common Polish abbreviations to their full forms so TTS models
pronounce them correctly instead of spelling them out.

Handles:
- Abbreviations with and without dots (dr, dr., m.in., np.)
- Case preservation (Dr → Doktor, dr → doktor)
- Context-aware expansion (dr + capitalized word → title usage)
- Day-of-week abbreviations
- Academic titles, military ranks, street types, common phrases
"""

import re

# Abbreviations → full form (lowercase)
# Organized by category for maintainability
ABBREVIATIONS: dict[str, str] = {
    # Academic & professional titles
    "dr": "doktor",
    "prof": "profesor",
    "mgr": "magister",
    "inż": "inżynier",
    "doc": "docent",
    "hab": "habilitowany",
    "lic": "licencjat",
    "dyr": "dyrektor",
    "red": "redaktor",
    "mec": "mecenas",

    # Military / uniformed ranks
    "gen": "generał",
    "płk": "pułkownik",
    "mjr": "major",
    "kpt": "kapitan",
    "por": "porucznik",
    "ppor": "podporucznik",
    "sierż": "sierżant",
    "szer": "szeregowy",
    "kom": "komisarz",

    # Address / location
    "ul": "ulica",
    "al": "aleja",
    "pl": "plac",
    "os": "osiedle",
    "woj": "województwo",
    "pow": "powiat",
    "gm": "gmina",

    # Common phrases
    "np": "na przykład",
    "m.in": "między innymi",
    "tj": "to jest",
    "tzn": "to znaczy",
    "itp": "i tym podobne",
    "itd": "i tak dalej",
    "wg": "według",
    "ok": "około",
    "tzw": "tak zwany",
    "ds": "do spraw",
    "ws": "w sprawie",
    "jw": "jak wyżej",
    "cd": "ciąg dalszy",
    "cdn": "ciąg dalszy nastąpi",
    "ps": "post scriptum",
    "br": "bieżącego roku",
    "ub": "ubiegłego",
    "b.r": "bieżącego roku",

    # Units / measures
    "godz": "godzina",
    "tel": "telefon",
    "nr": "numer",
    "pkt": "punkt",
    "str": "strona",
    "tys": "tysięcy",
    "mln": "milionów",
    "mld": "miliardów",
    # "zł" and "gr" handled by currency_pl.py with proper grammar
    # (złoty/złote/złotych depending on amount)

    # Religious / honorific
    "św": "święty",
    "bł": "błogosławiony",
    "ks": "ksiądz",
    "bp": "biskup",
    "abp": "arcybiskup",
    "o": None,  # skip — too ambiguous as single letter

    # Days of the week
    "pn": "poniedziałek",
    "wt": "wtorek",
    "śr": "środa",
    "czw": "czwartek",
    "pt": "piątek",
    "sb": "sobota",
    "nd": "niedziela",
    "pon": "poniedziałek",
    "sob": "sobota",
    "niedz": "niedziela",

    # Months (abbreviated)
    "sty": "stycznia",
    "lut": "lutego",
    "mar": "marca",
    "kwi": "kwietnia",
    "maj": "maja",
    "cze": "czerwca",
    "lip": "lipca",
    "sie": "sierpnia",
    "wrz": "września",
    "paź": "października",
    "lis": "listopada",
    "gru": "grudnia",

    # Misc
    "wyd": "wydanie",
    "przyp": "przypis",
    "ang": "angielski",
    "pol": "polski",
    "fr": "francuski",
    "niem": "niemiecki",
    "łac": "łaciński",
    "im": "imienia",
}

# Remove None entries (explicitly skipped)
ABBREVIATIONS = {k: v for k, v in ABBREVIATIONS.items() if v is not None}

# Compound abbreviations that contain dots internally (must match as-is)
# These are checked first before the dot-stripping logic
COMPOUND_ABBREVS: dict[str, str] = {
    "m.in": "między innymi",
    "b.r": "bieżącego roku",
    "dr hab": "doktor habilitowany",
}


def _match_case(original: str, replacement: str) -> str:
    """Match the case pattern of original to replacement."""
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement



def expand_abbreviations(text: str) -> str:
    """Expand Polish abbreviations in text to full forms.
    
    Processing order:
    1. Compound abbreviations (m.in., b.r., dr hab.)
    2. Single abbreviations with optional trailing dot
    
    Case is preserved: Dr → Doktor, DR → DOKTOR, dr → doktor.
    """
    # Step 1: Compound abbreviations
    for abbr, full in COMPOUND_ABBREVS.items():
        # Match with optional trailing dot, case-insensitive
        pattern = re.compile(
            r'\b' + re.escape(abbr) + r'\.?' + r'(?=\s|$|[,;:!?)])',
            re.IGNORECASE,
        )
        def _compound_repl(m, full=full):
            return _match_case(m.group(0), full)
        text = pattern.sub(_compound_repl, text)

    # Step 2: Single abbreviations
    # Build pattern from all keys, sorted longest-first to avoid partial matches
    abbr_keys = sorted(ABBREVIATIONS.keys(), key=len, reverse=True)
    # Escape special regex chars in abbreviation keys
    escaped = [re.escape(k) for k in abbr_keys]
    # Pattern: word boundary + abbreviation + optional dot + boundary
    # The dot is optional because some abbreviations appear with or without it
    pattern = re.compile(
        r'(?<!\w)(' + '|'.join(escaped) + r')\.?(?=\s|$|[,;:!?)\]\-])',
        re.IGNORECASE,
    )

    def _replace(m: re.Match) -> str:
        matched = m.group(0)
        # Strip trailing dot to look up the key
        key = matched.rstrip('.').lower()
        if key not in ABBREVIATIONS:
            return matched
        full = ABBREVIATIONS[key]
        return _match_case(matched.rstrip('.'), full)

    text = pattern.sub(_replace, text)

    return text


if __name__ == "__main__":
    # Quick demo
    examples = [
        "Dr Kowalski przyjmuje w godz. 8-16.",
        "Mieszka na ul. Marszałkowskiej, al. Jerozolimskie.",
        "Np. można to zrobić, m.in. tak.",
        "Prof. Nowak, mgr inż. Wiśniewski",
        "Spotkanie w pn. o godz. 10, tj. rano.",
        "Gen. Anders, płk. Stauffenberg",
        "Kościół św. Anny",
        "Ok. 50 tys. osób, tj. ok. 3 mln zł.",
        "Itp., itd., tzn. wszystko.",
    ]
    for ex in examples:
        print(f"  IN: {ex}")
        print(f" OUT: {expand_abbreviations(ex)}")
        print()
