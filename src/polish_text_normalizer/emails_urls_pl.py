"""
Polish email and URL expander for TTS preprocessing.

Converts email addresses and URLs to spoken Polish:
- jan@example.com → "jan małpa example kropka com"
- https://www.example.com/page → "example kropka com ukośnik page"
- user@mail.pl → "user małpa mail kropka pl"

Symbols:
- @ → małpa
- . → kropka
- / → ukośnik
- : → dwukropek
- - → myślnik
- _ → podkreślnik
- # → hasz
- ? → znak zapytania
- = → równa się
- & → i (ampersand)
- % → procent
- ~ → tylda
- + → plus
"""

import re

# Module-level storage for placeholder ↔ expansion mappings
_placeholder_list: list[tuple[str, str]] = []


def _make_placeholder(expansion: str) -> str:
    """Create a unique placeholder token and store the expansion."""
    # Use \x00 delimiters + letter-only index so no downstream regex
    # matches digits or word characters in the token
    idx = len(_placeholder_list)
    # Encode index as lowercase letters: 0→a, 1→b, ..., 25→z, 26→ba, etc.
    letters = []
    n = idx
    while True:
        letters.append(chr(ord('a') + n % 26))
        n //= 26
        if n == 0:
            break
    tag = ''.join(reversed(letters))
    token = f"\x00\x01EURL{tag}\x01\x00"
    _placeholder_list.append((token, expansion))
    return token


def restore_placeholders(text: str) -> str:
    """Replace all placeholder tokens with their spoken expansions."""
    for token, expansion in _placeholder_list:
        text = text.replace(token, expansion)
    _placeholder_list.clear()
    return text


def _expand_symbols_in_segment(segment: str) -> str:
    """Expand symbols (hyphens, underscores, etc.) within a domain/path segment."""
    result = []
    for char in segment:
        if char in SYMBOL_MAP:
            result.append(SYMBOL_MAP[char])
        else:
            result.append(char)
    text = "".join(result)
    return re.sub(r"\s+", " ", text).strip()


def _read_domain_part(domain: str) -> str:
    """Convert domain like 'www.example.com' to spoken form."""
    # Strip www. prefix — it's noise in speech
    if domain.lower().startswith("www."):
        domain = domain[4:]
    
    parts = domain.split(".")
    spoken_parts = [_expand_symbols_in_segment(p) for p in parts]
    return " kropka ".join(spoken_parts)


SYMBOL_MAP = {
    "@": " małpa ",
    "/": " ukośnik ",
    ":": " dwukropek ",
    "-": " myślnik ",
    "_": " podkreślnik ",
    "#": " hasz ",
    "?": " znak zapytania ",
    "=": " równa się ",
    "&": " i ",
    "%": " procent ",
    "~": " tylda ",
    "+": " plus ",
}


def _read_path_part(path: str) -> str:
    """Convert URL path/query to spoken form, symbol by symbol."""
    if not path:
        return ""
    
    result = []
    for char in path:
        if char == ".":
            result.append(" kropka ")
        elif char in SYMBOL_MAP:
            result.append(SYMBOL_MAP[char])
        else:
            result.append(char)
    
    # Clean up multiple spaces
    text = "".join(result)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Email pattern: word-like chars, dots, hyphens, pluses before @, domain after
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)

# URL pattern: optional scheme, domain, optional path
URL_RE = re.compile(
    r"https?://[^\s<>\"\')]+|www\.[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}[^\s<>\"\')]*",
)


def _expand_email_to_spoken(email: str) -> str:
    """Convert an email address to spoken Polish."""
    local, domain = email.rsplit("@", 1)
    local_spoken = _read_path_part(local)
    domain_spoken = _read_domain_part(domain)
    return f"{local_spoken} małpa {domain_spoken}"


def _expand_url_to_spoken(url: str) -> str:
    """Convert a URL to spoken Polish (without trailing punctuation)."""
    # Remove scheme
    display = re.sub(r"^https?://", "", url)

    # Split domain from path
    slash_idx = display.find("/")
    if slash_idx == -1:
        domain = display
        path = ""
    else:
        domain = display[:slash_idx]
        path = display[slash_idx:]  # includes leading /

    domain_spoken = _read_domain_part(domain)

    if path and path != "/":
        path_spoken = _read_path_part(path[1:])
        return f"{domain_spoken} ukośnik {path_spoken}"
    return domain_spoken


def _placeholder_email(match: re.Match) -> str:
    """Replace email with placeholder, store spoken form."""
    return _make_placeholder(_expand_email_to_spoken(match.group(0)))


def _placeholder_url(match: re.Match) -> str:
    """Replace URL with placeholder, store spoken form."""
    url = match.group(0)
    # Strip trailing punctuation that got captured
    trailing = ""
    while url and url[-1] in ".,;:!?)":
        trailing = url[-1] + trailing
        url = url[:-1]
    return _make_placeholder(_expand_url_to_spoken(url)) + trailing


def expand_emails_urls(text: str) -> str:
    """Replace email addresses and URLs with placeholders.

    The actual spoken expansions are stored internally and restored later
    by calling ``restore_placeholders()`` after all other normalizers run.
    This prevents downstream steps (e.g. abbreviation expander) from
    mangling parts of the expanded email/URL text.
    """
    # Emails first
    text = EMAIL_RE.sub(_placeholder_email, text)
    # Then URLs
    text = URL_RE.sub(_placeholder_url, text)
    return text
