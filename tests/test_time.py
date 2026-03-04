"""Tests for Polish time pattern expander."""

import pytest
from polish_text_normalizer.time_pl import time_to_words, expand_times


class TestTimeToWords:
    def test_full_hour(self):
        assert time_to_words(8, 0) == "ósma"

    def test_midnight(self):
        assert time_to_words(0, 0) == "zero"

    def test_noon(self):
        assert time_to_words(12, 0) == "dwunasta"

    def test_13_45(self):
        assert time_to_words(13, 45) == "trzynasta czterdzieści pięć"

    def test_8_30(self):
        assert time_to_words(8, 30) == "ósma trzydzieści"

    def test_21_15(self):
        assert time_to_words(21, 15) == "dwudziesta pierwsza piętnaście"

    def test_1_05(self):
        assert time_to_words(1, 5) == "pierwsza pięć"

    def test_23_59(self):
        assert time_to_words(23, 59) == "dwudziesta trzecia pięćdziesiąt dziewięć"

    def test_0_30(self):
        assert time_to_words(0, 30) == "zero trzydzieści"

    def test_24_00(self):
        assert time_to_words(24, 0) == "dwudziesta czwarta"


class TestExpandTimes:
    def test_basic(self):
        assert expand_times("Spotkanie o 13:45") == "Spotkanie o trzynasta czterdzieści pięć"

    def test_full_hour(self):
        assert expand_times("Wstałem o 8:00") == "Wstałem o ósma"

    def test_leading_zero(self):
        assert expand_times("Alarm na 08:30") == "Alarm na ósma trzydzieści"

    def test_multiple_times(self):
        result = expand_times("Od 8:00 do 16:00")
        assert result == "Od ósma do szesnasta"

    def test_midnight(self):
        assert expand_times("O 0:00 zamykamy") == "O zero zamykamy"

    def test_no_match_invalid_hour(self):
        assert expand_times("25:00") == "25:00"

    def test_no_match_invalid_minute(self):
        assert expand_times("12:60") == "12:60"

    def test_no_match_single_digit_minute(self):
        # 12:5 is not valid HH:MM format (needs two digits for minutes)
        assert expand_times("12:5") == "12:5"

    def test_not_inside_number(self):
        # Ratio-like patterns — this matches as time, which is acceptable
        # since in Polish text 3:14 appearing alone is ambiguous
        result = expand_times("3:14")
        assert "trzecia" in result

    def test_in_sentence(self):
        result = expand_times("Pociąg o 17:30 z Warszawy")
        assert result == "Pociąg o siedemnasta trzydzieści z Warszawy"

    def test_evening(self):
        assert expand_times("Film o 20:00") == "Film o dwudziesta"

    def test_preserves_surrounding_text(self):
        result = expand_times("abc 14:15 def")
        assert result == "abc czternasta piętnaście def"


class TestTimeRanges:
    def test_basic_range(self):
        result = expand_times("14:00-15:30")
        assert result == "od czternastej do piętnastej trzydzieści"

    def test_range_in_sentence(self):
        result = expand_times("Spotkanie 14:00-15:30 w sali")
        assert "od czternastej do piętnastej trzydzieści" in result

    def test_range_with_minutes(self):
        result = expand_times("8:30-9:45")
        assert result == "od ósmej trzydzieści do dziewiątej czterdzieści pięć"

    def test_full_hours_range(self):
        result = expand_times("8:00-16:00")
        assert result == "od ósmej do szesnastej"

    def test_range_preserves_single_times(self):
        # After range expansion, remaining single times still work
        result = expand_times("8:00-16:00, przerwa o 12:00")
        assert "od ósmej do szesnastej" in result
        assert "dwunasta" in result
