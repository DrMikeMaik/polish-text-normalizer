"""Tests for Roman numeral expansion in Polish text."""

import pytest
from roman_numerals_pl import expand_roman_numerals, _parse_roman


class TestParseRoman:
    def test_basic(self):
        assert _parse_roman("I") == 1
        assert _parse_roman("IV") == 4
        assert _parse_roman("IX") == 9
        assert _parse_roman("XIV") == 14
        assert _parse_roman("XXI") == 21
        assert _parse_roman("XLII") == 42
        assert _parse_roman("MCMXCIX") == 1999

    def test_invalid(self):
        assert _parse_roman("") is None
        assert _parse_roman("ABC") is None
        assert _parse_roman("MMMM") is None  # > 3999


class TestMonarchs:
    def test_jan_iii_sobieski(self):
        assert "trzeci" in expand_roman_numerals("Jan III Sobieski")

    def test_henryk_viii(self):
        assert "ósmy" in expand_roman_numerals("Henryk VIII")

    def test_kazimierz_iii_wielki(self):
        result = expand_roman_numerals("Kazimierz III Wielki")
        assert "trzeci" in result

    def test_pius_xii(self):
        assert "dwunasty" in expand_roman_numerals("Pius XII")

    def test_benedykt_xvi(self):
        assert "szesnasty" in expand_roman_numerals("Benedykt XVI")

    def test_karol_v(self):
        result = expand_roman_numerals("Karol V Habsburg")
        assert "piąty" in result


class TestCenturies:
    def test_xxi_wiek(self):
        result = expand_roman_numerals("W XXI wieku")
        assert "dwudziestym pierwszym" in result

    def test_xx_wiek(self):
        result = expand_roman_numerals("XX wiek")
        assert "dwudziesty" in result

    def test_xvii_wieku(self):
        result = expand_roman_numerals("w XVII wieku")
        assert "siedemnastym" in result

    def test_xvi_wiek(self):
        result = expand_roman_numerals("XVI wiek")
        assert "szesnasty" in result


class TestStructural:
    def test_rozdzial(self):
        result = expand_roman_numerals("rozdział XII")
        assert "dwunasty" in result

    def test_tom(self):
        result = expand_roman_numerals("Tom IV")
        assert "czwarty" in result

    def test_multi_roman(self):
        result = expand_roman_numerals("Jan III i Henryk VIII")
        assert "trzeci" in result
        assert "ósmy" in result


class TestNoFalsePositives:
    def test_standalone_i_no_context(self):
        # Standalone "I" without context should NOT be converted
        assert expand_roman_numerals("I went home") == "I went home"

    def test_regular_words_unchanged(self):
        text = "CIVIL DISOBEDIENCE"
        assert expand_roman_numerals(text) == text

    def test_mixed_case_not_roman(self):
        text = "Idę do domu"
        assert expand_roman_numerals(text) == text


class TestMultiCharAlwaysConverts:
    def test_ii(self):
        result = expand_roman_numerals("II")
        assert "drugi" in result

    def test_xiv(self):
        result = expand_roman_numerals("XIV")
        assert "czternasty" in result
