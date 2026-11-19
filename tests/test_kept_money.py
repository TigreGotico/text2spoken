"""An amount next to a currency sign that the language does not read stays as written (design section 10).

A language file reads the currencies of its own table. A number next to any other currency sign used to read
alone, so the sign stayed glued to the number word: ar `€5` gave `€خمسة` and de `¥5` gave `¥fünf`. The language has
no name for that currency, so the whole amount is a decline: it stays as written, with the usual unread warning.
"""
import random
import unicodedata

import pytest

from text2spoken import NormalizationParams, UnreadFormError, normalize
from text2spoken.core import language, parsers

SIGNS = ("€", "¥", "₹", "£")

READ = {
    # The currency name comes from the `currencies` table of each language file, which cites its source there.
    ("de-DE", "€"): "fünf Euro", ("de-DE", "£"): "fünf Pfund",
    ("es-ES", "€"): "cinco euros", ("es-ES", "£"): "cinco libras",
    ("eu-ES", "€"): "bost euro", ("eu-ES", "£"): "bost libera",
    ("fr-FR", "€"): "cinq euros", ("fr-FR", "£"): "cinq livres",
    ("ru-RU", "€"): "пять евро",
}
"""The signs that each language reads. Every other sign of `SIGNS` has no entry in the table of the language."""

TAGS = ("ar-001", "arz-EG", "de-DE", "es-ES", "eu-ES", "fr-FR", "ru-RU")
CASES = [(tag, sign, text) for tag in TAGS for sign in SIGNS for text in (f"{sign}5", f"5 {sign}")]


@pytest.mark.parametrize(("tag", "sign", "text"), CASES)
def test_a_sign_reads_or_its_amount_stays_as_written(tag, sign, text):
    assert normalize(text, tag) == READ.get((tag, sign), text)


@pytest.mark.parametrize(("tag", "sign", "text"), [case for case in CASES if case[:2] not in READ])
def test_a_kept_amount_logs_the_unread_warning_and_raises_in_strict_mode(tag, sign, text, caplog):
    assert normalize(f"x {text} y", tag) == f"x {text} y"
    assert f"unread written form {text.split()[0]!r}" in caplog.text
    with pytest.raises(UnreadFormError):
        normalize(text, tag, NormalizationParams(strict=True))


@pytest.mark.parametrize(("tag", "text", "expected"), [
    # de.wiktionary, kosten: takes the accusative; "zwei" is the same in every case.
    ("de-DE", "Das kostet ¥2 und 2 €.", "Das kostet ¥2 und zwei Euro."),
    ("es-ES", "Cuesta 3 ₹ o 3 €.", "Cuesta 3 ₹ o tres euros."),
    ("ru-RU", "Это стоит £5 или 5 €.", "Это стоит £5 или пять евро."),
    ("ar-001", "الثمن €5 اليوم", "الثمن €5 اليوم"),
])
def test_a_kept_amount_leaves_the_other_amounts_of_the_text_read(tag, text, expected):
    assert normalize(text, tag) == expected


@pytest.mark.parametrize("text", ["-¥5", "¥-5", "¥−5"])
def test_a_minus_next_to_the_sign_stays_with_the_kept_amount(text):
    assert normalize(text, "de-DE") == text


# A currency sign after a letter is no amount, so the number next to the sign stays as written with it: a sign glued
# to a number word is no reading (design section 10). A sign before a minus is no amount either, except in nl, whose
# amount reads the minus after the sign ("min vijf euro").
GLUED_TAGS = ("pt-PT", "pt-BR", "es-ES", "de-DE", "fr-FR", "eu-ES", "ru-RU", "ar-001", "it-IT", "nl-NL", "en-GB",
              "sv-SE", "hi-IN")
GLUED_AMOUNTS = [(tag, text) for tag in GLUED_TAGS for text in ("a¥5", "Laura£5", "x a€7 y")] + [
    (tag, text) for tag in GLUED_TAGS if tag != "nl-NL" for text in ("¥-5", "€−5")]


@pytest.mark.parametrize(("tag", "text"), GLUED_AMOUNTS)
def test_a_number_that_a_currency_sign_touches_reads_only_as_an_amount(tag, text):
    assert normalize(text, tag) == text


@pytest.mark.parametrize(("tag", "text"), [("pt-PT", "a¥5,5"), ("es-ES", "a¥5,5"), ("en-GB", "a¥5.5"),
                                           ("hi-IN", "a¥5.5"), ("pt-PT", "5,5¥b")])
def test_a_decimal_that_a_currency_sign_touches_reads_only_as_an_amount(tag, text):
    assert normalize(text, tag) == text


@pytest.mark.parametrize(("tag", "expected"), [("en-GB", "bitcoin one"), ("pt-PT", "bitcoin um")])
def test_a_sign_that_the_symbol_form_names_still_reads(tag, expected):
    # CLDR 49 annotations: ₿ is "bitcoin" in en and pt; the number reads as a cardinal after it.
    assert normalize("₿1", tag) == expected


def sweep_tags() -> list[str]:
    """Each variety tag of each language file, and each language with no file that reads cardinals."""
    specs = {spec.code: spec for spec in language._registry().values()}
    with_file = {variety.tag for spec in specs.values() for variety in spec.varieties}
    no_file = {locale.split("_")[0] for locale in language.rbnf_locales()} | set(parsers.number_writer_languages())
    return sorted(with_file | (no_file - set(specs)))


def glued(output: str) -> list[str]:
    """The currency signs of the output that touch a letter on either side."""
    return [output[max(0, i - 1):i + 2] for i, char in enumerate(output)
            if unicodedata.category(char) == "Sc"
            and ((i and output[i - 1].isalpha()) or (i + 1 < len(output) and output[i + 1].isalpha()))]


@pytest.mark.parametrize("seed", range(2))
def test_no_currency_sign_touches_a_letter_in_any_language(seed):
    rng = random.Random(seed)
    tags = sweep_tags()
    assert len(tags) > 100
    for tag in tags:
        for shape in ("€{}", "{} €", "¥{}", "₹{}"):
            amount = str(rng.choice((rng.randint(1, 99), rng.randint(100, 99999))))
            for text in (shape.format(5), f"a {shape.format(amount)} b"):
                once = normalize(text, tag)
                assert not glued(once), (tag, text, once)
                assert normalize(once, tag) == once, (tag, text, once)
