"""Tests for Polish phone number expansion."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from polish_text_normalizer.phone_numbers_pl import expand_phone_numbers


class TestMobileNumbers:
    """9-digit mobile numbers in various formats."""

    def test_spaces(self):
        assert expand_phone_numbers("512 345 678") == "pięć jeden dwa, trzy cztery pięć, sześć siedem osiem"

    def test_hyphens(self):
        assert expand_phone_numbers("512-345-678") == "pięć jeden dwa, trzy cztery pięć, sześć siedem osiem"

    def test_in_sentence(self):
        result = expand_phone_numbers("Zadzwoń pod 512 345 678 po 18.")
        assert "pięć jeden dwa" in result
        assert "sześć siedem osiem" in result

    def test_two_numbers(self):
        result = expand_phone_numbers("Tel: 512 345 678 lub 600 100 200")
        assert "pięć jeden dwa" in result
        assert "sześć zero zero" in result


class TestInternational:
    """Numbers with country code."""

    def test_plus48_spaces(self):
        result = expand_phone_numbers("+48 512 345 678")
        assert result.startswith("plus czterdzieści osiem")
        assert "pięć jeden dwa" in result

    def test_plus48_hyphens(self):
        result = expand_phone_numbers("+48-512-345-678")
        assert result.startswith("plus czterdzieści osiem")

    def test_plus44(self):
        result = expand_phone_numbers("+44 789 012 345")
        assert result.startswith("plus czterdzieści cztery")

    def test_plus1(self):
        result = expand_phone_numbers("+1 555 123 456")
        assert result.startswith("plus jeden")


class TestLandline:
    """Landline formats."""

    def test_parens_area_code(self):
        result = expand_phone_numbers("(22) 123 45 67")
        assert "dwa dwa" in result
        assert "jeden dwa trzy" in result
        assert "cztery pięć" in result
        assert "sześć siedem" in result

    def test_parens_no_space(self):
        result = expand_phone_numbers("(22)123 45 67")
        assert "dwa dwa" in result

    def test_area_code_spaces(self):
        result = expand_phone_numbers("22 123 45 67")
        assert "dwa dwa" in result
        assert "sześć siedem" in result

    def test_area_code_hyphens(self):
        result = expand_phone_numbers("22-123-45-67")
        assert "dwa dwa" in result


class TestEdgeCases:
    """Edge cases and non-phone numbers."""

    def test_no_match_short(self):
        """3-digit numbers alone shouldn't be matched."""
        assert expand_phone_numbers("pokój 123") == "pokój 123"

    def test_no_match_random_digits(self):
        """Random digit sequences shouldn't match."""
        assert expand_phone_numbers("kod 12345") == "kod 12345"

    def test_preserves_surrounding_text(self):
        result = expand_phone_numbers("Zadzwoń pod 512 345 678 po 18.")
        assert result.startswith("Zadzwoń pod ")
        assert result.endswith(" po 18.")

    def test_no_match_inside_longer_number(self):
        """Don't match 9 digits that are part of a longer number."""
        text = "1234567890123"
        assert expand_phone_numbers(text) == text

    def test_intl_landline(self):
        result = expand_phone_numbers("+48 22 567 89 01")
        assert "plus czterdzieści osiem" in result
