"""Mixed numbers: a whole part, one space or no-break space, and a proper fraction, as `2 1/2`. A language file that
gives the reading reads the two parts as one number; every other language keeps the text as written, and never
reads the parts as two numbers (design section 10). The readings of each language file are rows of tests/data."""
import logging
import warnings

import pytest

from text2spoken import (FrozenMap, GrammaticalGender, NormalizationParams, SayAs, UnreadFormError, analyze,
                         normalize, supports)
from text2spoken.core import language


def mixed_spans(text: str, lang: str) -> list:
    return [span for span in analyze(text, lang).spans if span.fields.get("whole")]


NOT_MIXED = [
    ("2 1/2/2024", "a date after a number"),
    ("3-2 1/2", "a score or a range before the fraction"),
    ("2:1 1/2", "a ratio before the fraction"),
    ("1,2 1/2", "a decimal before the fraction"),
    ("5 1 1/2", "a longer run of digit groups"),
    ("1 1/2 3", "a longer run of digit groups"),
    ("A2 1/2", "a code with a letter"),
    ("2  1/2", "two spaces"),
    ("2 3/2", "an improper fraction"),
    ("2 1/200", "a denominator above 100"),
]


@pytest.mark.parametrize("text,why", NOT_MIXED, ids=[text for text, _ in NOT_MIXED])
def test_a_text_that_is_no_mixed_number_gives_no_mixed_number_span(text, why):
    assert mixed_spans(text, "en-US") == []


def test_a_date_after_a_number_reads_as_the_number_and_the_date():
    assert normalize("2 1/2/2024", "en-US") == f"two {normalize('1/2/2024', 'en-US')}"


KEPT = [
    ("0 1/2", "a whole part of zero"),
    ("02 1/2", "a leading zero in the whole part"),
    ("2 01/2", "a leading zero in the numerator, as in a day and a month"),
    ("2 1/02", "a leading zero in the denominator"),
    ("-2 1/2", "a sign, which may be a dash"),
    ("1 1/2 kg", "a unit after it, as `3/4 kg` stays as written"),
    ("2 1/2%", "a symbol after it"),
    ("#2 1/2", "a symbol before it"),
    ("２ 1/2", "digits from two digit sets"),
]


@pytest.mark.parametrize("text,why", KEPT, ids=[text for text, _ in KEPT])
def test_a_mixed_number_with_an_unclear_reading_stays_as_written_with_the_unread_warning(caplog, text, why):
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(text, "en-US") == text
    assert any(record.levelno == logging.WARNING for record in caplog.records)


@pytest.mark.parametrize("gap", [" ", " "], ids=["space", "no-break space"])
def test_the_gap_is_a_space_or_a_no_break_space(gap):
    assert normalize(f"Add 2{gap}1/2 cups.", "en-US") == "Add two and a half cups."


# A mixed number next to a currency symbol stays as written whole. An amount reads no mixed number, and a reading of
# the parts would be two numbers ("two dollars one-half") or leave the sign unread ("deux et demi €"). The symbol
# may stand before or after the number, attached or after one space.
MIXED_AMOUNTS = [
    ("en-US", "It costs $2 1/2."), ("en-GB", "It costs €2 1/2."), ("pt-PT", "Custa $2 1/2."),
    ("es-ES", "Cuesta $2 1/2."), ("fr-FR", "Il coûte 2 1/2 €."), ("de-DE", "Es kostet 2 1/2 €."),
    ("en-US", "It costs $ 2 1/2."), ("de-DE", "Es kostet 2 1/2€."), ("it-IT", "Costa 2 1/2 €."),
    ("nl-NL", "Het kost € 2 1/2."), ("pt-BR", "Custa R$ 2 1/2."), ("en-US", "It costs $٢ ١/٢."),
]


@pytest.mark.parametrize(("lang", "text"), MIXED_AMOUNTS)
def test_a_mixed_number_next_to_a_currency_symbol_stays_as_written(lang, text):
    assert normalize(text, lang) == text


@pytest.mark.parametrize(("lang", "text", "expected"), [
    ("en-US", "It costs $2.", "It costs two dollars."),
    ("en-US", "It costs $2 and 1/2 hour.", "It costs two dollars and one-half hour."),
    ("en-US", "Add 2 1/2 cups.", "Add two and a half cups."),
])
def test_an_amount_with_no_mixed_number_still_reads(lang, text, expected):
    assert normalize(text, lang) == expected


# A symbol with a number on its other side, in any digit set, is the symbol of that number, so the mixed number beside
# it reads, and a second pass changes nothing (design sections 4.7 and 11). A symbol that `SYMBOL` reads in part, as
# `₵` of `GH₵`, does not stay beside the mixed number either.
MIXED_BESIDE_AMOUNTS = [
    ("en-GB", "x 3 1/2 €5 y", "x three and a half five euros y"),
    ("en-GB", "I paid 5€ 2 1/2 years ago.", "I paid five euros two and a half years ago."),
    ("en-GB", "Mix 2 1/2 £5 bags.", "Mix two and a half five pounds bags."),
    ("en-GB", "5$ 1 1/2", "five dollars one and a half"),
    ("en-GB", "wait 1 1/2 $5", "wait one and a half five dollars"),
    ("en-US", "x 3 1/2 €5 y", "x three and a half five euros y"),
    ("en-US", "I paid 5€ 2 1/2 years ago.", "I paid five euros two and a half years ago."),
    ("en-US", "Mix 2 1/2 £5 bags.", "Mix two and a half five pounds bags."),
    ("en-US", "wait 1 1/2 $5", "wait one and a half five dollars"),
    ("de-DE", "Gab 5 € 2 1/2 Tage", "Gab fünf Euro zweieinhalb Tage"),
    ("de-DE", "x 3 1/2 €5 y", "x dreieinhalb fünf Euro y"),
    ("de-DE", "5$ 1 1/2", "fünf Dollar eineinhalb"),
    ("de-DE", "wait 1 1/2 $5", "wait eineinhalb fünf Dollar"),
    ("fr-FR", "5$ 1 1/2", "cinq dollars un et demi"),
    ("es-ES", "5$ 1 1/2", "cinco dólares uno y medio"),
    ("it-IT", "5$ 1 1/2", "cinque dollari uno e mezzo"),
    ("en-GB", "I paid ５€ 2 1/2 years ago.", "I paid five euros two and a half years ago."),
    ("en-GB", "I paid ٥€ ٢ ١/٢ years ago.", "I paid five euros two and a half years ago."),
    ("en-US", "Mix 2 1/2 £٥ bags.", "Mix two and a half five pounds bags."),
    ("de-DE", "Gab ٥ € 2 1/2 Tage", "Gab fünf Euro zweieinhalb Tage"),
    ("de-DE", "Gab ५ € 2 1/2 Tage", "Gab fünf Euro zweieinhalb Tage"),
    ("en", "It costs GH₵ 2 1/2.", "It costs GH Ghanaian Cedi two and a half."),
    ("en-GB", "2 1/2 GH₵", "two and a half GH Ghanaian Cedi"),
]


@pytest.mark.parametrize(("lang", "text", "expected"), MIXED_BESIDE_AMOUNTS)
def test_a_mixed_number_beside_a_separate_amount_reads(lang, text, expected):
    assert normalize(text, lang) == expected
    assert normalize(expected, lang) == expected


def test_the_whole_part_of_a_kept_mixed_number_is_no_amount_in_a_second_pass():
    """Italian keeps a mixed number before a word, so `euro` stands before its whole part after the first pass."""
    assert normalize("x ٥€ ٢ ١/٢ y", "it-IT") == "x cinque euro ٢ ١/٢ y"
    assert normalize("x cinque euro ٢ ١/٢ y", "it-IT") == "x cinque euro ٢ ١/٢ y"


DECLINING = ["ar", "ru-RU", "eu-ES", "sv-SE", "pl-PL", "fi-FI", "tr-TR", "ja-JP", "da-DK"]
"""Language files that give no reading of a mixed number, and languages with no file, which read through RBNF or
ovos-number-parser."""


@pytest.mark.parametrize("lang", DECLINING)
def test_a_language_with_no_reading_keeps_the_mixed_number_as_written(caplog, lang):
    """Each part alone reads in some of these languages, as `2` does in every one, so a reading of the parts
    would be two numbers."""
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize("2 1/2", lang) == "2 1/2"
    assert any("2" in record.getMessage() for record in caplog.records if record.levelno == logging.WARNING)
    with pytest.raises(UnreadFormError):
        normalize("2 1/2", lang, NormalizationParams(strict=True))


@pytest.mark.parametrize("lang", ["en-US", "en-GB", "pt-PT", "pt-BR", "es-ES", "fr-FR", "it-IT", "de-DE", "nl-NL",
                                  "el-GR", *DECLINING])
@pytest.mark.parametrize("text", ["2 1/2", "Wait 10 3/4 hours.", "2 1/2, 3 1/3 e 4 3/4", "0 1/2", "5 1 1/2"])
def test_a_second_pass_changes_nothing(lang, text):
    once = normalize(text, lang)
    assert normalize(once, lang) == once


GENDERLESS = sorted({variety.tag for spec in language._registry().values() if not spec.genders
                     for variety in spec.varieties} | {"sv-SE", "hu-HU", "fi-FI", "tr-TR", "ja-JP"})
"""Every variety of a language file that declares no grammatical gender, and languages with no file and no gender."""


def outcome(text: str, lang: str, params: NormalizationParams, say_as: SayAs | None = None) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return normalize(text, lang, params, say_as=say_as)
        except Exception as error:
            return type(error).__name__


@pytest.mark.parametrize("lang", GENDERLESS)
@pytest.mark.parametrize("strict", [False, True])
def test_a_gender_has_no_effect_in_a_language_with_no_grammatical_gender(lang, strict):
    """Design section 2.3: "`default_gender`, or a gender in a hint, for a language with no grammatical gender | No
    effect. `supports(lang).genders` is empty"."""
    assert not supports(lang).genders
    plain = NormalizationParams(strict=strict)
    for gender in GrammaticalGender:
        params = NormalizationParams(strict=strict, default_gender=FrozenMap({lang.split("-")[0]: gender}))
        for text, say_as in (("Het is 2 1/2.", None), ("2 1/2", None), ("3+1/2", SayAs(interpret_as="fraction"))):
            assert outcome(text, lang, params, say_as) == outcome(text, lang, plain, say_as), (gender, text)
