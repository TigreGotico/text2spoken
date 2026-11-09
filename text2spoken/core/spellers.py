"""Number spellers: one interface and three implementations (design section 5.4).

A speller holds no tag and no option. Each method takes the Request, so one speller serves every variety of
its file. A speller returns words separated by single spaces, with no space at either end.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from functools import lru_cache
from typing import TYPE_CHECKING, Protocol

from text2spoken.core.language import cldr_locale, rbnf_locales
from text2spoken.core.spans import Features
from text2spoken.errors import DeclinedReading
from text2spoken.params import GrammaticalGender

if TYPE_CHECKING:
    from unicode_rbnf import RbnfEngine

    from text2spoken.core.language import Request


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


def _integer(digits: str) -> int:
    try:
        return int(digits)
    except ValueError as error:
        raise DeclinedReading(f"{len(digits)} digits pass the integer string limit of Python") from error


class OvosNumberSpeller:
    """ovos-number-parser, for a language and form where its output is right.

    The refusals of ovos-number-parser decline the span (design section 5.4): a language or a form that it does
    not read (`NotImplementedError`), a number too large for it (`OverflowError`) and an empty reading. A number
    that Python cannot convert, as an integer or as a finite float, also declines. Any other error raises."""

    def __init__(self, gender_arg: Mapping[GrammaticalGender, str]):
        self.gender_arg = dict(gender_arg)

    def _kwargs(self, features: Features, request: Request) -> dict:
        from ovos_number_parser.util import GrammaticalGender as OvosGender, Scale

        kwargs = {}
        if features.gender is not None:
            kwargs["gender"] = OvosGender(self.gender_arg[features.gender])
        if request.params.scale is not None:
            kwargs["scale"] = Scale(request.params.scale)
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
        from ovos_number_parser import pronounce_number

        number, kwargs = _integer(digits), self._kwargs(features, request)
        return self._read("cardinal", f"{len(digits)} digits", request,
                          lambda: pronounce_number(number, request.tag, **kwargs))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        from ovos_number_parser import pronounce_ordinal

        number, kwargs = _integer(digits), self._kwargs(features, request)
        return self._read("ordinal", f"{len(digits)} digits", request,
                          lambda: pronounce_ordinal(number, request.tag, **kwargs))

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        from ovos_number_parser import pronounce_number

        value = float(f"{integer or '0'}.{fraction}")
        if math.isinf(value):
            raise DeclinedReading(f"{len(integer)} integer digits pass the range of a float")
        kwargs = self._kwargs(features, request)
        return self._read("decimal", f"{len(integer)}.{len(fraction)} digits", request,
                          lambda: pronounce_number(value, request.tag, places=len(fraction), **kwargs))

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        from ovos_number_parser import pronounce_fraction
        from ovos_number_parser.util import Scale

        scale = Scale(request.params.scale) if request.params.scale is not None else None
        written = f"{_integer(numerator)}/{_integer(denominator)}"
        return self._read("fraction", f"{len(numerator)}/{len(denominator)} digits", request,
                          lambda: pronounce_fraction(written, request.tag, scale=scale))


def _rbnf_key(features: Features) -> Features:
    return Features(gender=features.gender, animacy=features.animacy, case=features.case,
                    numeral_system=features.numeral_system)


@lru_cache(maxsize=None)
def rbnf_engine(locale: str) -> RbnfEngine:
    """The RBNF engine of a CLDR locale id; an engine with no rule sets is refused."""
    from unicode_rbnf import RbnfEngine

    engine = RbnfEngine.for_language(locale)
    if not engine.rulesets:
        raise LookupError(f"the RBNF locale {locale!r} has no rule sets")
    return engine


class RbnfSpeller:
    """unicode_rbnf, with explicit rule set names; integers only."""

    def __init__(self, cardinal: Mapping[Features, str], ordinal: Mapping[Features, str],
                 year: str = "spellout-numbering-year"):
        for name, table in (("cardinal", cardinal), ("ordinal", ordinal)):
            if Features() not in table:
                raise ValueError(f"the {name} map of an RbnfSpeller needs an entry for Features()")
        self.cardinal_sets = dict(cardinal)
        self.ordinal_sets = dict(ordinal)
        self.year_set = year

    @staticmethod
    def rule_set(table: Mapping[Features, str], features: Features) -> str:
        key = _rbnf_key(features)
        for drop in ("case", "animacy", "numeral_system"):
            if key in table:
                return table[key]
            key = replace(key, **{drop: None})
        return table.get(key, table[Features()])

    @staticmethod
    def engine(request: Request) -> RbnfEngine:
        locale = cldr_locale(request.tag, rbnf_locales(), request.language)
        if locale is None:
            raise LookupError(f"no RBNF locale for {request.tag!r}")
        return rbnf_engine(locale)

    def _format(self, digits: str, name: str, request: Request) -> str:
        from unicode_rbnf.engine import NoRuleForNumberError

        try:
            number = int(digits)
        except ValueError as error:
            raise DeclinedReading(f"{len(digits)} digits pass the integer string limit of Python") from error
        try:
            result = self.engine(request).format_number(number, ruleset_names=[name])
        except (NoRuleForNumberError, OverflowError) as error:
            raise DeclinedReading(f"no rule of {name} reads a number of {len(digits)} digits") from error
        return words(result.text_by_ruleset[name])

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.rule_set(self.cardinal_sets, features), request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.rule_set(self.ordinal_sets, features), request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self._format(digits, self.year_set, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        raise NotImplementedError("RbnfSpeller reads integers only")

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        raise NotImplementedError("RbnfSpeller reads integers only")


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
