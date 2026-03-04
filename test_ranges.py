"""Tests for Polish number range expander."""

import pytest
from ranges_pl import expand_ranges


class TestBareRanges:
    def test_simple(self):
        assert expand_ranges("8-16") == "od osiem do szesnaście"

    def test_in_sentence(self):
        result = expand_ranges("Strony 5-10 do przeczytania")
        assert result == "Strony od pięć do dziesięć do przeczytania"

    def test_large_numbers(self):
        result = expand_ranges("100-200")
        assert result == "od sto do dwieście"

    def test_single_digits(self):
        assert expand_ranges("1-3") == "od jeden do trzy"

    def test_preserves_text(self):
        result = expand_ranges("abc 5-10 def")
        assert "od pięć do dziesięć" in result


class TestHourContextRanges:
    def test_godz_dot(self):
        result = expand_ranges("godz. 8-16")
        assert result == "godz. od ósmej do szesnastej"

    def test_godzina_expanded(self):
        """After abbreviation expansion, godz. becomes godzina — should still detect hour context."""
        result = expand_ranges("godzina 8-16")
        assert result == "godzina od ósmej do szesnastej"

    def test_godz_no_dot(self):
        result = expand_ranges("godz 8-16")
        assert result == "godz od ósmej do szesnastej"

    def test_godziny(self):
        result = expand_ranges("godziny 9-17")
        assert result == "godziny od dziewiątej do siedemnastej"

    def test_o_prefix(self):
        # "o" alone before a range — could be hour context
        result = expand_ranges("czynne o 8-16")
        assert "ósmej" in result

    def test_evening_hours(self):
        result = expand_ranges("godz. 18-22")
        assert result == "godz. od osiemnastej do dwudziestej drugiej"


class TestNoFalsePositives:
    def test_negative_number_not_range(self):
        # -5 alone should not be treated as a range (no digit before hyphen)
        result = expand_ranges("temperatura -5")
        assert result == "temperatura -5"

    def test_compound_word_preserved(self):
        # Words with hyphens should not match (letter before/after)
        result = expand_ranges("biało-czerwony")
        assert result == "biało-czerwony"

    def test_phone_number_not_range(self):
        # Digits adjacent to the match boundary
        result = expand_ranges("12-345")
        assert "od dwanaście do trzysta czterdzieści pięć" in result

    def test_single_number(self):
        result = expand_ranges("15")
        assert result == "15"


class TestMultipleRanges:
    def test_two_ranges(self):
        result = expand_ranges("8-16 i 18-22")
        assert "od osiem do szesnaście" in result
        assert "od osiemnaście do dwadzieścia dwa" in result


class TestEdgeCases:
    def test_same_number(self):
        result = expand_ranges("5-5")
        assert result == "od pięć do pięć"

    def test_zero_range(self):
        result = expand_ranges("0-24")
        assert result == "od zero do dwadzieścia cztery"
