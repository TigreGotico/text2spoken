"""Say-as: the form that the caller names for one run of text (design section 17).

SSML lets an author name the form of a run: `<say-as interpret-as="ordinal">3</say-as>`. The markup is the evidence
that a recognizer of section 4.2 asks for. `read` resolves the attributes of a `SayAs` for a language. `classify`
then runs the recognizers of the language for the named forms first, then the recognizer of this module that takes
the markup as evidence, then the other recognizers on the characters that are left.

The values come from the W3C Note "SSML 1.0 say-as attribute values" (26 May 2005): `date`, `time`, `telephone`,
`characters`, `cardinal` and `ordinal`. Amazon Polly ("Controlling how special types of words are spoken") defines
`digits`, `fraction` and `unit`, and the aliases `number` and `spell-out`. Google Cloud Text-to-Speech ("Speech
Synthesis Markup Language (SSML)") defines `currency` and the alias `verbatim`. IBM Watson Text to Speech ("SSML
elements") defines the alias `letters`: "The `letters` value spells out the characters in the word within the
element."
"""
from __future__ import annotations

import re
import warnings
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import TYPE_CHECKING

from text2spoken.core.dates import is_valid, resolve as resolve_date
from text2spoken.core.recognizers import (_DATE, PHONE_PLANS, _cluster_edge, _edge, _period_after, _phone_pattern,
                                          _sentence_period, digit_run_matches, numbers_in, whole_part)
from text2spoken.core.spans import SAY_AS_SPANS, Features, Recognizer, Span, SpanContext
from text2spoken.core.spellers import bounded_integer, spell_digits
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import Token, fold_digits, is_bounded, is_digit, is_word_char, one_digit_set
from text2spoken.errors import ArgumentTypeError, ParameterNotHonouredWarning, UnsupportedParameterError, require_type
from text2spoken.params import FrozenMap, Form, NormalizationParams

if TYPE_CHECKING:
    from text2spoken.core.language import LanguageSpec, Request


@dataclass(frozen=True, kw_only=True)
class SayAs:
    """The attributes of one SSML `say-as` element, as the markup writes them."""
    interpret_as: str
    format: str | None = None
    detail: str | None = None

    def __post_init__(self):
        require_type(self.interpret_as, "interpret_as", str)
        for name in ("format", "detail"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ArgumentTypeError(f"{name} must be str or None, not {type(value).__name__}")


ALIASES: Mapping[str, str] = MappingProxyType({
    "number": "cardinal", "spell-out": "characters", "letters": "characters", "verbatim": "characters"})
"""The other names that phoonnx takes, by the value of `VALUES` that they name."""

VALUES: Mapping[str, frozenset[Form]] = MappingProxyType({
    "cardinal": frozenset({Form.CARDINAL, Form.DECIMAL}),
    "ordinal": frozenset({Form.ORDINAL}),
    "date": frozenset({Form.DATE}),
    "time": frozenset({Form.TIME}),
    "telephone": frozenset({Form.TELEPHONE}),
    "currency": frozenset({Form.MONEY}),
    "unit": frozenset({Form.MEASURE}),
    "fraction": frozenset({Form.FRACTION}),
    "digits": frozenset(),
    "characters": frozenset(),
})
"""Each value that reads, with the forms whose recognizers of the language read it first. `digits` and
`characters` read only through the core readings of this module. A `date` with the format `y` reads `YEAR`."""

DATE_FORMATS: Mapping[str, str] = MappingProxyType({"dmy": "DMY", "mdy": "MDY", "ymd": "YMD"})
"""The three-field date formats of the Note, by the written order of the `DATE` fields."""

CLOCK_HOURS: Mapping[str | None, tuple[int, int]] = MappingProxyType({None: (0, 23), "hms24": (0, 23),
                                                                       "hms12": (1, 12)})
"""The hours that a time without a written day period may have, by its format (Note 3.2)."""


def _clean(value: str | None) -> str | None:
    """An attribute with no white space at its edges and in case-folded form, or None when it is empty."""
    if value is None:
        return None
    return value.strip().casefold() or None


def _numbers(text: str, request: Request):
    """The unsigned integers of the text that no word character touches."""
    return (number for number in numbers_in(text, request)
            if not number.sign and number.fraction is None and is_bounded(text, number.start, number.end))


@dataclass(frozen=True)
class BareOrdinal:
    """A run of digits with no ordinal mark, as in `123`."""
    name: str = "say_as_ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in _numbers(text, request):
            yield Span(number.start, number.end, Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": "", "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name)


def _fields_in_order(fields: Sequence[str], order: str) -> tuple[int, int, int, str] | None:
    """(year, month, day, order) of three digit fields in the written order of a date format, with a year of four
    digits, or None when they form no valid date."""
    by_field = dict(zip(order, fields))
    year, month, day = by_field["Y"], by_field["M"], by_field["D"]
    if len(year) != 4 or not 1 <= len(month) <= 2 or not 1 <= len(day) <= 2:
        return None
    values = int(year), int(month), int(day)
    return (*values, order) if is_valid(*values) else None


@dataclass(frozen=True)
class NumericDate:
    """Three digit fields that a hyphen, a slash or a full stop part (Note 3.1), read in the order of the format.
    With no format, the fields read as `DateNumeric` reads them. A year of two digits gives no date."""
    order: str | None = None
    name: str = "say_as_date"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in digit_run_matches(_DATE, fold_digits(text)):
            start, end = match.span()
            if not (_edge(text, start, end) and one_digit_set(text[start:end])):
                continue
            fields = tuple(re.split("[/.-]", match.group()))
            resolved = (_fields_in_order(fields, self.order) if self.order is not None
                        else resolve_date(fields, request.params.date_order))
            if resolved is None:
                continue
            year, month, day, order = resolved
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": order,
                                  "month_written": "digits", "prefix": "", "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class BareYear:
    """Four digits that do not start with zero, as in `2024`: the date format `y`."""
    name: str = "say_as_year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in _numbers(text, request):
            if number.end - number.start == 4 and number.integer[0] != "0":
                yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": number.integer, "suffix": ""}),
                           recognizer=self.name)


@dataclass(frozen=True)
class BareClock:
    """`H:MM` or `H:MM:SS`, with a colon or a full stop between the fields (Note 3.2), and the day period of
    `day_periods` that the text writes after it. A time with a written day period has an hour from 1 to 12; any
    other time has an hour of `hours`."""
    hours: tuple[int, int] = (0, 23)
    name: str = "say_as_time"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        periods = request.data.get("day_periods", FrozenMap())
        folded = fold_digits(text)
        for mark in (":", "."):
            escaped = re.escape(mark)
            pattern = re.compile(f"[0-9][0-9]?{escaped}[0-9][0-9](?:{escaped}[0-9][0-9])?")
            for match in digit_run_matches(pattern, folded):
                start, end = match.span()
                if (not _cluster_edge(text, start, end) or (start and is_word_char(text[start - 1]))
                        or not one_digit_set(text[start:end])):
                    continue
                parts = match.group().split(mark)
                fields = clock_fields(parts[0], parts[1], parts[2] if len(parts) == 3 else None)
                if fields is None:
                    continue
                hour, minute, second = fields
                period, trail = None, ""
                written_period = _period_after(text, end, periods)
                if written_period is not None:
                    period, end = written_period
                    if not 1 <= hour <= 12:
                        continue
                    if text[end - 1] == "." and _sentence_period(text, end):
                        trail = "."
                elif not self.hours[0] <= hour <= self.hours[1]:
                    continue
                if end < len(text) and is_word_char(text[end]):
                    continue
                yield Span(start, end, Form.TIME,
                           FrozenMap({"hour": hour, "minute": minute, "second": second, "period": period,
                                      "prefix": "", "suffix": ""}), trail=trail, recognizer=self.name)


@dataclass(frozen=True)
class BareTelephone:
    """A run of digit groups that a space, a full stop or a hyphen part, with an optional `+` and a country code and
    an optional area code in brackets. A `+` with no country code of `PHONE_PLANS` gives no span."""
    name: str = "say_as_telephone"
    form: Form = Form.TELEPHONE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        codes = sorted((plan["country_code"] for plan in PHONE_PLANS.values()), key=len, reverse=True)
        for match in _phone_pattern(" ").finditer(fold_digits(text)):
            start, end = match.span()
            written = match.group()
            if not (_edge(text, start, end) and one_digit_set(text[start:end])):
                continue
            groups = [group for group in re.split("[ .()-]", written.lstrip("+")) if group]
            country_code = ""
            if written.startswith("+"):
                if len(groups) > 1 and len(groups[0]) <= 3:
                    country_code, groups = groups[0], groups[1:]
                else:
                    country_code = next((code for code in codes if groups[0].startswith(code)), "")
                    if not country_code or groups[0] == country_code:
                        continue
                    groups[0] = groups[0][len(country_code):]
            yield Span(start, end, Form.TELEPHONE,
                       FrozenMap({"country_code": country_code, "groups": tuple(groups), "prefix": "", "suffix": ""}),
                       recognizer=self.name)


@dataclass(frozen=True)
class PlusMixedNumber:
    """A whole part, a plus sign and a proper fraction, as Amazon Polly writes a mixed number: `3+1/2` "is
    pronounced "three and a half."" ("Controlling how special types of words are spoken", `fraction`). The span
    holds the whole part in the field `whole`, as a mixed number with a space does (`whole_part`)."""
    name: str = "say_as_mixed_number"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in digit_run_matches("[0-9]+/[0-9]+", fold_digits(text)):
            start, end = match.span()
            numerator, denominator = match.group().split("/")
            top, bottom = bounded_integer(numerator), bounded_integer(denominator)
            if (not _edge(text, start, end) or numerator[0] == "0" or denominator[0] == "0" or bottom is None
                    or not 2 <= bottom <= 100 or top is None or not 0 < top < bottom):
                continue
            begin = whole_part(text, start, end, ("+",))
            if begin is not None and fold_digits(text[begin]) != "0" and one_digit_set(text[begin:end]):
                yield Span(begin, end, Form.FRACTION,
                           FrozenMap({"whole": fold_digits(text[begin:start - 1]), "numerator": numerator,
                                      "denominator": denominator, "sign": "", "prefix": "", "suffix": ""}),
                           recognizer=self.name)


@dataclass(frozen=True)
class DigitRun:
    """Each run of digits, which reads digit by digit."""
    name: str = "say_as_digits"
    form: Form = Form.IDENTIFIER

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer("[0-9]+", fold_digits(text)):
            if one_digit_set(text[match.start():match.end()]):
                yield Span(match.start(), match.end(), Form.IDENTIFIER,
                           FrozenMap({"head": "", "digits": match.group()}), recognizer=self.name)


@dataclass(frozen=True)
class CharacterRun:
    """Each run of characters of which every one has a name: a letter of `letter_names` in any case, or a digit."""
    name: str = "say_as_characters"
    form: Form = Form.LETTERS

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        names = request.data["letter_names"]
        start = None
        for index, char in enumerate((*text, "")):
            named = bool(char) and (is_digit(char) or char.casefold() in names)
            if named and start is None:
                start = index
            elif not named and start is not None:
                yield Span(start, index, Form.LETTERS,
                           FrozenMap({"letters": text[start:index], "reading": "characters", "clause": ()}),
                           recognizer=self.name)
                start = None


def speak_bare_ordinal(span: Span, context: SpanContext) -> str:
    """The ordinal through the ordinal speller of the language, with the `default_gender` of the params, else of
    the language (Note 3.6: "the best representation of the ordinal that it can")."""
    request = context.request
    language = request.language
    gender = request.params.default_gender.get(language.code) or language.default_gender
    features = Features(gender=gender) if gender is not None and language.genders else Features()
    return language.spellers[Form.ORDINAL].ordinal(span.fields["digits"], features, request)


def speak_digits(span: Span, context: SpanContext) -> str:
    return spell_digits(span.fields["digits"], context.request)


def speak_characters(span: Span, context: SpanContext) -> str:
    """Each character by its name: a digit by `digit_words`, a letter in any case by `letter_names` (Note 3.4)."""
    data = context.request.data
    names, digits = data["letter_names"], data["digit_words"]
    return " ".join(digits[int(fold_digits(char))] if is_digit(char) else names[char.casefold()]
                    for char in span.fields["letters"])


READINGS = MappingProxyType({BareOrdinal.name: speak_bare_ordinal, DigitRun.name: speak_digits,
                             CharacterRun.name: speak_characters})
"""The core readings, by the name of the recognizer whose spans they speak. Every other say-as span reads through
the verbalizer of the language."""


@dataclass(frozen=True, kw_only=True)
class ResolvedSayAs:
    """A say-as as one call reads it: the value of `VALUES`, the format and the detail that the language honours,
    the forms whose recognizers of the language read first, and the recognizer that takes the markup as evidence."""
    value: str
    format: str | None
    detail: str | None
    forms: frozenset[Form]
    forced: Recognizer | None
    plain: NormalizationParams | None = None
    """The params of the call with no say-as, for the plain reading when a say-as span declines."""

    def recognizers(self, language: LanguageSpec) -> tuple[Recognizer, ...]:
        """The recognizers that claim first, in claim order."""
        first = tuple(r for r in language.recognizers if r.form in self.forms)
        return first if self.forced is None else (*first, self.forced)

    def fits(self, span: Span) -> bool:
        """Whether a span agrees with the format: a numeric date in the field order of the format, and a time with
        no day period in the hours of the format."""
        if self.value == "date" and self.format in DATE_FORMATS and span.form is Form.DATE:
            return span.fields["month_written"] != "digits" or span.fields["written_order"] == DATE_FORMATS[self.format]
        if self.value == "time" and span.form is Form.TIME and span.fields["period"] is None:
            low, high = CLOCK_HOURS[self.format]
            return low <= span.fields["hour"] <= high
        return True

    def claims(self, span: Span, request: Request) -> bool:
        """Whether a recognizer of the say-as claimed the span in the call of the request."""
        return (span.start, span.end) in request.memo.get(SAY_AS_SPANS, ())

    def read_in(self, spans: Sequence[Span], request: Request) -> bool:
        """Whether one of the spans reads the say-as."""
        return any(self.claims(span, request) for span in spans)


def _not_honoured(message: str, strict: bool) -> None:
    if strict:
        raise UnsupportedParameterError(message)
    warnings.warn(message, ParameterNotHonouredWarning, stacklevel=6)


def _reads(value: str, language: LanguageSpec, data: FrozenMap) -> bool:
    """Whether the language reads the value with no format."""
    if value == "digits":
        return "digit_words" in data
    if value == "characters":
        return "digit_words" in data and "letter_names" in data
    if value == "ordinal":
        return Form.ORDINAL in language.verbalizers and Form.ORDINAL in language.spellers
    return all(form in language.verbalizers for form in VALUES[value] - {Form.DECIMAL})


def _decimal_mark(format: str | None, detail: str | None, language: LanguageSpec,
                  ignore: Callable[[str, str], None]) -> str | None:
    """The decimal mark of a `cardinal`: the format, or the other mark of a language that declares two marks when
    the detail names one as the group mark (Note 3.5)."""
    marks = language.options.get("decimal_mark", frozenset())
    mark = None
    if format is not None:
        if format in marks:
            mark = format
        else:
            ignore("format", format)
    if detail is not None:
        others = marks - {detail}
        if detail not in marks or len(others) != 1 or (mark is not None and mark != next(iter(others))):
            ignore("detail", detail)
        else:
            mark = next(iter(others))
    return mark


def read(say_as: SayAs, tag: str, language: LanguageSpec, data: FrozenMap,
         params: NormalizationParams) -> tuple[ResolvedSayAs | None, NormalizationParams]:
    """The say-as as the language reads it, and the params of the call with the decimal mark of a `cardinal`.

    The value and its format are case-folded, with no white space at their edges. A value that the core does not
    read, or that names a form the language does not read, gives None: the call then gives the plain reading. A
    format or a detail that the language cannot honour is dropped, and the say-as reads without it. Each case
    warns with `ParameterNotHonouredWarning`, and raises `UnsupportedParameterError` in strict mode (section 17.6).
    """
    require_type(say_as, "say_as", SayAs)
    strict = params.strict
    value = _clean(say_as.interpret_as) or ""
    value = ALIASES.get(value, value)
    if value not in VALUES or not _reads(value, language, data):
        _not_honoured(f"{tag!r} reads no say-as {say_as.interpret_as!r}; the text reads as if no say-as were given",
                      strict)
        return None, params
    attributes = {"format": _clean(say_as.format), "detail": _clean(say_as.detail)}

    def ignore(name: str, written: str) -> None:
        attributes[name] = None
        _not_honoured(f"{tag!r} cannot honour the {name} {written!r} of the say-as {value!r}; the say-as reads "
                      "without it", strict)

    forms, forced = VALUES[value], None
    format, detail = attributes["format"], attributes["detail"]
    if value == "cardinal":
        mark = _decimal_mark(format, detail, language, ignore)
        if mark is not None:
            params = replace(params, decimal_mark=mark)
    else:
        if detail is not None:
            ignore("detail", detail)
        if value == "date":
            if format == "y" and Form.YEAR in language.verbalizers:
                forms, forced = frozenset({Form.YEAR}), BareYear()
            elif format is not None and format not in DATE_FORMATS:
                ignore("format", format)
            if forced is None:
                forced = NumericDate(DATE_FORMATS.get(attributes["format"]))
        elif value == "time":
            if format is not None and format not in CLOCK_HOURS:
                ignore("format", format)
            forced = BareClock(CLOCK_HOURS[attributes["format"]])
        elif value == "telephone":
            if format is not None and not re.fullmatch("[0-9]{1,3}", format):
                ignore("format", format)
            forced = BareTelephone()
        elif value == "characters":
            if format is not None and format != "characters":
                ignore("format", format)
            forced = CharacterRun()
        elif format is not None:
            ignore("format", format)
        if value == "ordinal":
            forced = BareOrdinal()
        elif value == "digits":
            forced = DigitRun()
        elif value == "fraction":
            forced = PlusMixedNumber()
    return ResolvedSayAs(value=value, format=attributes["format"], detail=attributes["detail"], forms=forms,
                         forced=forced), params
