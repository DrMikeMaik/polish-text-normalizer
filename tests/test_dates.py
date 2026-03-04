"""Tests for Polish date pattern expander."""

import pytest
from polish_text_normalizer.dates_pl import expand_dates


class TestDotFormat:
    """DD.MM.YYYY and DD.MM formats."""

    def test_full_date(self):
        assert "dwudziestego siódmego lutego dwa tysiące dwadzieścia sześć" in expand_dates("27.02.2026")

    def test_single_digit_day_month(self):
        assert "pierwszego stycznia" in expand_dates("1.1.2025")

    def test_padded_date(self):
        assert "piątego marca" in expand_dates("05.03.2024")

    def test_short_date_no_year(self):
        assert expand_dates("31.12") == "trzydziestego pierwszego grudnia"

    def test_new_years(self):
        assert "pierwszego stycznia dwa tysiące dwadzieścia pięć" in expand_dates("01.01.2025")

    def test_preserves_surrounding_text(self):
        result = expand_dates("Spotkanie 15.06.2024 w Warszawie.")
        assert "piętnastego czerwca" in result
        assert "Spotkanie" in result
        assert "w Warszawie." in result


class TestSlashFormat:
    """DD/MM/YYYY and DD/MM formats."""

    def test_full_date(self):
        assert "dwudziestego piątego grudnia" in expand_dates("25/12/2024")

    def test_short_date(self):
        assert expand_dates("25/12") == "dwudziestego piątego grudnia"


class TestISOFormat:
    """YYYY-MM-DD format."""

    def test_iso_date(self):
        result = expand_dates("2026-02-28")
        assert "dwudziestego ósmego lutego" in result
        assert "dwa tysiące dwadzieścia sześć" in result

    def test_iso_single_digit(self):
        result = expand_dates("2025-1-5")
        assert "piątego stycznia" in result


class TestTextMonth:
    """DD month_name YYYY formats."""

    def test_with_year(self):
        result = expand_dates("5 marca 2026")
        assert "piątego marca dwa tysiące dwadzieścia sześć" in result

    def test_without_year(self):
        result = expand_dates("12 stycznia")
        assert "dwunastego stycznia" in result

    def test_genitive_month(self):
        result = expand_dates("1 lutego 2025")
        assert "pierwszego lutego" in result

    def test_nominative_month(self):
        result = expand_dates("15 czerwiec 2024")
        assert "piętnastego czerwca" in result

    def test_locative_month(self):
        result = expand_dates("20 styczniu 2025")
        assert "dwudziestego stycznia" in result

    def test_preserves_context(self):
        result = expand_dates("Urodziny 5 marca 2026 roku.")
        assert "piątego marca" in result
        assert "roku." in result


class TestEdgeCases:
    """Edge cases and non-dates."""

    def test_invalid_month_13(self):
        assert expand_dates("15.13.2024") == "15.13.2024"

    def test_invalid_day_32(self):
        assert expand_dates("32.01.2024") == "32.01.2024"

    def test_invalid_month_0(self):
        assert expand_dates("15.0.2024") == "15.0.2024"

    def test_does_not_match_time(self):
        # 13:45 should NOT be treated as a date
        assert expand_dates("13:45") == "13:45"

    def test_does_not_match_decimal(self):
        # 3.14 could match DD.MM but 14 > 12, so it won't
        assert expand_dates("3.14") == "3.14"

    def test_multiple_dates(self):
        result = expand_dates("Od 1.01.2025 do 31.12.2025")
        assert "pierwszego stycznia" in result
        assert "trzydziestego pierwszego grudnia" in result

    def test_no_dates(self):
        text = "Zwykły tekst bez dat."
        assert expand_dates(text) == text

    def test_year_standalone_not_matched(self):
        # A bare 4-digit number shouldn't be treated as a date
        assert expand_dates("W roku 2025 zdarzyło się wiele.") == "W roku 2025 zdarzyło się wiele."
