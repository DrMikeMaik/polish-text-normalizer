"""Tests for emails_urls_pl.py — email and URL expansion for Polish TTS."""

import pytest
from polish_text_normalizer.emails_urls_pl import expand_emails_urls


class TestEmails:
    def test_simple_email(self):
        assert expand_emails_urls("jan@example.com") == "jan małpa example kropka com"

    def test_email_pl_domain(self):
        assert expand_emails_urls("user@mail.pl") == "user małpa mail kropka pl"

    def test_email_with_dots_in_local(self):
        assert expand_emails_urls("jan.kowalski@firma.pl") == \
            "jan kropka kowalski małpa firma kropka pl"

    def test_email_with_plus(self):
        assert expand_emails_urls("user+tag@gmail.com") == \
            "user plus tag małpa gmail kropka com"

    def test_email_with_hyphen_domain(self):
        assert expand_emails_urls("info@my-company.com") == \
            "info małpa my myślnik company kropka com"

    def test_email_with_underscore(self):
        assert expand_emails_urls("jan_k@wp.pl") == \
            "jan podkreślnik k małpa wp kropka pl"

    def test_email_in_sentence(self):
        result = expand_emails_urls("Pisz na jan@example.com lub dzwoń.")
        assert "jan małpa example kropka com" in result
        assert result.startswith("Pisz na ")
        assert result.endswith(" lub dzwoń.")

    def test_email_with_numbers(self):
        assert expand_emails_urls("user123@test.org") == \
            "user123 małpa test kropka org"

    def test_email_subdomain(self):
        assert expand_emails_urls("a@sub.domain.co.uk") == \
            "a małpa sub kropka domain kropka co kropka uk"


class TestURLs:
    def test_simple_https(self):
        assert expand_emails_urls("https://example.com") == "example kropka com"

    def test_http(self):
        assert expand_emails_urls("http://example.com") == "example kropka com"

    def test_www_prefix_stripped(self):
        assert expand_emails_urls("https://www.example.com") == "example kropka com"

    def test_with_path(self):
        assert expand_emails_urls("https://example.com/page") == \
            "example kropka com ukośnik page"

    def test_with_deep_path(self):
        result = expand_emails_urls("https://example.com/a/b/c")
        assert result == "example kropka com ukośnik a ukośnik b ukośnik c"

    def test_with_query(self):
        result = expand_emails_urls("https://example.com/search?q=test")
        assert "example kropka com" in result
        assert "znak zapytania" in result
        assert "równa się" in result

    def test_url_in_sentence(self):
        result = expand_emails_urls("Odwiedź https://example.com teraz.")
        assert result == "Odwiedź example kropka com teraz."

    def test_url_with_trailing_period(self):
        result = expand_emails_urls("Strona: https://example.com.")
        assert result == "Strona: example kropka com."

    def test_url_with_hyphen_domain(self):
        result = expand_emails_urls("https://my-site.pl/info")
        assert result == "my myślnik site kropka pl ukośnik info"

    def test_url_pl_domain(self):
        assert expand_emails_urls("https://onet.pl") == "onet kropka pl"

    def test_www_without_scheme(self):
        assert expand_emails_urls("www.example.com") == "example kropka com"

    def test_url_trailing_slash_only(self):
        assert expand_emails_urls("https://example.com/") == "example kropka com"

    def test_url_with_fragment(self):
        result = expand_emails_urls("https://example.com/page#section")
        assert "hasz" in result


class TestMixed:
    def test_email_and_url_in_same_text(self):
        text = "Kontakt: jan@firma.pl lub https://firma.pl/kontakt"
        result = expand_emails_urls(text)
        assert "małpa" in result
        assert "firma kropka pl" in result
        assert "ukośnik kontakt" in result

    def test_no_match_plain_text(self):
        text = "Zwykły tekst bez adresów."
        assert expand_emails_urls(text) == text

    def test_no_match_number_with_dot(self):
        # Should NOT match "3.5" as a URL
        assert expand_emails_urls("Około 3.5 litra") == "Około 3.5 litra"

    def test_preserves_surrounding_text(self):
        text = "Zapraszam na https://sklep.pl - tanio i szybko!"
        result = expand_emails_urls(text)
        assert result.startswith("Zapraszam na ")
        assert result.endswith(" - tanio i szybko!")
