"""Tests for Polish currency expansion."""

import pytest
from polish_text_normalizer.currency_pl import expand_currencies


class TestZloty:
    def test_simple(self):
        assert "pięć złotych" in expand_currencies("5 zł")

    def test_one_zloty(self):
        assert "jeden złoty" in expand_currencies("1 zł")

    def test_two_zlote(self):
        assert "dwa złote" in expand_currencies("2 zł")

    def test_with_grosze(self):
        result = expand_currencies("3,50 zł")
        assert "trzy złote" in result
        assert "pięćdziesiąt groszy" in result

    def test_one_grosz(self):
        result = expand_currencies("0,01 zł")
        assert "jeden grosz" in result

    def test_pln_code(self):
        assert "złotych" in expand_currencies("100 PLN")

    def test_large_amount(self):
        result = expand_currencies("2500,99 PLN")
        assert "złot" in result  # some form of złoty/złote/złotych


class TestEuro:
    def test_eur_code(self):
        assert "euro" in expand_currencies("100 EUR")

    def test_euro_symbol(self):
        assert "euro" in expand_currencies("€100")

    def test_euro_with_cents(self):
        result = expand_currencies("5,99 EUR")
        assert "euro" in result
        assert "cent" in result


class TestDollar:
    def test_dollar_after(self):
        assert "dolar" in expand_currencies("25 $")

    def test_dollar_before(self):
        assert "dolar" in expand_currencies("$25")

    def test_usd_code(self):
        assert "dolar" in expand_currencies("100 USD")


class TestPound:
    def test_gbp(self):
        assert "funt" in expand_currencies("100 GBP")

    def test_pound_symbol(self):
        assert "funt" in expand_currencies("£50")


class TestNoFalsePositives:
    def test_plain_number_unchanged(self):
        text = "Mam 5 kotów"
        assert expand_currencies(text) == text

    def test_no_currency_symbol(self):
        text = "To kosztuje dużo"
        assert expand_currencies(text) == text
