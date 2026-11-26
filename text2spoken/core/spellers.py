"""Number spellers: one interface and three implementations (design section 5.4).

A speller holds no tag and no option. Each method takes the Request, so one speller serves every variety of
its file. A speller returns words separated by single spaces, with no space at either end.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from decimal import Decimal
from functools import cache, lru_cache
from importlib.resources import files
from typing import TYPE_CHECKING, Protocol

from text2spoken.core import parsers
from text2spoken.core.language import cldr_locale, rbnf_locales
from text2spoken.core.spans import Features
from text2spoken.errors import DeclinedReading
from text2spoken.params import GrammaticalGender

if TYPE_CHECKING:
    from unicode_rbnf import RbnfEngine

    from text2spoken.core.language import LanguageSpec, Request


def words(text: str) -> str:
    """Speller output as words separated by single spaces; a comma between words is written style, not a word."""
    return " ".join(text.replace(",", " ").split())


class NumberSpeller(Protocol):
    def cardinal(self, digits: str, features: Features, request: Request) -> str: ...
    def ordinal(self, digits: str, features: Features, request: Request) -> str: ...
    def year(self, digits: str, features: Features, request: Request) -> str: ...
    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str: ...
    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str: ...


SPELLER_METHODS = ("cardinal", "ordinal", "year", "decimal", "fraction")


DIGIT_BOUND = 308
"""The longest run of digits that a speller reads. A float holds an integer part of 308 digits, so the decimal path
reads no more. RBNF reads at most 17 digits in `en`, and ovos-number-parser names numbers up to 312 digits in `en`.
The bound is below 640, the lowest integer string limit that Python lets a process set, so `int()` reads every run
under the bound in every environment, and the output does not depend on `sys.int_max_str_digits`. Leading zeros do
not count: they are stripped before the check and before `int()`."""


def _significant(digits: str) -> str:
    """The digits with no leading zeros; a run of zeros keeps one, and an empty string stays empty."""
    return digits.lstrip("0") or digits[-1:]


def bounded_integer(digits: str) -> int | None:
    """The value of a run of digits, or None for a run of more than DIGIT_BOUND significant digits. An `int()` of a
    run from the input goes through this check, or reads a run that a pattern or a length test holds to a few
    digits, so its result does not depend on `sys.int_max_str_digits`. Text that is not digits raises."""
    significant = _significant(digits)
    return int(significant) if len(significant) <= DIGIT_BOUND else None


def _integer(digits: str) -> int:
    """The value of a run of digits; a run of more than DIGIT_BOUND significant digits declines."""
    value = bounded_integer(digits)
    if value is None:
        raise DeclinedReading(f"{len(_significant(digits))} digits pass the bound of {DIGIT_BOUND} digits that a "
                              "speller reads")
    return value


class OvosNumberSpeller:
    """ovos-number-parser, for a language and form where its output is right.

    The refusals of ovos-number-parser decline the span (design section 5.4): a language or a form that it does
    not read (`NotImplementedError`), a number too large for it (`OverflowError`) and an empty reading. A run past
    DIGIT_BOUND also declines, and so does a decimal that a float does not hold exactly, because ovos-number-parser
    reads a decimal from a float. Any other error raises."""

    def __init__(self, gender_arg: Mapping[GrammaticalGender, str]):
        self.gender_arg = dict(gender_arg)

    def _kwargs(self, features: Features, request: Request) -> dict:
        kwargs = {}
        if features.gender is not None:
            kwargs["gender"] = parsers.GrammaticalGender(self.gender_arg[features.gender])
        if request.params.scale is not None:
            kwargs["scale"] = parsers.Scale(request.params.scale)
        if features.case is not None:
            kwargs["case"] = features.case
        return kwargs

    @staticmethod
    def _read(form: str, size: str, request: Request, pronounce: Callable[[], str]) -> str:
        try:
            text = pronounce()
        except NotImplementedError as error:
            raise DeclinedReading(f"ovos-number-parser reads no {form} of {size} in {request.tag}: {error}") from error
        except OverflowError as error:
            raise DeclinedReading(f"ovos-number-parser reads no {form} of {size}: {error}") from error
        spoken = words(text) if text else ""
        if not spoken:
            raise DeclinedReading(f"ovos-number-parser gives an empty {form} of {size} in {request.tag}")
        return spoken

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        number, kwargs = _integer(digits), self._kwargs(features, request)
        return self._read("cardinal", f"{len(digits)} digits", request,
                          lambda: parsers.pronounce_number(number, request.tag, **kwargs))

    def negative_cardinal(self, digits: str, features: Features, request: Request) -> str:
        """The cardinal of minus the number. Zero declines, and so does a reading that has no word more than the
        reading of the number, because then the sign is not read."""
        number = _integer(digits)
        if number == 0:
            raise DeclinedReading("minus zero has no sign word")
        kwargs = self._kwargs(features, request)
        spoken = self._read("cardinal", f"-{len(digits)} digits", request,
                            lambda: parsers.pronounce_number(-number, request.tag, **kwargs))
        if len(spoken.split()) <= len(self.cardinal(digits, features, request).split()):
            raise DeclinedReading(f"ovos-number-parser reads no minus in {request.tag}")
        return spoken

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """The ordinal of the number. Three more refusals of the writer decline: a `ValueError`, which several writers
        raise for the ordinal of zero, as "Greek ordinals start at 1", a reading that holds a digit, which some
        writers return past a number of digits, and the cardinal of the number, as Turkish "iki yüz" for 200."""
        number, kwargs = _integer(digits), self._kwargs(features, request)
        try:
            spoken = self._read("ordinal", f"{len(digits)} digits", request,
                                lambda: parsers.pronounce_ordinal(number, request.tag, **kwargs))
        except DeclinedReading:
            raise
        except ValueError as error:
            raise DeclinedReading(f"ovos-number-parser reads no ordinal of {len(digits)} digits in {request.tag}: "
                                  f"{error}") from error
        if any(char.isdigit() for char in spoken):
            raise DeclinedReading(f"ovos-number-parser gives digits for the ordinal of {len(digits)} digits in "
                                  f"{request.tag}")
        if spoken == self.cardinal(digits, features, request):
            raise DeclinedReading(f"ovos-number-parser gives the cardinal for the ordinal of {len(digits)} digits in "
                                  f"{request.tag}")
        return spoken

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        value, kwargs = self._float(integer, fraction), self._kwargs(features, request)
        return self._read("decimal", f"{len(integer)}.{len(fraction)} digits", request,
                          lambda: parsers.pronounce_number(value, request.tag, places=len(fraction), **kwargs))

    def negative_decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimal of minus the number. A reading that has no word more than the reading of the number
        declines, because then the sign is not read."""
        value, kwargs = self._float(integer, fraction), self._kwargs(features, request)
        spoken = self._read("decimal", f"-{len(integer)}.{len(fraction)} digits", request,
                            lambda: parsers.pronounce_number(-value, request.tag, places=len(fraction), **kwargs))
        if len(spoken.split()) <= len(self.decimal(integer, fraction, features, request).split()):
            raise DeclinedReading(f"ovos-number-parser reads no minus in {request.tag}")
        return spoken

    @staticmethod
    def _float(integer: str, fraction: str) -> float:
        significant = len(_significant(integer))
        if significant > DIGIT_BOUND:
            raise DeclinedReading(f"{significant} integer digits pass the bound of {DIGIT_BOUND} digits that a "
                                  "speller reads")
        written = f"{integer or '0'}.{fraction}"
        value = float(written)
        # ovos-number-parser rounds a float through str(value), and its shared engine reads int(value) as the
        # integer part, so both must give the written number.
        if Decimal(str(value)) != Decimal(written) or int(value) != _integer(integer or "0"):
            raise DeclinedReading("ovos-number-parser reads a float, and no float holds the decimal of "
                                  f"{len(integer)}.{len(fraction)} digits exactly")
        return value

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        scale = parsers.Scale(request.params.scale) if request.params.scale is not None else None
        written = f"{_integer(numerator)}/{_integer(denominator)}"
        return self._read("fraction", f"{len(numerator)}/{len(denominator)} digits", request,
                          lambda: parsers.pronounce_fraction(written, request.tag, scale=scale))


class NumtagSpeller:
    """numtag.spell. A value that numtag refuses declines the span. `cases` names the cases that numtag inflects
    in the language; a speller with no cases passes no case."""

    def __init__(self, gender_arg: Mapping[GrammaticalGender, str], cases: tuple[str, ...] = ()):
        self.gender_arg = dict(gender_arg)
        self.cases = cases

    def spellings(self, value: str, features: Features, request: Request, form: str = "cardinal", **kwargs):
        """All the spellings of numtag, the standard one first."""
        from numtag import spell
        gender = self.gender_arg.get(features.gender)
        case = features.case if gender and features.case in self.cases else None
        try:
            return spell(value, request.tag, form=form, gender=gender, case=case, scale=request.params.scale,
                         **kwargs)
        except ValueError as error:
            raise DeclinedReading(f"numtag reads no {form} of {len(value)} characters in {request.tag}: "
                                  f"{error}") from error

    def _spell(self, value: str, features: Features, request: Request, form: str = "cardinal", **kwargs) -> str:
        return self.spellings(value, features, request, form, **kwargs)[0].text

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self._spell(str(_integer(digits)), features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._spell(str(_integer(digits)), features, request, "ordinal")

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimals as one number, with their written zeros: `1.80` reads eighty."""
        return self._spell(f"{_integer(integer or '0')}.{fraction}", features, request, decimals="number",
                           places=len(fraction))

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        return self._spell(f"{_integer(numerator)}/{_integer(denominator)}", features, request)


RBNF_HELD = frozenset({
    "da",  # "og" before the last part after tusind: 1001 reads "tusind en"; da.wikipedia writes "Tusind og en Nat"
    "sk",  # thousands 2000 to 2999: "dva tisíce", where Wiktionary writes "dvetisíc" and RBNF keeps "dve"
})
"""Languages with a writer of their own in ovos-number-parser that a language with no file still reads through
RBNF, because the writer reads a class of numbers worse than RBNF. The comment of each names the class. A language
leaves the set when text2spoken takes the floor of the parser release that fixes the class. Where RBNF reads a class
wrong too, the side with the narrower class wins: sl reads through the writer, which misreads 2000 to 2999, because
RBNF misreads every number from 21 to 99."""

RBNF_HELD_DECIMALS = frozenset({
    "ast",  # "un punto cinco"; Wiktionary, puntu (Asturian): "dot; full stop, period"; no ast RBNF, kept as written
    "az",  # "bir nöqtə beş"; Wiktionary, nöqtə: "period", "dot", "full stop"; az.xml x.x: ←← tam →→
    "cs",  # "jedna tečka pět"; Wiktionary, tečka: "period, full stop"; cs.xml x.x: ←← čárka →→
    "uk",  # "один крапка п'ять"; Wiktionary, крапка: "full stop, period"; uk.xml x.x: ←← кома →→
})
"""Writer languages whose writer says the decimal comma of CLDR 49 with the word for a full stop. Their decimals read
through the RBNF `x.x` rule, or stay as written with no RBNF locale, until the parser writes the comma word."""


@lru_cache(maxsize=None)
def rbnf_engine(locale: str) -> RbnfEngine:
    """The RBNF engine of a CLDR locale id; an engine with no rule sets is refused."""
    from unicode_rbnf import RbnfEngine

    engine = RbnfEngine.for_language(locale)
    if not engine.rulesets:
        raise LookupError(f"the RBNF locale {locale!r} has no rule sets")
    return engine


@cache
def rbnf_bound(locale: str, name: str) -> int | None:
    """The first number whose magnitude a rule set has no rule for, or None. RBNF reads past the last rule through
    that rule, and a quotient there reaches the radix: sr spellout-ordinal ends at 400 and reads 2000 двадесетстоти."""
    from unicode_rbnf.engine import SubRulePart, SubType

    rules = rbnf_engine(locale).rulesets[name].numeric_rules
    value = max(rules)
    last = rules[value]
    if not any(isinstance(part, SubRulePart) and part.type == SubType.QUOTIENT for part in last.parts):
        return None
    divisor = 1
    while divisor * last.radix <= value:
        divisor *= last.radix
    return divisor * last.radix


_WORD_BREAK = re.compile("([ \u00a0\u200b]+)")
"""A space, a no-break space, or a zero-width space, which the Lao rules of CLDR write between the parts of a
number."""


@cache
def rbnf_corrections() -> dict[str, dict[str, str]]:
    """The cited corrections of `data/rbnf_corrections.json`, by language: each wrong word of the CLDR RBNF data and
    its right word (design section 5.4). The core keeps every such correction in this one table, never in a language
    file. The dict is shared, so a caller does not change it."""
    table = json.loads((files("text2spoken") / "data" / "rbnf_corrections.json").read_text(encoding="utf-8"))
    by_language: dict[str, dict[str, str]] = {}
    for row in table["corrections"]:
        by_language.setdefault(row["language"], {})[row["wrong"]] = row["right"]
    return by_language


def corrected(text: str, locale: str) -> str:
    """RBNF output of a CLDR locale, with each word that `rbnf_corrections` holds for its language replaced."""
    table = rbnf_corrections().get(locale.split("_")[0])
    if not table:
        return text
    return "".join(table.get(part, part) for part in _WORD_BREAK.split(text))


class RbnfSpeller:
    """unicode_rbnf, with explicit rule set names. The output passes through `corrected`.

    It reads integers, and decimals when `decimal` names the rule set that holds the `x.x` rule. With no such rule
    set, a decimal raises NotImplementedError."""

    def __init__(self, cardinal: Mapping[Features, str], ordinal: Mapping[Features, str],
                 year: str = "spellout-numbering-year", decimal: str | None = None):
        for name, table in (("cardinal", cardinal), ("ordinal", ordinal)):
            if Features() not in table:
                raise ValueError(f"the {name} map of an RbnfSpeller needs an entry for Features()")
        self.cardinal_sets = dict(cardinal)
        self.ordinal_sets = dict(ordinal)
        self.year_set = year
        self.decimal_set = decimal

    @staticmethod
    def rule_set(table: Mapping[Features, str], features: Features) -> str:
        key = Features(gender=features.gender, animacy=features.animacy, case=features.case,
                       numeral_system=features.numeral_system)
        for drop in ("case", "animacy", "numeral_system"):
            if key in table:
                return table[key]
            key = replace(key, **{drop: None})
        return table.get(key, table[Features()])

    @staticmethod
    def locale(request: Request) -> str:
        locale = cldr_locale(request.tag, rbnf_locales(), request.language)
        if locale is None:
            raise LookupError(f"no RBNF locale for {request.tag!r}")
        return locale

    def _format(self, digits: str, name: str, request: Request, sign: int = 1) -> str:
        return self._spell(sign * _integer(digits), f"{len(digits)} digits", name, request)

    def _spell(self, number: int | Decimal, size: str, name: str, request: Request) -> str:
        from unicode_rbnf.engine import NoRuleForNumberError

        locale = self.locale(request)
        bound = rbnf_bound(locale, name)
        if bound is not None and abs(number) >= bound:
            raise DeclinedReading(f"{name} of {locale} has no rule for a number of {size}")
        try:
            result = rbnf_engine(locale).format_number(number, ruleset_names=[name])
        except (NoRuleForNumberError, ArithmeticError) as error:  # 2.5.1 raises decimal.InvalidOperation on a 30-digit ordinal
            raise DeclinedReading(f"no rule of {name} reads a number of {size}") from error
        text = result.text_by_ruleset[name]
        if any(char.isdigit() for char in text):  # unicode-rbnf 2.5.1 writes digits where no rule reads the number
            raise DeclinedReading(f"no rule of {name} reads a number of {size}")
        return words(corrected(text, locale))

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.rule_set(self.cardinal_sets, features), request)

    def negative_cardinal(self, digits: str, features: Features, request: Request) -> str:
        """The cardinal of minus the number, through the `-x` rule of the cardinal rule set, which places the sign
        word and its space. A rule set with no `-x` rule declines. Zero declines too, because RBNF reads `-0` as
        zero, with no sign word."""
        if _integer(digits) == 0:
            raise DeclinedReading("the -x rule of RBNF reads no minus zero")
        return self._format(digits, self.rule_set(self.cardinal_sets, features), request, sign=-1)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.rule_set(self.ordinal_sets, features), request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.year_set, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimal through the `x.x` rule of `decimal_set`, which writes the word of the decimal mark and the
        digits after it."""
        return self._decimal(integer, fraction, request, sign=1)

    def negative_decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimal of minus the number, through the `-x` rule that `decimal_set` finds and its `x.x` rule."""
        return self._decimal(integer, fraction, request, sign=-1)

    def _decimal(self, integer: str, fraction: str, request: Request, sign: int) -> str:
        """unicode_rbnf picks the `x.x` rule when the float of the number is more than DEFAULT_TOLERANCE from an
        integer, and else reads the integer alone. So a fraction of zeros, as in `3.0`, a fraction too small for
        the tolerance, and an integer part too long for a float to keep the fraction decline."""
        from unicode_rbnf.engine import DEFAULT_TOLERANCE

        if self.decimal_set is None:
            raise NotImplementedError("RbnfSpeller reads integers only")
        if len(fraction) > DIGIT_BOUND:
            raise DeclinedReading(f"{len(fraction)} fraction digits pass the bound of {DIGIT_BOUND} digits that a "
                                  "speller reads")
        value = Decimal(f"{_integer(integer or '0')}.{fraction}")
        if abs(float(value) - round(float(value))) <= DEFAULT_TOLERANCE:
            raise DeclinedReading(f"RBNF reads the decimal {len(integer)}.{len(fraction)} digits as an integer")
        return self._spell(sign * value, f"{len(integer)}.{len(fraction)} digits", self.decimal_set, request)

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        raise NotImplementedError("RbnfSpeller reads integers and decimals only")


#: The CLDR RBNF rule set that reads a plain cardinal: the first of these that the locale has.
CARDINAL_RULE_SETS = ("spellout-cardinal", "spellout-cardinal-masculine", "spellout-numbering")


@lru_cache(maxsize=128)
def cardinal_digit_words(tag: str, language: LanguageSpec) -> tuple[str, ...] | None:
    """The cardinal of each digit from 0 to 9 by the writer of ovos-number-parser for the language, else by the
    CLDR RBNF rule set `spellout-numbering`. UTS #35, Part 3, "Rule-Based Number Formatting", names that rule set
    "the default used when there is no context for the number. Usually this is used for counting without reference
    to a noun". Zero reads as the plain cardinal of the locale reads 0: the `zh` rule set `spellout-numbering` writes
    the digit sign 〇, and its cardinal writes the word 零. None when neither reads all ten, or a reading holds a
    digit."""
    if language.code in parsers.number_writer_languages():
        try:
            spoken = tuple(words(str(parsers.pronounce_number(digit, tag))) for digit in range(10))
        except (NotImplementedError, ValueError):
            return None
    else:
        locale = cldr_locale(tag, rbnf_locales(), language)
        engine = None if locale is None else rbnf_engine(locale)
        if engine is None or "spellout-numbering" not in engine.rulesets:
            return None
        cardinal = next(name for name in CARDINAL_RULE_SETS if name in engine.rulesets)
        spoken = tuple(words(corrected(engine.format_number(digit, ruleset_names=[rule_set])
                                       .text_by_ruleset[rule_set], locale))
                       for digit, rule_set in enumerate([cardinal, *["spellout-numbering"] * 9]))
    if not all(spoken) or any(char.isdigit() for word in spoken for char in word):
        return None
    return spoken


def spell_digits(digits: str, request: Request) -> str:
    """The digits one by one, by the `digit_words` of the language."""
    return DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)


class DigitSpeller:
    """One word per digit, from a table in the language file."""

    def __init__(self, digit_words: Sequence[str]):
        if len(digit_words) != 10:
            raise ValueError("a DigitSpeller needs one word for each of the ten digits")
        self.digit_words = tuple(digit_words)

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return " ".join(self.digit_words[int(d)] for d in digits)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        raise NotImplementedError("DigitSpeller reads digit strings only")

    def year(self, digits: str, features: Features, request: Request) -> str:
        raise NotImplementedError("DigitSpeller reads digit strings only")

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        raise NotImplementedError("DigitSpeller reads digit strings only")

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        raise NotImplementedError("DigitSpeller reads digit strings only")
