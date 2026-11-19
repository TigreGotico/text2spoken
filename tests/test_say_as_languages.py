"""Say-as `digits`, `telephone`, `characters` and `ordinal` in every language that reads numbers (design section
17.5), over forty language tags from the major language families.

Each expected value comes from the writer of ovos-number-parser or from a CLDR RBNF rule set of unicode_rbnf, which
the test calls directly, with the cited words of data/rbnf_corrections.json. No expected value comes from text2spoken
code."""
import json
import logging
import pkgutil
import re
import warnings
from pathlib import Path

import ovos_number_parser
import pytest
from ovos_number_parser import pronounce_number, pronounce_ordinal
from ovos_number_parser.util import GrammaticalGender as ParserGender
from unicode_rbnf import RbnfEngine

from unicode_rbnf.engine import NoRuleForNumberError

from text2spoken import (FrozenMap, GrammaticalGender, NormalizationParams, ParameterNotHonouredWarning, SayAs,
                         UnreadFormError, UnsupportedParameterError, normalize)

TAGS = ["en-US", "pt-PT", "de-DE", "fr-FR", "es-ES", "it-IT", "nl-NL", "ru-RU", "eu-ES", "el-GR", "ar", "ca-ES",
        "gl-ES", "pl-PL", "tr-TR", "uk-UA", "sv-SE", "da-DK", "fi-FI", "hu-HU", "cs-CZ", "ro-RO", "zh-CN", "ja-JP",
        "ko-KR", "hi-IN", "fa-IR", "he-IL", "sw-KE", "yo-NG", "ha-NG", "tw", "apc", "oc-FR", "vi-VN", "id-ID",
        "cy-GB", "is-IS", "bn-IN", "ta-IN"]
"""Forty language tags: the languages with a file, and others with and without a CLDR RBNF locale."""

NO_NUMBERS = frozenset({"yo-NG", "ha-NG", "tw", "bn-IN"})
"""Tags with no writer of ovos-number-parser and no RBNF locale: no word for a digit, so `digits`, `telephone` and
`characters` decline to the plain reading."""

NO_ORDINAL = NO_NUMBERS | {"ko-KR", "cy-GB", "is-IS"}
"""Tags whose say-as `ordinal` declines. RBNF `ko` has ordinal rule sets for the native and the Sino-Korean numbers
and none with no qualifier, so the markup does not choose one; RBNF `cy` and `is` have no ordinal rule set, and no
writer reads them."""

LETTER_NAMES = frozenset({"en-US", "pt-PT"})
"""Tags whose language file has a `letter_names` table."""

WRITERS = frozenset(module.name.removeprefix("numbers_") for module in pkgutil.iter_modules(ovos_number_parser.__path__)
                    if module.name.startswith("numbers_"))
"""The languages with a writer module of their own in ovos-number-parser."""

AR_LECTS = frozenset({"apc"})
"""Arabic lect codes with no writer module of their own that the `ar` writer reads. linguatag standardizes `ajp` to
`apc` (ISO 639-3 change request 2022-006), so both read the same."""


RBNF_DIGITS = frozenset({"ca"})
"""Languages with a writer whose file names each digit by RBNF `spellout-numbering`. The Catalan file names the digit 1
"u", by the `1: u` rule of RBNF `ca`, where the writer writes "un"."""


def code(tag: str) -> str:
    return tag.split("-")[0]


CORRECTIONS = {(row["language"], row["wrong"]): row["right"] for row in json.loads(
    (Path(__file__).parents[1] / "text2spoken" / "data" / "rbnf_corrections.json").read_text(encoding="utf-8"))[
    "corrections"]}


def rbnf(tag: str, number: int, rule_set: str) -> str:
    text = RbnfEngine.for_language(code(tag)).format_number(number, ruleset_names=[rule_set]).text_by_ruleset[rule_set]
    return "".join(CORRECTIONS.get((code(tag), part), part) for part in re.split("([ \u00a0\u200b]+)", text))


def digit_word(tag: str, digit: str) -> str:
    """The cardinal of one digit: the writer of the language, else RBNF `spellout-numbering`, with zero from the
    first plain cardinal rule set of the locale (`spellout-numbering` of `zh` writes the digit sign 〇 for zero)."""
    if (code(tag) in WRITERS or code(tag) in AR_LECTS) and code(tag) not in RBNF_DIGITS:
        return pronounce_number(int(digit), tag)
    if digit == "0":
        names = RbnfEngine.for_language(code(tag)).rulesets
        return rbnf(tag, 0, next(name for name in ("spellout-cardinal", "spellout-cardinal-masculine",
                                                   "spellout-numbering") if name in names))
    return rbnf(tag, int(digit), "spellout-numbering")


def spelled(tag: str, digits: str) -> str:
    return " ".join(digit_word(tag, digit) for digit in digits)


ORDINALS = {
    **{tag: lambda number, tag=tag: pronounce_ordinal(number, tag)
       for tag in ("gl-ES", "pl-PL", "tr-TR", "uk-UA", "sv-SE", "fi-FI", "hu-HU", "cs-CZ", "ro-RO", "fa-IR",
                   "he-IL", "oc-FR", "id-ID")},
    "ar": lambda number: pronounce_ordinal(number, "ar", gender=ParserGender.MASCULINE),
    "el-GR": lambda number: rbnf("el-GR", number, "spellout-ordinal-neuter"),
    "da-DK": lambda number: rbnf("da-DK", number, "spellout-ordinal-common"),
    "hi-IN": lambda number: rbnf("hi-IN", number, "spellout-ordinal-masculine"),
    **{tag: lambda number, tag=tag: rbnf(tag, number, "spellout-ordinal")
       for tag in ("zh-CN", "ja-JP", "sw-KE", "vi-VN", "ta-IN")},
}
"""The source of the ordinal of each tag that no language file reads with an ordinal verbalizer. A language with a
writer reads through it, as it reads its cardinals; `da` reads its cardinals through RBNF (`RBNF_HELD`), so its
ordinals too. The Greek file reads a number with no noun in the neuter (`el.py`), and the Arabic file reads its
default gender, the masculine (`ar.py`). With no gender, RBNF `hi` reads the masculine and RBNF `da` the common
gender: neither has an ordinal rule set with no gender."""


def say(text: str, tag: str, value: str, params: NormalizationParams | None = None, **fields) -> str:
    return normalize(text, tag, params, say_as=SayAs(interpret_as=value, **fields))


def reads_again_the_same(spoken: str, tag: str) -> bool:
    """Design section 17.7: a second pass changes nothing, alone and spliced into a sentence."""
    return normalize(spoken, tag) == spoken and normalize(f"Room {spoken} is free.", tag) == f"Room {spoken} is free."


READ = [tag for tag in TAGS if tag not in NO_NUMBERS]


@pytest.mark.parametrize("tag", READ)
@pytest.mark.parametrize("text", ["2024", "007", "1 9"])
def test_digits_read_each_digit_by_its_cardinal(tag, text):
    """Amazon Polly, `digits`: "Spells out each digit individually"."""
    spoken = say(text, tag, "digits")
    expected = " ".join(spelled(tag, run) for run in text.split())
    assert spoken == expected
    assert reads_again_the_same(spoken, tag)


@pytest.mark.parametrize("tag", READ + ["zh-TW", "yue"])
def test_a_digit_reading_writes_zero_as_the_plain_reading_does(tag):
    """Zero in a digit reading is the word that the plain reading of the language writes for 0. Wiktionary, "〇":
    "Used to express a zero digit in a number"; a phonemizer that reads 零 can leave the sign unread. The French file
    reads a telephone group of an even length in pairs (`fr.py`)."""
    zero = normalize("0", tag)
    assert say("007", tag, "digits").split()[:2] == [zero, zero]
    if tag != "fr-FR":
        assert say("555-0100", tag, "telephone").split()[-2:] == [zero, zero]


@pytest.mark.parametrize("tag", [tag for tag in READ if tag != "fr-FR"])
@pytest.mark.parametrize("text", ["912 345 678", "555-0199", "3981900"])
def test_a_telephone_number_reads_digit_by_digit(tag, text):
    """W3C Note, section 3.3: the telephone format is processor specific; each group reads digit by digit, as in
    the `en` and `pt` files, and the groups stay in the order the text writes them. The French file reads a group of
    an even length in pairs, by the numbering plan of France (`fr.py`)."""
    spoken = say(text, tag, "telephone")
    assert spoken == spelled(tag, text.replace(" ", "").replace("-", ""))
    assert reads_again_the_same(spoken, tag)


@pytest.mark.parametrize("text,tag,value", [("Il totale è 6.000 franchi.", "it-CH", "cardinal"),
                                             ("COVID-19.", "eu-ES", "cardinal"),
                                             ("6/89 Legea, uztailaren 6koa.", "eu-ES", "fraction")])
def test_a_span_kept_as_written_stays_so_under_a_value_other_than_telephone(text, tag, value):
    """The markup is evidence of a phone number only. `6.000` in Swiss Italian has no evidence for the thousands or
    the decimal reading, and `cardinal` does not choose one, so the span stays as written."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert say(text, tag, value) == normalize(text, tag)


NO_PLUS = [tag for tag in READ if code(tag) not in {"en", "pt", "de", "fr", "es", "it", "nl", "ru", "eu"}]
"""Tags with no sign word for `+`: the language files of these languages hold none, and no source for one is cited."""


@pytest.mark.parametrize("tag", NO_PLUS)
def test_a_country_code_reads_without_a_plus_that_the_language_has_no_word_for(caplog, tag):
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        spoken = say("+351 912 345 678", tag, "telephone")
    assert spoken == spelled(tag, "351912345678")
    records = [record for record in caplog.records if "+" in record.getMessage()]
    assert len(records) == 1 and records[0].levelno == logging.WARNING and "351" in records[0].getMessage()
    with pytest.raises(UnreadFormError):
        say("+351 912 345 678", tag, "telephone", NormalizationParams(strict=True))


NO_LETTER_NAMES = [tag for tag in READ if tag not in LETTER_NAMES]


@pytest.mark.parametrize("tag", NO_LETTER_NAMES)
@pytest.mark.parametrize("value", ["characters", "spell-out", "letters"])
@pytest.mark.parametrize("text,letters", [("NASA", "N A S A"), ("XK7", "X K 7"), ("ab", "a b")])
def test_characters_with_no_letter_names_read_each_letter_alone(tag, value, text, letters):
    """W3C Note, section 3.4: "the enclosed text should be spoken as a series of alpha-numeric characters". With no
    `letter_names` table each letter stays as written, alone, a digit reads by its cardinal, and the call warns."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        spoken = say(text, tag, value)
    expected = " ".join(digit_word(tag, char) if char.isdigit() else char for char in letters.split())
    assert spoken == expected
    honoured = [str(w.message) for w in caught if issubclass(w.category, ParameterNotHonouredWarning)]
    assert len(honoured) == 1 and "letter_names" in honoured[0]
    assert reads_again_the_same(spoken, tag)
    with pytest.raises(UnsupportedParameterError, match="letter_names"):
        say(text, tag, value, NormalizationParams(strict=True))


def test_a_letter_keeps_its_combining_marks():
    """A letter and the combining marks after it are one character: Devanagari `कि` is क and the vowel sign ि."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert say("कि2", "hi-IN", "characters") == f"कि {rbnf('hi-IN', 2, 'spellout-numbering')}"


@pytest.mark.parametrize("tag", sorted(ORDINALS))
@pytest.mark.parametrize("number", [1, 3, 21, 101])
def test_a_bare_ordinal_reads_through_the_ordinal_of_the_language(tag, number):
    """W3C Note, section 3.6: "the processor will produce the best representation of the ordinal that it can". A
    number that the rule set has no rule for, as 21 in RBNF `ta`, declines to the plain reading."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        spoken = say(str(number), tag, "ordinal")
    try:
        expected = " ".join(ORDINALS[tag](number).replace(",", " ").split())
    except NoRuleForNumberError:
        expected = normalize(str(number), tag)
    assert spoken == expected
    assert reads_again_the_same(spoken, tag)


@pytest.mark.parametrize("gender,rule_set", [(GrammaticalGender.FEMININE, "spellout-ordinal-feminine"),
                                              (GrammaticalGender.MASCULINE, "spellout-ordinal-masculine")])
def test_the_default_gender_chooses_the_rbnf_ordinal_rule_set(gender, rule_set):
    params = NormalizationParams(default_gender=FrozenMap({"hi": gender}))
    assert say("3", "hi-IN", "ordinal", params) == rbnf("hi-IN", 3, rule_set)


@pytest.mark.parametrize("tag", TAGS)
@pytest.mark.parametrize("digits", ["0", "999999999", "1" + "0" * 17, "12345678901234567890123", "9" * 30])
def test_a_say_as_ordinal_never_raises(tag, digits):
    """Section 17.6: with `strict=False` no say-as case raises. A writer that raises or gives digits for an ordinal
    declines, and the text reads as plain text."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        spoken = say(digits, tag, "ordinal")
    assert not any(char.isdigit() for char in spoken) or spoken == normalize(digits, tag)


DECLINES = [(tag, value) for value, tags in (("digits", NO_NUMBERS), ("telephone", NO_NUMBERS),
                                             ("characters", NO_NUMBERS), ("ordinal", NO_ORDINAL)) for tag in TAGS
            if tag in tags]


@pytest.mark.parametrize("tag,value", DECLINES, ids=[f"{tag}-{value}" for tag, value in DECLINES])
def test_a_language_with_no_reading_of_the_value_gives_the_plain_reading(tag, value):
    text = {"digits": "2024", "telephone": "912 345 678", "characters": "XK7", "ordinal": "3"}[value]
    with pytest.warns(ParameterNotHonouredWarning, match=value):
        assert say(text, tag, value) == normalize(text, tag)


def test_the_declining_languages_are_exactly_the_listed_ones():
    """Each tag outside the decline lists reads the value; the lists name every tag that does not."""
    texts = {"digits": "2024", "telephone": "912 345 678", "characters": "XK7", "ordinal": "3"}
    declining = set()
    for value, text in texts.items():
        for tag in TAGS:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                say(text, tag, value)
            if any(value in str(w.message) and "reads no say-as" in str(w.message) for w in caught):
                declining.add((tag, value))
    assert declining == set(DECLINES)
