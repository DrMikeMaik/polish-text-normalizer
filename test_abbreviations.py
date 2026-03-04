"""Tests for Polish abbreviation expander."""

import pytest
from abbreviations_pl import expand_abbreviations


class TestBasicExpansion:
    """Test basic abbreviation → full form expansion."""

    def test_dr(self):
        assert "doktor" in expand_abbreviations("dr Kowalski")

    def test_dr_with_dot(self):
        assert "doktor" in expand_abbreviations("dr. Kowalski")

    def test_prof(self):
        assert "profesor" in expand_abbreviations("prof. Nowak")

    def test_mgr(self):
        assert "magister" in expand_abbreviations("mgr Wiśniewski")

    def test_inz(self):
        assert "inżynier" in expand_abbreviations("inż. Kowalski")

    def test_ul(self):
        assert "ulica" in expand_abbreviations("ul. Marszałkowska")

    def test_al(self):
        assert "aleja" in expand_abbreviations("al. Jerozolimskie")

    def test_sw(self):
        assert "święty" in expand_abbreviations("św. Jan")


class TestCommonPhrases:
    """Test common phrase abbreviations."""

    def test_np(self):
        assert "na przykład" in expand_abbreviations("np. można")

    def test_m_in(self):
        assert "między innymi" in expand_abbreviations("m.in. tak")

    def test_tj(self):
        assert "to jest" in expand_abbreviations("tj. rano")

    def test_itp(self):
        assert "i tym podobne" in expand_abbreviations("itp.")

    def test_itd(self):
        assert "i tak dalej" in expand_abbreviations("itd.")

    def test_tzn(self):
        assert "to znaczy" in expand_abbreviations("tzn. wszystko")

    def test_wg(self):
        assert "według" in expand_abbreviations("wg raportu")

    def test_ok(self):
        assert "około" in expand_abbreviations("ok. 50")

    def test_tzw(self):
        assert "tak zwany" in expand_abbreviations("tzw. problem")


class TestCasePreservation:
    """Test that case is preserved correctly."""

    def test_lowercase(self):
        result = expand_abbreviations("dr Kowalski")
        assert result.startswith("doktor")

    def test_capitalized(self):
        result = expand_abbreviations("Dr Kowalski")
        assert result.startswith("Doktor")

    def test_uppercase(self):
        result = expand_abbreviations("DR Kowalski")
        assert result.startswith("DOKTOR")

    def test_np_capitalized(self):
        result = expand_abbreviations("Np. tutaj")
        assert "Na przykład" in result


class TestDays:
    """Test day-of-week abbreviations."""

    def test_pn(self):
        assert "poniedziałek" in expand_abbreviations("pn.")

    def test_wt(self):
        assert "wtorek" in expand_abbreviations("wt.")

    def test_sr(self):
        assert "środa" in expand_abbreviations("śr.")

    def test_czw(self):
        assert "czwartek" in expand_abbreviations("czw.")

    def test_pt(self):
        assert "piątek" in expand_abbreviations("pt.")

    def test_sb(self):
        assert "sobota" in expand_abbreviations("sb.")

    def test_nd(self):
        assert "niedziela" in expand_abbreviations("nd.")


class TestMilitary:
    """Test military rank abbreviations."""

    def test_gen(self):
        assert "generał" in expand_abbreviations("gen. Anders")

    def test_plk(self):
        assert "pułkownik" in expand_abbreviations("płk. Stauffenberg")

    def test_mjr(self):
        assert "major" in expand_abbreviations("mjr Nowak")


class TestUnits:
    """Test unit/measure abbreviations."""

    def test_godz(self):
        assert "godzina" in expand_abbreviations("godz. 10")

    def test_tel(self):
        assert "telefon" in expand_abbreviations("tel. 123")

    def test_nr(self):
        assert "numer" in expand_abbreviations("nr 5")

    def test_tys(self):
        assert "tysięcy" in expand_abbreviations("50 tys. osób")

    def test_mln(self):
        assert "milionów" in expand_abbreviations("3 mln zł")


class TestEdgeCases:
    """Test edge cases and non-interference."""

    def test_empty_string(self):
        assert expand_abbreviations("") == ""

    def test_no_abbreviations(self):
        text = "To jest zwykłe zdanie bez skrótów."
        assert expand_abbreviations(text) == text

    def test_abbreviation_mid_word_no_expand(self):
        # "dr" inside a word shouldn't be expanded
        result = expand_abbreviations("drewno")
        assert "doktor" not in result

    def test_multiple_abbreviations(self):
        result = expand_abbreviations("Dr prof. Nowak, ul. Główna")
        assert "Doktor" in result
        assert "profesor" in result
        assert "ulica" in result

    def test_compound_m_in(self):
        # m.in. should not expand "m" and "in" separately
        result = expand_abbreviations("m.in. tutaj")
        assert "między innymi" in result

    def test_sentence_end(self):
        result = expand_abbreviations("Tak napisał dr.")
        assert "doktor" in result

    def test_comma_after(self):
        result = expand_abbreviations("dr, mgr i prof.")
        assert "doktor" in result
        assert "magister" in result
        assert "profesor" in result


class TestFullSentences:
    """Integration tests with realistic sentences."""

    def test_newsletter_style(self):
        text = "Dr Nowak z ul. Długiej, wg raportu ok. 3 mln osób."
        result = expand_abbreviations(text)
        assert "doktor" in result.lower()
        assert "ulica" in result.lower()
        assert "według" in result.lower()
        assert "około" in result.lower()
        assert "milionów" in result.lower()

    def test_schedule(self):
        text = "Spotkanie pn. godz. 10, tj. rano."
        result = expand_abbreviations(text)
        assert "poniedziałek" in result.lower()
        assert "godzina" in result.lower()
        assert "to jest" in result.lower()
