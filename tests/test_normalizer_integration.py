"""Integration tests for the full Polish text normalizer pipeline.

These test multi-step interactions where pipeline ordering matters —
cases where one step's output could break another step's input.
"""

import pytest
from polish_text_normalizer.polish_text_normalizer import normalize_polish_text


class TestPipelineOrdering:
    """Cases where step ordering matters."""

    def test_abbreviation_then_number(self):
        # "ok." must expand before number conversion sees "50"
        result = normalize_polish_text("ok. 50 osób")
        assert "około" in result
        assert "pięćdziesiąt" in result

    def test_abbreviation_then_currency(self):
        result = normalize_polish_text("ok. 50 zł")
        assert "około" in result
        assert "złotych" in result

    def test_currency_before_number(self):
        # Currency step must grab "5,99 zł" before number step sees bare "5"
        result = normalize_polish_text("Cena: 5,99 zł")
        assert "złot" in result  # złotych/złote
        assert "groszy" in result or "grosz" in result

    def test_roman_before_number(self):
        # "XXI" must be expanded as Roman, not left for number step
        result = normalize_polish_text("W XXI wieku")
        assert "dwudziest" in result  # dwudziestym pierwszym

    def test_date_before_number(self):
        # "27.02.2026" must be recognized as date, not "27" + dots
        result = normalize_polish_text("Spotkanie 27.02.2026")
        assert "dwudziestego siódmego" in result
        assert "lutego" in result

    def test_time_before_range(self):
        # "14:00-15:30" — time range, not a bare range
        result = normalize_polish_text("Spotkanie 14:00-15:30")
        assert "czternast" in result
        assert "piętnast" in result

    def test_time_before_number(self):
        # "13:45" should become time, not "13" colon "45"
        result = normalize_polish_text("O 13:45")
        assert "trzynasta" in result
        assert "czterdzieści pięć" in result

    def test_phone_before_range(self):
        # Phone "512 345 678" must not be interpreted as ranges
        result = normalize_polish_text("Tel: 512 345 678")
        assert "pięć jeden dwa" in result

    def test_email_before_abbreviation(self):
        # "dr@hospital.pl" is an email, not abbreviation "dr" + junk
        result = normalize_polish_text("Napisz do dr@hospital.pl")
        assert "małpa" in result
        assert "hospital" in result

    def test_url_before_special_chars(self):
        # URL dots/slashes must not be mangled by special chars step
        result = normalize_polish_text("Sprawdź https://example.com/page")
        assert "example kropka com" in result

    def test_range_before_number(self):
        # "8-16" must become range, not "8 minus 16"
        result = normalize_polish_text("Czynne 8-16")
        assert "od" in result
        assert "do" in result
        assert "minus" not in result

    def test_special_chars_before_number(self):
        # "20°C" — degree symbol must expand before number eats "20"
        result = normalize_polish_text("Temperatura 20°C")
        assert "stopni" in result
        assert "Celsjusza" in result

    def test_section_symbol_before_number(self):
        result = normalize_polish_text("§ 5 regulaminu")
        assert "paragraf" in result
        assert "pięć" in result


class TestComplexSentences:
    """Real-world-ish sentences exercising multiple pipeline steps."""

    def test_doctor_address_hours(self):
        result = normalize_polish_text("Dr Nowak, ul. Długa 15, godz. 8-16.")
        assert "doktor" in result.lower() or "Doktor" in result
        assert "ulica" in result.lower() or "Ulica" in result
        assert "piętnaście" in result or "piętnast" in result

    def test_population_stats(self):
        result = normalize_polish_text("Ok. 3,5 mln osób, tj. ok. 10% populacji.")
        assert "około" in result.lower() or "Około" in result
        assert "to jest" in result.lower() or "To jest" in result

    def test_meeting_with_professor(self):
        result = normalize_polish_text(
            "Spotkanie w pn. o godz. 10, m.in. z prof. Kowalskim."
        )
        assert "poniedziałek" in result
        assert "między innymi" in result
        assert "profesor" in result.lower() or "Profesor" in result

    def test_king_and_century(self):
        result = normalize_polish_text("Jan III Sobieski rządził w XVII wieku.")
        assert "trzeci" in result
        assert "siedemnast" in result

    def test_price_in_two_currencies(self):
        result = normalize_polish_text("Cena: 5,99 zł za sztukę, tj. ok. $2.")
        assert "złot" in result
        assert "dolar" in result

    def test_train_schedule(self):
        result = normalize_polish_text("Pociąg o 13:45, godz. 8-16 czynne.")
        assert "trzynasta" in result
        assert "czterdzieści pięć" in result

    def test_meeting_time_range_room(self):
        result = normalize_polish_text("Spotkanie 14:00-15:30 w sali 5.")
        assert "pięć" in result

    def test_email_in_context(self):
        result = normalize_polish_text(
            "Wyślij na jan.kowalski@firma.pl do godz. 16:00."
        )
        assert "małpa" in result
        assert "szesnasta" in result

    def test_date_with_time_and_currency(self):
        result = normalize_polish_text(
            "Termin: 15.03.2026, godz. 10:00, opłata 50 zł."
        )
        assert "marca" in result or "trzeciego" in result
        assert "dziesiąta" in result
        assert "złotych" in result

    def test_phone_with_address(self):
        result = normalize_polish_text(
            "Kontakt: ul. Marszałkowska 10, tel. +48 512 345 678."
        )
        assert "ulica" in result.lower() or "Ulica" in result
        assert "plus czterdzieści osiem" in result
        assert "pięć jeden dwa" in result

    def test_fraction_and_temperature(self):
        result = normalize_polish_text("½ litra wody o temp. 20°C.")
        assert "pół" in result or "jedna druga" in result
        assert "stopni Celsjusza" in result

    def test_math_expression(self):
        result = normalize_polish_text("2 + 2 = 4, a 3 × 5 = 15")
        assert "plus" in result
        assert "równa się" in result
        assert "razy" in result

    def test_url_and_date(self):
        result = normalize_polish_text(
            "Więcej na https://example.com od 01.04.2026."
        )
        assert "example kropka com" in result
        assert "pierwszego" in result
        assert "kwietnia" in result


class TestEdgeCases:
    """Edge cases and potential pipeline conflicts."""

    def test_empty_string(self):
        assert normalize_polish_text("") == ""

    def test_plain_text_unchanged(self):
        text = "To jest zwykłe zdanie bez niczego specjalnego."
        result = normalize_polish_text(text)
        assert result == text

    def test_multiple_currencies_same_line(self):
        result = normalize_polish_text("100 zł = 25 EUR = $30")
        assert "złotych" in result
        assert "euro" in result
        assert "dolar" in result

    def test_abbreviation_with_period_not_confused_as_sentence_end(self):
        # "dr." followed by name — period is part of abbreviation
        result = normalize_polish_text("Wizyta u dr. Nowaka o 10:00.")
        assert "doktor" in result.lower() or "Doktor" in result

    def test_consecutive_numbers(self):
        result = normalize_polish_text("Sala 5, piętro 3, budynek 12.")
        assert "pięć" in result
        assert "trzy" in result
        assert "dwanaście" in result

    def test_mixed_roman_and_arabic(self):
        result = normalize_polish_text("Rozdział III, strona 45.")
        assert "trzeci" in result
        assert "czterdzieści pięć" in result

    def test_no_double_expansion(self):
        # Numbers that result from earlier expansions shouldn't be re-expanded weirdly
        result = normalize_polish_text("§ 5")
        assert "paragraf" in result
        assert "pięć" in result
        # Should not have nested expansions
        assert result.count("paragraf") == 1
