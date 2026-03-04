"""Tests for special_chars_pl.py"""
import pytest
from special_chars_pl import expand_special_chars


class TestDegrees:
    def test_degrees_plain(self):
        assert expand_special_chars("20°") == "20 stopni"

    def test_degrees_celsius(self):
        assert expand_special_chars("36°C") == "36 stopni Celsjusza"

    def test_degrees_fahrenheit(self):
        assert expand_special_chars("98°F") == "98 stopni Fahrenheita"

    def test_degrees_in_sentence(self):
        assert expand_special_chars("Temperatura: 20°C w cieniu") == "Temperatura: 20 stopni Celsjusza w cieniu"

    def test_negative_degrees(self):
        assert expand_special_chars("-5°C") == "-5 stopni Celsjusza"


class TestSection:
    def test_section_with_space(self):
        assert expand_special_chars("§ 5") == "paragraf 5"

    def test_section_no_space(self):
        assert expand_special_chars("§5") == "paragraf 5"

    def test_section_in_sentence(self):
        assert expand_special_chars("Zgodnie z § 12 regulaminu") == "Zgodnie z paragraf 12 regulaminu"


class TestMathOperators:
    def test_addition(self):
        assert expand_special_chars("2+3") == "2 plus 3"

    def test_equals_between_chars(self):
        assert expand_special_chars("x=5") == "x równa się 5"

    def test_full_expression(self):
        result = expand_special_chars("2+3=5")
        assert "plus" in result
        assert "równa się" in result

    def test_multiply(self):
        assert "razy" in expand_special_chars("3×4")

    def test_divide(self):
        assert "dzielone przez" in expand_special_chars("10÷2")

    def test_not_equal(self):
        assert "nie równa się" in expand_special_chars("a≠b")

    def test_approximately(self):
        assert "w przybliżeniu" in expand_special_chars("π≈3.14")

    def test_plus_minus(self):
        assert "plus minus" in expand_special_chars("±5")

    def test_less_equal(self):
        assert "mniejsze lub równe" in expand_special_chars("x≤10")

    def test_greater_equal(self):
        assert "większe lub równe" in expand_special_chars("x≥0")

    def test_less_than(self):
        assert "mniejsze niż" in expand_special_chars("a<b")

    def test_greater_than(self):
        assert "większe niż" in expand_special_chars("a>b")

    def test_infinity(self):
        assert "nieskończoność" in expand_special_chars("∞")


class TestArrows:
    def test_right_arrow(self):
        assert "strzałka w prawo" in expand_special_chars("A → B")

    def test_left_arrow(self):
        assert "strzałka w lewo" in expand_special_chars("B ← A")

    def test_up_arrow(self):
        assert "strzałka w górę" in expand_special_chars("↑")

    def test_down_arrow(self):
        assert "strzałka w dół" in expand_special_chars("↓")

    def test_implies(self):
        assert "wynika" in expand_special_chars("A ⇒ B")


class TestCommonSymbols:
    def test_ampersand(self):
        assert expand_special_chars("rock & roll") == "rock i roll"

    def test_copyright(self):
        assert "prawa autorskie" in expand_special_chars("© 2026")

    def test_registered(self):
        assert "znak zastrzeżony" in expand_special_chars("OpenClaw®")

    def test_trademark(self):
        assert "znak towarowy" in expand_special_chars("Brand™")

    def test_per_mille(self):
        assert "promil" in expand_special_chars("2‰")


class TestBrackets:
    def test_parentheses_removed(self):
        result = expand_special_chars("tekst (w nawiasie) dalej")
        assert "(" not in result
        assert ")" not in result
        assert "tekst" in result
        assert "w nawiasie" in result
        assert "dalej" in result

    def test_square_brackets_removed(self):
        result = expand_special_chars("[przypis]")
        assert "[" not in result
        assert "]" not in result
        assert "przypis" in result

    def test_curly_brackets_removed(self):
        result = expand_special_chars("{kod}")
        assert "{" not in result
        assert "}" not in result
        assert "kod" in result


class TestStandaloneSymbols:
    def test_asterisk(self):
        assert "gwiazdka" in expand_special_chars("patrz * poniżej")

    def test_hash(self):
        assert "hasz" in expand_special_chars("naciśnij # aby")

    def test_tilde(self):
        assert "tylda" in expand_special_chars("około ~ sto")

    def test_pipe(self):
        assert "kreska pionowa" in expand_special_chars("A | B")

    def test_backslash(self):
        assert "ukośnik odwrotny" in expand_special_chars("C \\ D")


class TestEllipsis:
    def test_ellipsis_removed(self):
        result = expand_special_chars("hmm… no tak")
        assert "…" not in result
        assert "hmm" in result
        assert "no tak" in result


class TestDashes:
    def test_em_dash_pause(self):
        result = expand_special_chars("słowo — drugie słowo")
        assert "—" not in result
        assert "słowo" in result
        assert "drugie słowo" in result

    def test_em_dash_no_spaces(self):
        result = expand_special_chars("tak—nie")
        assert "—" not in result

    def test_en_dash_numeric_range(self):
        # en-dash between numbers → "do"
        result = expand_special_chars("2020–2025")
        assert "do" in result
        assert "–" not in result

    def test_en_dash_non_numeric(self):
        # en-dash between words → pause (comma)
        result = expand_special_chars("Warszawa–Kraków")
        # Should not contain "–"
        assert "–" not in result


class TestQuotationMarks:
    def test_polish_quotes(self):
        result = expand_special_chars('Powiedział \u201etak\u201d i poszedł')
        assert '\u201e' not in result
        assert '\u201d' not in result
        assert 'tak' in result

    def test_guillemets(self):
        result = expand_special_chars("«cytat»")
        assert "«" not in result
        assert "»" not in result
        assert "cytat" in result

    def test_english_quotes(self):
        result = expand_special_chars('"hello"')
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "hello" in result

    def test_single_quotes(self):
        result = expand_special_chars("it\u2019s")
        assert "\u2019" not in result


class TestFractions:
    def test_half(self):
        assert "jedna druga" in expand_special_chars("½")

    def test_quarter(self):
        assert "jedna czwarta" in expand_special_chars("¼")

    def test_three_quarters(self):
        assert "trzy czwarte" in expand_special_chars("¾")

    def test_third(self):
        assert "jedna trzecia" in expand_special_chars("⅓")

    def test_two_thirds(self):
        assert "dwie trzecie" in expand_special_chars("⅔")

    def test_fraction_in_sentence(self):
        result = expand_special_chars("Dodaj ½ litra wody")
        assert "jedna druga" in result
        assert "litra wody" in result

    def test_fifth(self):
        assert "jedna piąta" in expand_special_chars("⅕")

    def test_seven_eighths(self):
        assert "siedem ósmych" in expand_special_chars("⅞")


class TestEdgeCases:
    def test_empty_string(self):
        assert expand_special_chars("") == ""

    def test_no_special_chars(self):
        assert expand_special_chars("Zwykły tekst po polsku") == "Zwykły tekst po polsku"

    def test_multiple_spaces_cleaned(self):
        result = expand_special_chars("a  +  b")
        assert "  " not in result

    def test_combined(self):
        result = expand_special_chars("Temperatura: 20°C, § 5 mówi że 2+3=5")
        assert "stopni Celsjusza" in result
        assert "paragraf" in result
        assert "plus" in result
        assert "równa się" in result
