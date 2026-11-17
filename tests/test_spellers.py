"""Spellers, CLDR locales and plural categories (design sections 5.3 and 5.4)."""
import json
import logging
import re
import subprocess
import sys
from dataclasses import replace
from decimal import Decimal, localcontext

import pytest

from text2spoken import DeclinedReading, Features, GrammaticalGender, NormalizationParams, UnreadFormError, normalize
from text2spoken.core.language import Request, Variety, plural_category
from text2spoken.core.spellers import (DigitSpeller, OvosNumberSpeller, RbnfSpeller, _integer, corrected,
                                       rbnf_corrections, rbnf_engine, words)

F, M = GrammaticalGender.FEMININE, GrammaticalGender.MASCULINE
OVOS_GENDER = {M: "masculine", F: "feminine", GrammaticalGender.NEUTER: "neutral"}


def request(gendered, tag, **params):
    return Request(tag, Variety(tag), gendered.LANGUAGE, NormalizationParams(**params))


def test_ovos_speller_passes_the_tag_and_the_scale(gendered):
    # Portuguese: 10^9 is "mil milhões" on the long scale of pt-PT and "um bilhão" in pt-BR
    # (design section 5.4, Ciberdúvidas on the long and short scales).
    speller = OvosNumberSpeller(OVOS_GENDER)
    assert speller.cardinal("1000000000", Features(), request(gendered, "pt-PT")) == "mil milhões"
    assert speller.cardinal("1000000000", Features(), request(gendered, "pt-BR")) == "um bilhão"
    assert speller.cardinal("1000000000", Features(), request(gendered, "pt-PT", scale="short")) == "um bilião"


def test_ovos_speller_maps_the_gender(gendered):
    speller = OvosNumberSpeller(OVOS_GENDER)
    assert speller.cardinal("2", Features(gender=F), request(gendered, "pt-PT")) == "duas"
    assert speller.cardinal("2", Features(gender=M), request(gendered, "pt-PT")) == "dois"
    assert speller.ordinal("2", Features(gender=F), request(gendered, "pt-PT")) == "segunda"


def test_ovos_speller_passes_places_equal_to_the_written_digits(gendered):
    speller = OvosNumberSpeller(OVOS_GENDER)
    assert speller.decimal("1", "2345", Features(), request(gendered, "en")) == "one point two three four five"


def test_ovos_speller_reads_a_decimal_that_a_float_holds_exactly(gendered):
    """The integer part, the decimal word, then the fraction: Portuguese composes the digits after the leading zeros,
    and Spanish reads them one by one. Each expected value comes from ovos-number-parser on exact integers. A
    written trailing zero is not spoken, because a float does not hold it (design section 5.4). 16 digits that a
    float holds still read."""
    from ovos_number_parser import pronounce_number

    speller = OvosNumberSpeller(OVOS_GENDER)
    pt, es = request(gendered, "pt-PT"), request(gendered, "es-ES")
    assert speller.decimal("1", "05", Features(), pt) == "um vírgula zero cinco"
    assert speller.decimal("1", "05", Features(), es) == "uno coma cero cinco"
    assert speller.decimal("2", "50", Features(), pt) == "dois vírgula cinco"
    assert speller.decimal("2", "50", Features(), es) == "dos coma cinco"
    assert speller.decimal("0", "1", Features(), pt) == "zero vírgula um"
    assert speller.decimal("12345678901234", "56", Features(), pt) == (
        f"{pronounce_number(12345678901234, 'pt-PT')} vírgula cinquenta e seis")
    assert speller.decimal("12345678901234", "56", Features(), es) == (
        f"{pronounce_number(12345678901234, 'es-ES')} coma cinco seis")
    assert speller.decimal("0", "1234567890123456", Features(), pt) == (
        f"zero vírgula {pronounce_number(1234567890123456, 'pt-PT')}")
    assert speller.decimal("0", "000000000000000012", Features(), pt) == "zero vírgula " + "zero " * 16 + "doze"


@pytest.mark.parametrize("tag", ["pt-PT", "es-ES"])
@pytest.mark.parametrize(("integer", "fraction"), [
    ("123456789012345678", "5"),         # the float is 123456789012345680.0
    ("1", "1234567890123456789"),        # the float is 1.1234567890123457
    ("1", "000000000000000005"),         # the float is 1.0
    ("12345678901234567", "50"),         # the float is 12345678901234568.0
    ("9007199254740993", "5"),           # the float is 9007199254740994.0
    ("100000000000000000000000", "0"),   # the float prints as 1e+23, and its integer part is 99999999999999991611392
    ("1", "9" * 400),                    # the float is 2.0
])
def test_ovos_speller_declines_a_decimal_that_no_float_holds(gendered, tag, integer, fraction):
    """ovos-number-parser reads a float. A decimal that no float holds declines: the float gives other digits,
    drops the fraction or changes the integer part, and the parser gives no error."""
    with pytest.raises(DeclinedReading, match=f"no float holds the decimal of {len(integer)}.{len(fraction)} "
                                              "digits exactly"):
        OvosNumberSpeller(OVOS_GENDER).decimal(integer, fraction, Features(), request(gendered, tag))


def test_ovos_speller_declines_a_language_it_does_not_read(gendered):
    # ovos-number-parser raises NotImplementedError for a language that it does not read.
    with pytest.raises(DeclinedReading, match="reads no cardinal of 1 digits in qaa") as declined:
        OvosNumberSpeller(OVOS_GENDER).cardinal("7", Features(), request(gendered, "qaa"))
    assert type(declined.value.__cause__) is NotImplementedError


def test_ovos_speller_declines_a_number_too_large_to_read(gendered, monkeypatch):
    """A run past the digit bound, an integer part past it, which ovos-number-parser reads as "infinity" past 308
    digits, and an OverflowError of the library, as for a Kabyle number past 9999."""
    import ovos_number_parser

    speller, en = OvosNumberSpeller(OVOS_GENDER), request(gendered, "en")
    with pytest.raises(DeclinedReading, match="4301 digits pass the bound of 308 digits"):
        speller.cardinal("9" * 4301, Features(), en)
    with pytest.raises(DeclinedReading, match="400 integer digits pass the bound of 308 digits"):
        speller.decimal("9" * 400, "5", Features(), en)

    def overflow(number, lang, **kwargs):
        raise OverflowError("Kabyle pronunciation is supported up to 9999")

    monkeypatch.setattr(ovos_number_parser, "pronounce_number", overflow)
    with pytest.raises(DeclinedReading, match="up to 9999") as declined:
        speller.cardinal("10000", Features(), request(gendered, "kab"))
    assert type(declined.value.__cause__) is OverflowError


LONG_RUN_PROBE = """
from text2spoken import DeclinedReading, Features, NormalizationParams
from text2spoken.core.language import Request, Variety
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller
from text2spoken.lang.en import LANGUAGE

request = Request(tag="en", variety=Variety("en"), language=LANGUAGE, params=NormalizationParams())
rbnf = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})
for speller in (OvosNumberSpeller({}), rbnf):
    try:
        print(speller.cardinal("9" * 4301, Features(), request))
    except DeclinedReading as error:
        print("declined:", error)
"""


def test_a_long_run_reads_the_same_whatever_the_integer_string_limit_of_python():
    """The design forbids output that depends on the environment. `-X int_max_str_digits=0` lifts the limit of
    `int()`, and the run of 4301 digits must still decline in both spellers, with the same reason."""
    runs = [subprocess.run([sys.executable, *flags, "-c", LONG_RUN_PROBE], capture_output=True, text=True,
                           check=True).stdout for flags in ([], ["-X", "int_max_str_digits=0"])]
    assert runs[0] == runs[1] == "declined: 4301 digits pass the bound of 308 digits that a speller reads\n" * 2


LONG_DECIMAL_PROBE = """
from text2spoken import DeclinedReading, Features, NormalizationParams
from text2spoken.core.language import Request, Variety
from text2spoken.core.spellers import OvosNumberSpeller
from text2spoken.lang.en import LANGUAGE

request = Request(tag="pt-PT", variety=Variety("pt-PT"), language=LANGUAGE, params=NormalizationParams())
for integer, fraction in (("9" * 4301, "5"), ("9" * 309, "5"), ("9" * 308, "5"), ("1", "9" * 5000), ("2", "5")):
    try:
        print(OvosNumberSpeller({}).decimal(integer, fraction, Features(), request))
    except DeclinedReading as error:
        print("declined:", error)
"""


def test_a_long_decimal_reads_the_same_whatever_the_integer_string_limit_of_python():
    """An integer part past the digit bound declines before `int()`, and a decimal that no float holds declines,
    under the default limit of `int()`, the lowest limit Python allows and no limit."""
    runs = [subprocess.run([sys.executable, *flags, "-c", LONG_DECIMAL_PROBE], capture_output=True, text=True,
                           check=True).stdout
            for flags in ([], ["-X", "int_max_str_digits=640"], ["-X", "int_max_str_digits=0"])]
    no_float = "declined: ovos-number-parser reads a float, and no float holds the decimal of {} digits exactly\n"
    assert runs[0] == runs[1] == runs[2] == "".join([
        "declined: 4301 integer digits pass the bound of 308 digits that a speller reads\n",
        "declined: 309 integer digits pass the bound of 308 digits that a speller reads\n",
        no_float.format("308.1"), no_float.format("1.5000"), "dois vírgula cinco\n"])


LEADING_ZEROS_PROBE = """
import json, logging
logging.disable(logging.CRITICAL)
from text2spoken import normalize

Z = "0" * 320
texts = [f"It is {Z}1.5 now.", f"Pay ${Z}5 now.", f"It is {Z}1/2 now.", f"the {Z}1st one", f"{Z}10%", f"{Z}5 km"]
print(json.dumps([normalize(text, tag) for tag in ("en-GB", "en-US") for text in texts]))
"""


def test_leading_zeros_do_not_count_against_the_digit_bound_under_any_integer_limit():
    """320 leading zeros do not make a number long: each text reads as it did before the bound, and the same under
    the default limit of `int()`, the lowest limit Python allows and no limit."""
    expected = ["It is one point five now.", "Pay five dollars now.", "It is one-half now.", "the first one",
                "ten per cent", "five kilometres",
                "It is one point five now.", "Pay five dollars now.", "It is one-half now.", "the first one",
                "ten percent", "five kilometers"]
    for flags in ([], ["-X", "int_max_str_digits=640"], ["-X", "int_max_str_digits=0"]):
        run = subprocess.run([sys.executable, *flags, "-c", LEADING_ZEROS_PROBE], capture_output=True, text=True,
                             check=True)
        assert json.loads(run.stdout) == expected, flags


LONG_RUN_IN_RECOGNIZERS_PROBE = """
import json, logging
from text2spoken import normalize

warnings = []
handler = logging.Handler(logging.WARNING)
handler.emit = lambda record: warnings.append(record.getMessage().split(" '")[0])
logging.getLogger("text2spoken").addHandler(handler)
logging.getLogger("text2spoken").propagate = False
N, O, Z = "9" * 4400, "1" * 4400, "0" * 4400
long_runs = [f"the {N}th one", f"the 1,{N}th one", f"the {N}th of May", f"take 1/{N} now", f"take {N}/2 now",
             f"take {O}/{N} now", f"pages 1-{N} now", f"pages {N}-5 now", f"pages {O}-{N} now",
             f"pages {N}-{O} now", f"5-{N} km"]
zeros = [f"It is {Z}1/2 now.", f"It is 1/{Z}2 now.", f"Pay ${Z}5.50 now.", f"Pay ${Z}0.50 now.", f"the {Z}11th hour",
         f"pages {Z}1-{Z}5 now", f"{Z}5-{Z}9 km", f"{Z}10%"]
runs = {}
for tag in ("en-GB", "en-US"):
    for text in long_runs:
        warnings.clear()
        runs.setdefault("long", []).append([normalize(text, tag) == text, warnings[:]])
    runs.setdefault("zeros", []).extend(normalize(text, tag) for text in zeros)
print(json.dumps(runs))
"""

UNREAD_WRITTEN, UNREAD_ORDINAL = ["unread written form"], ["unread ordinal span"]
UNREAD_RANGE, UNREAD_MEASURE = ["unread range span"], ["unread measure span"]


def test_a_long_run_in_a_recognizer_stays_as_written_under_any_integer_limit():
    """The ordinal, fraction and range recognizers compare the numbers they find, and the speller compares them
    again. A run of 4400 digits passes the default limit of `int()`, so a raw `int()` raised before the speller
    bound. The output is the same under the default limit, the lowest limit Python allows and no limit.

    A long run stays as written with one WARNING. A span that a recognizer claims declines in the speller; a run
    that no recognizer claims stays unread. Two runs past the bound do not count as a descending range, so that
    range is read and declines. Leading zeros do not change a value, so a run of 4400 zeros before a short number
    reads as that number."""
    runs = []
    for flags in ([], ["-X", "int_max_str_digits=640"], ["-X", "int_max_str_digits=0"]):
        run = subprocess.run([sys.executable, *flags, "-c", LONG_RUN_IN_RECOGNIZERS_PROBE], capture_output=True,
                             text=True)
        assert run.returncode == 0, (flags, run.stderr[-300:])
        runs.append(json.loads(run.stdout))
    assert runs[0] == runs[1] == runs[2]
    warnings = [UNREAD_ORDINAL, UNREAD_WRITTEN, UNREAD_ORDINAL, UNREAD_WRITTEN, UNREAD_WRITTEN, UNREAD_WRITTEN,
                UNREAD_RANGE, UNREAD_WRITTEN, UNREAD_RANGE, UNREAD_RANGE, UNREAD_MEASURE]
    assert runs[0]["long"] == [[True, kind] for kind in warnings * 2]
    readings = ["It is one-half now.", "It is one-half now.", "Pay five dollars and fifty cents now.",
                "Pay fifty cents now.", "the eleventh hour", "pages one to five now"]
    assert runs[0]["zeros"] == [*readings, "five to nine kilometres", "ten per cent",
                                *readings, "five to nine kilometers", "ten percent"]


def test_the_digit_bound_reads_308_digits_and_declines_309(gendered):
    en = request(gendered, "en")
    ovos = OvosNumberSpeller(OVOS_GENDER)
    rbnf = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})
    assert ovos.cardinal("9" * 308, Features(), en).endswith("nine hundred and ninety nine")
    for speller in (ovos, rbnf):
        with pytest.raises(DeclinedReading, match="^309 digits pass the bound of 308 digits that a speller reads$"):
            speller.cardinal("9" * 309, Features(), en)


@pytest.mark.parametrize("written", ["1,000", "", "12a"])
def test_text_that_is_not_digits_raises_and_does_not_decline(gendered, written):
    """Only a run past the digit bound declines. A ValueError of `int()` for text that is not digits is a defect of
    the caller, so it raises."""
    rbnf = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})
    for read in (_integer, lambda digits: rbnf.cardinal(digits, Features(), request(gendered, "en"))):
        with pytest.raises(ValueError) as raised:
            read(written)
        assert not isinstance(raised.value, DeclinedReading)


@pytest.mark.parametrize("reading", ["", 0, " , "])
def test_ovos_speller_declines_an_empty_reading(gendered, monkeypatch, reading):
    # The ordinal of 0 is "" in sl and the integer 0 in et.
    import ovos_number_parser

    monkeypatch.setattr(ovos_number_parser, "pronounce_ordinal", lambda number, lang, **kwargs: reading)
    with pytest.raises(DeclinedReading, match="empty ordinal of 1 digits in sl"):
        OvosNumberSpeller(OVOS_GENDER).ordinal("0", Features(), request(gendered, "sl"))


@pytest.mark.parametrize("error", [ValueError("Greek ordinals start at 1"), KeyError(2000000)])
def test_ovos_speller_raises_any_other_error_of_the_library(gendered, monkeypatch, error):
    import ovos_number_parser

    def fail(number, lang, **kwargs):
        raise error

    monkeypatch.setattr(ovos_number_parser, "pronounce_ordinal", fail)
    with pytest.raises(type(error)):
        OvosNumberSpeller(OVOS_GENDER).ordinal("0", Features(), request(gendered, "el"))


def test_rbnf_speller_falls_back_case_then_animacy_then_numeral_system_then_bare(gendered):
    table = {Features(): "a", Features(gender=F): "f", Features(gender=F, case="genitive"): "fg",
             Features(gender=F, animacy="animate"): "fa"}
    pick = RbnfSpeller.rule_set
    assert pick(table, Features(gender=F, case="genitive")) == "fg"
    assert pick(table, Features(gender=F, case="dative")) == "f"
    assert pick(table, Features(gender=F, case="dative", animacy="animate")) == "fa"
    assert pick(table, Features(gender=F, numeral_system="native")) == "f"
    assert pick(table, Features(gender=M, case="genitive")) == "a"
    assert pick(table, Features(gender=F, number="plural", definite=True)) == "f"


def test_rbnf_speller_reads_the_named_rule_set(gendered):
    # Russian: одна (feminine one), двух (genitive two), вторая (feminine second); German: eine, ein.
    ru = replace(gendered.LANGUAGE, code="ru")
    speller = RbnfSpeller(cardinal={Features(): "spellout-cardinal-masculine",
                                    Features(gender=F): "spellout-cardinal-feminine",
                                    Features(gender=F, case="genitive"): "spellout-cardinal-feminine-genitive"},
                          ordinal={Features(): "spellout-ordinal-masculine",
                                   Features(gender=F): "spellout-ordinal-feminine"})
    r = Request("ru-RU", Variety("ru-RU"), ru, NormalizationParams())
    assert speller.cardinal("1", Features(gender=F), r) == "одна"
    assert speller.cardinal("2", Features(gender=F, case="genitive"), r) == "двух"
    assert speller.ordinal("2", Features(gender=F), r) == "вторая"
    assert speller.cardinal("1", Features(), r) == "один"


def test_rbnf_speller_reads_integers_only(gendered):
    speller = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})
    with pytest.raises(NotImplementedError):
        speller.decimal("2", "5", Features(), request(gendered, "en"))
    with pytest.raises(NotImplementedError):
        speller.fraction("1", "2", Features(), request(gendered, "en"))
    with pytest.raises(ValueError):
        RbnfSpeller(cardinal={Features(gender=F): "x"}, ordinal={Features(): "y"})


def test_an_rbnf_engine_with_no_rule_sets_is_refused(monkeypatch):
    class Empty:
        rulesets = {}

    import unicode_rbnf

    rbnf_engine.cache_clear()
    monkeypatch.setattr(unicode_rbnf.RbnfEngine, "for_language", staticmethod(lambda locale: Empty()))
    with pytest.raises(LookupError):
        rbnf_engine("nb")
    rbnf_engine.cache_clear()


def test_digit_speller(gendered):
    speller = DigitSpeller(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])
    assert speller.cardinal("2079", Features(), request(gendered, "en")) == "two zero seven nine"
    with pytest.raises(ValueError):
        DigitSpeller(["zero"])


def test_speller_output_has_single_spaces_and_no_commas():
    assert words(" eine  Milliarde ") == "eine Milliarde"
    assert words("one million, two hundred") == "one million two hundred"


# CLDR plural rules, read by hand from the CLDR "Language Plural Rules" chart:
# en one: i = 1 and v = 0. pt one: i = 0..1. pt_PT one: i = 1 and v = 0. many (pt, pt_PT): e = 0 and i != 0
# and i % 1000000 = 0 and v = 0. ru one: v = 0 and i % 10 = 1 and i % 100 != 11; few: i % 10 = 2..4 ...;
# many: v = 0 and i % 10 = 0 or 5..9 ...; ar zero n = 0, two n = 2, few n % 100 = 3..10, many n % 100 = 11..99.
PLURAL_ROWS = [
    ("ru", "1", "one"), ("ru", "3", "few"), ("ru", "5", "many"), ("ru", "1.5", "other"),
    ("ar", "0", "zero"), ("ar", "2", "two"), ("ar", "5", "few"), ("ar", "11", "many"), ("ar", "100", "other"),
    ("pt-BR", "0", "one"), ("pt-BR", "1.5", "one"), ("pt-BR", "2", "other"), ("pt-BR", "1000000", "many"),
    ("pt-PT", "0", "other"), ("pt-PT", "1", "one"), ("pt-PT", "1.5", "other"), ("pt-PT", "1000000", "many"),
    ("en", "1", "one"), ("en", "1.0", "other"), ("en", "2", "other"),
]


@pytest.mark.parametrize("tag,written,category", PLURAL_ROWS)
def test_plural_category(gendered, tag, written, category):
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    assert plural_category(Request(tag, Variety(tag), language, NormalizationParams()), written) == category


def test_plural_category_refuses_a_locale_with_no_rules(gendered):
    language = replace(gendered.LANGUAGE, code="tlh", cldr_aliases=())
    with pytest.raises(LookupError):
        plural_category(Request("tlh", Variety("tlh"), language, NormalizationParams()), "1")


# CLDR 49, common/supplemental/plurals.xml, read by hand:
#   es        one:  n = 1
#   fr pt     one:  i = 0..1
#   pt_PT     one:  i = 1 and v = 0
#   es, pt, pt_PT  many: e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5
#   ru uk     one:  v = 0 and i % 10 = 1 and i % 100 != 11
#             few:  v = 0 and i % 10 = 2..4 and i % 100 != 12..14
#             many: v = 0 and i % 10 = 0 or v = 0 and i % 10 = 5..9 or v = 0 and i % 100 = 11..14
def cldr_integer_category(code: str, i: int) -> str:
    """The category of a written integer above 1 (v = 0, e = 0) by the rules above, in Python int arithmetic."""
    if code == "ru":
        if i % 10 == 1 and i % 100 != 11:
            return "one"
        if 2 <= i % 10 <= 4 and not 12 <= i % 100 <= 14:
            return "few"
        return "many" if i % 10 == 0 or 5 <= i % 10 <= 9 or 11 <= i % 100 <= 14 else "other"
    return "many" if i % 1000000 == 0 else "other"


LARGE_INTEGERS = [10**28, 10**28 + 1, 10**29, 10**29 + 1, 10**29 + 2, 10**29 + 11, 10**34, 10**34 + 1,
                  int("1" * 400)]


@pytest.mark.parametrize("tag", ["es", "pt-BR", "pt-PT", "ru"])
@pytest.mark.parametrize("number", LARGE_INTEGERS, ids=lambda number: f"{len(str(number))}digits-{number % 100}")
def test_the_plural_category_of_a_large_integer_is_exact(gendered, tag, number):
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    category = plural_category(Request(tag, Variety(tag), language, NormalizationParams()), str(number))
    assert category == cldr_integer_category(tag.split("-")[0], number)


@pytest.mark.parametrize("tag", ["es", "pt-BR", "pt-PT"])
def test_one_more_than_ten_to_the_twenty_eight_is_other(gendered, tag):
    # (10**28 + 1) % 1000000 == 1, so many fails; n and i are not 1 or 0..1, so one fails.
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    assert plural_category(Request(tag, Variety(tag), language, NormalizationParams()), str(10**28 + 1)) == "other"


@pytest.mark.parametrize("tag", ["es", "pt-BR", "pt-PT", "ru"])
def test_a_long_decimal_keeps_its_visible_fraction(gendered, tag):
    # v = 1, so neither many nor any ru category applies; n and i are far from 1.
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    written = "1" + "0" * 30 + ".5"
    assert plural_category(Request(tag, Variety(tag), language, NormalizationParams()), written) == "other"


def test_the_plural_category_is_exact_under_a_caller_context_of_low_precision(gendered):
    # ru 1000001: i % 10 = 1 and i % 100 = 1, so one.
    language = replace(gendered.LANGUAGE, code="ru", cldr_aliases=())
    with localcontext(prec=6) as caller:
        assert plural_category(Request("ru", Variety("ru"), language, NormalizationParams()), "1000001") == "one"
        assert caller.prec == 6


@pytest.mark.parametrize(("tag", "text", "form"), [
    ("en-GB", "It is 1.{} km.", "measure"),
    ("en-GB", "It costs £1.{}.", "money"),
    ("de-DE", "Es sind 1,{} km.", "measure"),
    ("pt-PT", "Mede 1,{} km.", "measure"),
])
def test_a_fraction_past_the_int_string_limit_keeps_the_written_form(tag, text, form, caplog):
    """unicode_rbnf converts the fraction digits to an `int`, and Python converts no string longer than
    `sys.get_int_max_str_digits()`, 4300 by default. The plural category declines, so the span stays as written with
    one warning, and strict mode raises `UnreadFormError` (design section 10)."""
    limit = sys.get_int_max_str_digits()
    text = text.format("1" * (limit + 1))
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(text, tag) == text
    [warning] = [record.getMessage() for record in caplog.records if record.getMessage().startswith(f"unread {form} ")]
    assert warning.endswith(f": a number of 1 integer and {limit + 1} fraction digits passes the int string limit of "
                            f"{limit} digits, so it has no plural category")
    with pytest.raises(UnreadFormError) as raised:
        normalize(text, tag, NormalizationParams(strict=True))
    assert type(raised.value.__cause__) is DeclinedReading


@pytest.mark.parametrize("tag", ["en", "de", "pt-PT", "ru"])
def test_a_number_at_the_int_string_limit_has_a_plural_category(gendered, tag):
    # en, de, pt_PT one: i = 1 and v = 0; every ru category above needs v = 0. So a decimal of v > 0 is other.
    limit = sys.get_int_max_str_digits()
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    request = Request(tag, Variety(tag), language, NormalizationParams())
    assert plural_category(request, "1." + "1" * limit) == "other"
    for written in ("1." + "1" * (limit + 1), "1" * (limit + 1), "1" * (limit + 1) + ".5"):
        with pytest.raises(DeclinedReading):
            plural_category(request, written)


def test_a_fraction_at_the_int_string_limit_reads():
    limit = sys.get_int_max_str_digits()
    text = normalize("It is 1." + "1" * limit + " km.", "en-GB")
    assert text == "It is one point" + " one" * limit + " kilometres."


INT_LIMIT_PROBE = """
from text2spoken import DeclinedReading, NormalizationParams
from text2spoken.core.language import Request, Variety, plural_category
from text2spoken.lang.en import LANGUAGE

request = Request(tag="en", variety=Variety("en"), language=LANGUAGE, params=NormalizationParams())
for digits in (640, 641, 4301):
    try:
        print(plural_category(request, "1." + "1" * digits))
    except DeclinedReading:
        print("declined")
"""


def test_the_plural_category_reads_the_int_string_limit_at_call_time():
    """The lowest limit Python allows, 640, declines a fraction of 641 digits. A limit of 0 is no limit."""
    runs = [subprocess.run([sys.executable, *flags, "-c", INT_LIMIT_PROBE], capture_output=True, text=True,
                           check=True).stdout for flags in (["-X", "int_max_str_digits=640"],
                                                            ["-X", "int_max_str_digits=0"])]
    assert runs == ["other\ndeclined\ndeclined\n", "other\nother\nother\n"]


def test_the_private_plural_locale_list_has_its_shape():
    from unicode_rbnf.plural_rules import PluralType, _eval_condition, _load

    table = _load(PluralType.CARDINAL)
    assert isinstance(table, dict) and {"en", "pt", "pt_PT", "ru", "ar"} <= set(table)
    assert ("one", "i = 1 and v = 0") in table["en"]
    operands = {name: Decimal(0) for name in "ivwftce"}
    assert _eval_condition("i = 1 and v = 0", {**operands, "n": Decimal(1), "i": Decimal(1)})
    assert not _eval_condition("i = 1 and v = 0", {**operands, "n": Decimal("1.0"), "i": Decimal(1), "v": Decimal(1)})


# The CLDR 49 rules of plurals.xml, applied by hand. The visible fraction digits give v, so v > 0 for each number.
# en, de, pt_PT: one is i = 1 and v = 0, so other. ru: one, few and many need v = 0, so other. pt: one is i = 0..1,
# and i = 0, so one. ar: each rule reads n, and n is no integer, so other.
SMALL_DECIMALS = [("en", "0.00000010", "other"), ("de", "0.0000001", "other"), ("pt-PT", "0.0000001", "other"),
                  ("pt-BR", "0.00000010", "one"), ("ru", "0.0000001", "other"), ("ru", "0.00000010", "other"),
                  ("ar", "0.0000001", "other"), ("ru", "0." + "0" * 30 + "1", "other")]


@pytest.mark.parametrize(("tag", "written", "category"), SMALL_DECIMALS)
def test_a_decimal_with_more_than_six_zeros_after_the_point_has_its_plural_category(gendered, tag, written, category):
    """`str(Decimal)` writes such a number with an exponent, as `1E-7`, so the operands read the fixed-point form."""
    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    assert plural_category(Request(tag, Variety(tag), language, NormalizationParams()), written) == category


@pytest.mark.parametrize("tag", ["en", "de", "pt-PT", "pt-BR", "ru", "ar"])
def test_the_plural_category_agrees_with_unicode_rbnf_where_it_reads_no_exponent(gendered, tag):
    from unicode_rbnf.plural_rules import get_plural_category

    language = replace(gendered.LANGUAGE, code=tag.split("-")[0], cldr_aliases=())
    request = Request(tag, Variety(tag), language, NormalizationParams())
    locale = {"pt-PT": "pt_PT", "pt-BR": "pt"}.get(tag, tag)
    for written in ("0", "1", "1.0", "2", "3", "5", "11", "12", "21", "22", "25", "101", "111", "0.5", "1.5", "2.50",
                    "10.0", "100", "1000000", "2000000", "0.000001", "0.0000010", "12.345", "1" + "0" * 27 + "1"):
        with localcontext(prec=40):
            expected = get_plural_category(locale, Decimal(written))
        assert plural_category(request, written) == expected, written


def test_each_rbnf_correction_names_a_word_that_the_rbnf_data_writes():
    """A release of unicode-rbnf that fixes a word of `data/rbnf_corrections.json` fails here, so the row goes."""
    numbers = (0, 13, 90, 100, 1000, 3000, 10_000, 100_000, 10**6, -5)
    for language, table in rbnf_corrections().items():
        engine = rbnf_engine(language)
        written = set()
        for name in engine.rulesets:
            for number in numbers:
                try:
                    text = engine.format_number(number, ruleset_names=[name]).text_by_ruleset[name]
                except Exception:  # a private or a numbering rule set may refuse a number; others still read it
                    continue
                written.update(re.split("[ \u00a0\u200b]+", text))
        assert set(table) <= written, (language, sorted(set(table) - written))


def test_a_correction_replaces_whole_words_only():
    assert corrected("ໜຶ່ງ\u200bร้อย ร้อยx", "lo") == "ໜຶ່ງ\u200bຮ້ອຍ ร้อยx"
    assert corrected("τρεις χίλιάδες", "el_GR") == "τρεις χιλιάδες"
    assert corrected("ร้อย", "th") == "ร้อย"

