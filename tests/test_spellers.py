"""Spellers, CLDR locales and plural categories (design sections 5.3 and 5.4)."""
import json
import subprocess
import sys
from dataclasses import replace

import pytest

from text2spoken import DeclinedReading, Features, GrammaticalGender, NormalizationParams
from text2spoken.core.language import Request, Variety, plural_category
from text2spoken.core.spellers import (DigitSpeller, OvosNumberSpeller, RbnfSpeller, _integer, rbnf_engine,
                                       words)

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


def test_the_private_plural_locale_list_has_its_shape():
    from unicode_rbnf.plural_rules import PluralType, _load

    table = _load(PluralType.CARDINAL)
    assert isinstance(table, dict) and {"en", "pt", "pt_PT", "ru", "ar"} <= set(table)
