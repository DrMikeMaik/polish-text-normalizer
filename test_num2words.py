"""Tests for Polish number-to-words converter."""
from num2words_pl import number_to_words, preprocess_numbers


def test_zero():
    assert number_to_words(0) == "zero"


def test_ones():
    assert number_to_words(1) == "jeden"
    assert number_to_words(5) == "pięć"
    assert number_to_words(9) == "dziewięć"


def test_teens():
    assert number_to_words(10) == "dziesięć"
    assert number_to_words(11) == "jedenaście"
    assert number_to_words(15) == "piętnaście"
    assert number_to_words(19) == "dziewiętnaście"


def test_tens():
    assert number_to_words(20) == "dwadzieścia"
    assert number_to_words(42) == "czterdzieści dwa"
    assert number_to_words(99) == "dziewięćdziesiąt dziewięć"


def test_hundreds():
    assert number_to_words(100) == "sto"
    assert number_to_words(200) == "dwieście"
    assert number_to_words(301) == "trzysta jeden"
    assert number_to_words(999) == "dziewięćset dziewięćdziesiąt dziewięć"


def test_thousands():
    assert number_to_words(1000) == "tysiąc"
    assert number_to_words(2000) == "dwa tysiące"
    assert number_to_words(5000) == "pięć tysięcy"
    assert number_to_words(1989) == "tysiąc dziewięćset osiemdziesiąt dziewięć"
    assert number_to_words(12345) == "dwanaście tysięcy trzysta czterdzieści pięć"


def test_millions():
    assert number_to_words(1000000) == "milion"
    assert number_to_words(2000000) == "dwa miliony"
    assert number_to_words(5000000) == "pięć milionów"


def test_negative():
    assert number_to_words(-7) == "minus siedem"
    assert number_to_words(-1000) == "minus tysiąc"


def test_preprocess_simple():
    assert preprocess_numbers("Mam 3 koty") == "Mam trzy koty"
    assert preprocess_numbers("W roku 1989") == "W roku tysiąc dziewięćset osiemdziesiąt dziewięć"


def test_preprocess_decimal():
    result = preprocess_numbers("Wynik to 3,14 punktu")
    assert "trzy przecinek czternaście" in result


def test_preprocess_percentage():
    result = preprocess_numbers("50% zniżki")
    assert result == "pięćdziesiąt procent zniżki"


def test_preprocess_ordinal():
    # Ordinal only at start of line/string (list item pattern)
    result = preprocess_numbers("3. miejsce")
    assert result == "trzeci miejsce"


def test_ordinal_at_line_start():
    result = preprocess_numbers("1. punkt\n2. punkt\n3. punkt")
    assert "pierwszy" in result
    assert "drugi" in result
    assert "trzeci" in result


def test_cardinal_sentence_ending():
    """Number + period at end of sentence = cardinal, not ordinal."""
    result = preprocess_numbers("Marszałkowska 10.")
    assert result == "Marszałkowska dziesięć."


def test_cardinal_after_nr():
    result = preprocess_numbers("sali nr 3.")
    assert result == "sali nr trzy."


def test_cardinal_mid_sentence():
    """Number + period mid-sentence after text = cardinal."""
    result = preprocess_numbers("pokój 12.")
    assert result == "pokój dwanaście."


def test_preprocess_no_false_positives():
    """Abbreviations with periods should be handled by the sentence splitter, not here."""
    # Numbers in context
    result = preprocess_numbers("Temperatura wynosi -5 stopni")
    assert "minus pięć" in result


def test_preprocess_mixed():
    result = preprocess_numbers("W 2024 roku, 15 osób zdobyło 100% punktów")
    assert "dwa tysiące dwadzieścia cztery" in result
    assert "piętnaście" in result
    assert "sto procent" in result


if __name__ == "__main__":
    test_zero()
    test_ones()
    test_teens()
    test_tens()
    test_hundreds()
    test_thousands()
    test_millions()
    test_negative()
    test_preprocess_simple()
    test_preprocess_decimal()
    test_preprocess_percentage()
    test_preprocess_ordinal()
    test_preprocess_no_false_positives()
    test_preprocess_mixed()
    print("All tests passed!")
