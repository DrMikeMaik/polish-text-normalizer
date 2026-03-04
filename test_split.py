"""Tests for _split_text — no model loading required."""
from polish_tts import _split_text


def test_preserves_punctuation():
    chunks = _split_text("Cześć! Jak się masz? Dobrze.")
    assert chunks == ["Cześć!", "Jak się masz?", "Dobrze."]


def test_preserves_trailing_punctuation():
    chunks = _split_text("Jedno zdanie.")
    assert chunks == ["Jedno zdanie."]


def test_long_text_splits_at_comma():
    long = "To jest bardzo długie zdanie, które ma więcej niż sto pięćdziesiąt znaków i powinno być podzielone na mniejsze części, żeby syntezator mógł je przetworzyć poprawnie i bez problemów."
    chunks = _split_text(long)
    for c in chunks:
        assert len(c) <= 150, f"Chunk too long ({len(c)}): {c}"


def test_empty():
    assert _split_text("") == []
    assert _split_text("   ") == []


def test_newlines_split():
    chunks = _split_text("Linia pierwsza\nLinia druga\nLinia trzecia")
    assert len(chunks) == 3


if __name__ == "__main__":
    test_preserves_punctuation()
    test_preserves_trailing_punctuation()
    test_long_text_splits_at_comma()
    test_empty()
    test_newlines_split()
    print("All tests passed!")
