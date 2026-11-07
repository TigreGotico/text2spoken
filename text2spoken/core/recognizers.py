"""The shared recognizers, each with a name (design sections 4.2, 4.3, 5.3).

A recognizer reads characters, not tokens: money, telephone numbers and colours cross token gaps. Each
regular expression here uses the portable subset of section 8, and runs on the text with its digits folded to
ASCII, which keeps every offset.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.color import COLOR
from text2spoken.core.dates import resolve as resolve_date
from text2spoken.core.language import Request, lexicon_entries
from text2spoken.core.numbers import SIGNS, Number, find_numbers, number_marks
from text2spoken.core.spans import Features, SpanContext, Span, clause_window, context_words
from text2spoken.core.spellers import DigitSpeller
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import (Token, fold_digits, is_bounded, is_digit, is_letter, is_mark,
                                     is_word_char, next_visible, one_digit_set)
from text2spoken.params import FrozenMap, Form

PHONE_PLANS = FrozenMap({
    "AE": FrozenMap({"country_code": "971", "trunk": "0", "lengths": (8, 9)}),
    "BR": FrozenMap({"country_code": "55", "trunk": "0", "lengths": (10, 11)}),
    "EG": FrozenMap({"country_code": "20", "trunk": "0", "lengths": (9, 10)}),
    "ES": FrozenMap({"country_code": "34", "trunk": "", "lengths": (9,)}),
    "FR": FrozenMap({"country_code": "33", "trunk": "0", "lengths": (9,)}),
    "GB": FrozenMap({"country_code": "44", "trunk": "0", "lengths": (10,)}),
    "PT": FrozenMap({"country_code": "351", "trunk": "", "lengths": (9,)}),
    "SA": FrozenMap({"country_code": "966", "trunk": "0", "lengths": (9,)}),
    "US": FrozenMap({"country_code": "1", "trunk": "1", "lengths": (10,)}),
})
"""Numbering plans by ISO 3166 region: the country calling code (ITU-T E.164), the trunk prefix and the
lengths of the national significant number. A partial table; a region with no plan gives no trunk evidence."""


def numbers_in(text: str, request: Request) -> tuple[Number, ...]:
    """The numbers of the text, found once for each text in one request."""
    key = ("numbers", text)
    if key not in request.memo:
        request.memo[key] = find_numbers(text, number_marks(request.data, request.params.decimal_mark))
    return request.memo[key]


def _free_before(text: str, start: int, symbols) -> bool:
    """Whether no word character and no form symbol touches text[start:] from the left.

    `classify` refuses a span that one character joins to an unread digit run, because only it knows the spans.
    """
    return start == 0 or not (is_word_char(text[start - 1]) or text[start - 1] in symbols or text[start - 1] == "#")


def _free_after(text: str, end: int, symbols) -> bool:
    """Whether no word character and no form symbol touches text[:end] from the right."""
    return end == len(text) or not (is_word_char(text[end]) or text[end] in symbols)


def _affixes(text: str, start: int, end: int, data) -> tuple[int, int, str, str] | None:
    """The span with a declared proclitic before it and a declared case ending after it, or None when a
    letter that is neither touches the number."""
    symbols = data.get("symbols", FrozenMap())
    prefix = next((p for p in sorted(data.get("proclitics", ()), key=len, reverse=True)
                   if start >= len(p) and text[start - len(p):start] == p
                   and _free_before(text, start - len(p), symbols)), "")
    if prefix:
        start -= len(prefix)
    elif not _free_before(text, start, symbols):
        return None
    after = _suffix(text, end, data)
    if after is None:
        return None
    return start, after[0], prefix, after[1]


def _suffix(text: str, end: int, data) -> tuple[int, str] | None:
    """The end of the span with a declared case ending after text[:end], or None when other letters touch it."""
    letters = end
    while letters < len(text) and (is_letter(text[letters]) or is_mark(text[letters])):
        letters += 1
    suffix = text[end:letters]
    if suffix and suffix not in data.get("case_suffixes", ()):
        return None
    if not _free_after(text, letters, data.get("symbols", FrozenMap())):
        return None
    return letters, suffix


def _lead(text: str, start: int, leads) -> str:
    """The longest declared lead that ends right before the digits at `start`.

    No lead follows a digit or another lead, so `##5` stays as written. A lead with words follows no
    word character either, so `C#5` stays as written, while a lead that stands for a space joins a word, as in
    `sub-23`.
    """
    for lead in sorted(leads, key=len, reverse=True):
        if not text.endswith(lead, 0, start):
            continue
        before = start - len(lead) - 1
        if before < 0 or not (is_digit(text[before]) or any(text.endswith(other, 0, before + 1) for other in leads)
                              or (leads[lead] and is_word_char(text[before]))):
            return lead
    return ""


def _sentence_period(text: str, end: int) -> bool:
    """Whether a period at text[end - 1] also ends the sentence: the text ends, or a capital letter follows."""
    following = next_visible(text, end)
    return following == "" or following.isupper()


def join_ranges(spans: Iterator[Span], text: str, range_word: str | None) -> Iterator[Span]:
    """The spans, where a dash alone between two of them joins them as a range: the first span takes the dash
    and a trail of the range word, as in `9am-5pm` and `1939-1945`."""
    ordered = sorted(spans, key=lambda span: span.start)
    for span, following in zip(ordered, ordered[1:] + [None]):
        if (range_word and following is not None and not span.trail
                and text[span.end:following.start] in ("-", "–")):
            span = replace(span, end=following.start, trail=f" {range_word} ")
        yield span


@dataclass(frozen=True)
class Lexicon:
    name: str = "lexicon"
    form: Form = Form.LEXICON

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        entries = lexicon_entries(request.tag, request.params.lexicon)
        keys = sorted(entries, key=len, reverse=True)
        position = 0
        while position < len(text):
            key = next((k for k in keys if text.startswith(k, position)
                        and _lexicon_limit(text, position - 1) and _lexicon_limit(text, position + len(k))), None)
            if key is None:
                position += 1
                continue
            yield Span(position, position + len(key), Form.LEXICON, FrozenMap({"spoken": entries[key]}),
                       recognizer=self.name)
            position += len(key)


def _lexicon_limit(text: str, index: int) -> bool:
    return index < 0 or index >= len(text) or not is_word_char(text[index])


@dataclass(frozen=True)
class Cardinal:
    name: str = "cardinal"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        leads = request.data.get("leads", FrozenMap())
        sign_words = request.data.get("sign_words", FrozenMap())
        for number in numbers_in(text, request):
            if number.fraction is not None or (number.sign and number.sign not in sign_words):
                continue
            bounds = _affixes(text, number.start, number.end, request.data)
            proclitic = bounds is not None and bounds[2]
            lead = "" if number.sign or proclitic else _lead(text, number.start, leads)
            if lead:
                after = _suffix(text, number.end, request.data)
                if after is None:
                    continue
                start, end, prefix, suffix = number.start - len(lead), after[0], "", after[1]
            elif bounds is None or (len(number.integer) > 1 and number.integer[0] == "0"):
                continue
            else:
                start, end, prefix, suffix = bounds
            yield Span(start, end, Form.CARDINAL,
                       FrozenMap({"digits": number.integer, "sign": number.sign, "lead": lead, "prefix": prefix,
                                  "suffix": suffix, "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Decimal:
    name: str = "decimal"
    form: Form = Form.DECIMAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if number.fraction is None:
                continue
            bounds = _affixes(text, number.start, number.end, request.data)
            if bounds is None:
                continue
            start, end, prefix, suffix = bounds
            yield Span(start, end, Form.DECIMAL, number.amount(prefix, suffix), recognizer=self.name)


_FRACTION = re.compile("[-+−]?[0-9]+/[0-9]+")
_DATE = re.compile("[0-9]+/[0-9]+/[0-9]+|[0-9]+-[0-9]+-[0-9]+|[0-9]+[.][0-9]+[.][0-9]+")
_CLOCK = re.compile("[0-9][0-9]?:[0-9][0-9](?::[0-9][0-9])?")
_HOUR = re.compile("[0-9][0-9]?")
_JOINERS = "/:.,-–"
_PHONE = re.compile("[+]?(?:[(][0-9]+[)] ?)?[0-9]+(?:[ .-][0-9]+)*")
_RANGE = re.compile("[0-9]+[-–][0-9]+")


def _cluster_edge(text: str, start: int, end: int) -> bool:
    """Whether no digit, and no cluster mark before a digit, continues text[start:end] on either side."""
    before_ok = start == 0 or not (is_digit(text[start - 1])
                                   or (text[start - 1] in _JOINERS and start > 1 and is_digit(text[start - 2])))
    after_ok = end == len(text) or not (is_digit(text[end])
                                        or (text[end] in _JOINERS and end + 1 < len(text) and is_digit(text[end + 1])))
    return before_ok and after_ok


def _bounded_matches(pattern: re.Pattern, text: str) -> Iterator[re.Match]:
    """Matches in the folded text that no word character, digit or cluster mark continues on either side."""
    for match in pattern.finditer(fold_digits(text)):
        start, end = match.span()
        if _cluster_edge(text, start, end) and is_bounded(text, start, end):
            yield match


def _unit_after(text: str, end: int, units: Iterable[str]) -> bool:
    """Whether a unit of the language follows text[:end], attached or after one space."""
    return any(text.startswith(gap + unit, end) and is_bounded(text, end + len(gap), end + len(gap) + len(unit))
               for gap in ("", " ", " ") for unit in units)


@dataclass(frozen=True)
class Fraction:
    name: str = "fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A symbol of the language next to the fraction or a unit after it leaves a reading that is not clear,
        as in `$5/6` and `3/4 kg`, so the fraction stays as written, as do digits from two digit sets."""
        symbols = request.data.get("symbols", FrozenMap())
        units = request.data.get("units", FrozenMap())
        for match in _bounded_matches(_FRACTION, text):
            start, end = match.span()
            written = match.group()
            sign = "-" if written[0] in "-−" else "+" if written[0] == "+" else ""
            numerator, denominator = written.lstrip("-+−").split("/")
            if sign and start > 0 and is_word_char(text[start - 1]):
                continue
            unclear = (not (_free_before(text, start, symbols) and _free_after(text, end, symbols))
                       or _unit_after(text, end, units) or not one_digit_set(text[start:end]))
            if unclear or (2 <= int(denominator) <= 100 and int(numerator) < int(denominator)):
                yield Span(start, end, Form.FRACTION,
                           FrozenMap({"numerator": numerator, "denominator": denominator, "sign": sign,
                                      "prefix": "", "suffix": ""}), recognizer=self.name, keep=unclear)


@dataclass(frozen=True)
class Idiom:
    name: str = "idiom"
    form: Form = Form.IDIOM

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for key in request.data.get("idioms", FrozenMap()):
            position = text.find(key)
            while position != -1:
                end = position + len(key)
                if _free_before(text, position, ()) and _free_after(text, end, ()) \
                        and not (end < len(text) and text[end] == "/"):
                    yield Span(position, end, Form.IDIOM, FrozenMap({"key": key}), recognizer=self.name)
                position = text.find(key, end)


@dataclass(frozen=True)
class Range:
    name: str = "range"
    form: Form = Form.RANGE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """Digits from two digit sets keep the whole range as written."""
        for match in _bounded_matches(_RANGE, text):
            low, high = re.split("[-–]", match.group())
            yield Span(match.start(), match.end(), Form.RANGE,
                       FrozenMap({"low": low, "high": high, "prefix": "", "suffix": ""}), recognizer=self.name,
                       keep=not one_digit_set(text[match.start():match.end()]))


@dataclass(frozen=True)
class DateNumeric:
    name: str = "date_numeric"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        folded = fold_digits(text)
        for match in _DATE.finditer(folded):
            start, end = match.span()
            if not (_cluster_edge(text, start, end) and one_digit_set(text[start:end])):
                continue
            fields = tuple(re.split("[/.-]", match.group()))
            resolved = resolve_date(fields, request.params.date_order)
            bounds = _affixes(text, match.start(), match.end(), request.data)
            if resolved is None or bounds is None:
                continue
            year, month, day, order = resolved
            start, end, _, suffix = bounds
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": order,
                                  "month_written": "digits", "suffix": suffix}), recognizer=self.name)


def _period_after(text: str, end: int, periods) -> tuple[str, int] | None:
    """The day period written after a time, with its end: `pm` in `2:30 pm`, `am` in `9am`."""
    rest = text[end:]
    gap = len(rest) - len(rest.lstrip(" ")) if rest.startswith(" ") else 0
    if gap > 1:
        return None
    for period, spellings in periods.items():
        for spelling in sorted(spellings, key=len, reverse=True):
            stop = end + gap + len(spelling)
            if text.startswith(spelling, end + gap) and (stop == len(text) or not is_word_char(text[stop])):
                return period, stop
    return None


@dataclass(frozen=True)
class TimeClock:
    """`at 14:30`, `at 14:30:05`, `2:30 pm`, `9am`, with the evidence rule of section 4.2, and `9am-5pm`.

    A seconds field is no evidence, because a duration such as `1:23:45` has one."""
    name: str = "time_clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._times(text, tokens, request), text, request.data.get("range_word"))

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        words = context_words(tokens)
        time_words = frozenset(w.lower() for w in data.get("time_words", ()))
        periods = data.get("day_periods", FrozenMap())
        suffixes = data.get("time_suffixes", ())
        folded = fold_digits(text)
        for pattern in (_CLOCK, _HOUR):
            for match in pattern.finditer(folded):
                start, end = match.span()
                if (not _cluster_edge(text, start, end) or (start and is_word_char(text[start - 1]))
                        or not one_digit_set(text[start:end])):
                    continue
                parts = match.group().split(":")
                if pattern is _CLOCK:
                    fields = clock_fields(parts[0], parts[1], parts[2] if len(parts) == 3 else None)
                else:
                    fields = (int(parts[0]), 0, None)
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
                elif pattern is _HOUR:
                    continue
                suffix = next((s for s in suffixes if text.startswith(s, end)), "")
                if end + len(suffix) < len(text) and is_word_char(text[end + len(suffix)]):
                    continue
                before = clause_window(text, words, start, end, -1, limit=1)
                if not (period is not None or suffix or (before and before[0].lower() in time_words)):
                    continue
                yield Span(start, end + len(suffix), Form.TIME,
                           FrozenMap({"hour": hour, "minute": minute, "second": second, "period": period,
                                      "suffix": suffix}), trail=trail, recognizer=self.name)


@dataclass(frozen=True)
class Percent:
    name: str = "percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        percent = request.data.get("percent")
        if percent is None:
            return
        for number in numbers_in(text, request):
            if percent["position"] in ("after", "either"):
                for sign in percent["signs"]:
                    for gap in ("", " ", " "):
                        end = number.end + len(gap) + len(sign)
                        if text.startswith(gap + sign, number.end) and _free_after(text, end, ()) \
                                and _free_before(text, number.start, ()):
                            yield Span(number.start, end, Form.PERCENT,
                                       FrozenMap({"amount": number.amount(), "sign_position": "after"}),
                                       recognizer=self.name)
            if percent["position"] in ("before", "either"):
                for sign in percent["signs"]:
                    start = number.start - len(sign)
                    if start >= 0 and text[start:number.start] == sign and _free_after(text, number.end, ()) \
                            and _free_before(text, start, ()):
                        yield Span(start, number.end, Form.PERCENT,
                                   FrozenMap({"amount": number.amount(), "sign_position": "before"}),
                                   recognizer=self.name)


@dataclass(frozen=True)
class Money:
    name: str = "money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._amounts(text, tokens, request), text, request.data.get("range_word"))

    def _amounts(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A currency symbol before or after a number. Before a symbol that comes first, a sign may stand, and
        after its number a scale word of the language, attached or after one space: `-$5`, `$2 million`, `$1m`."""
        symbols = [(symbol, code) for code, currency in request.data.get("currencies", FrozenMap()).items()
                   for symbol in currency["symbols"]]
        scales = sorted(request.data.get("scales", FrozenMap()), key=len, reverse=True)
        for number in numbers_in(text, request):
            if number.sign:
                continue
            for symbol, code in sorted(symbols, key=lambda pair: len(pair[0]), reverse=True):
                found = None
                for gap in ("", " ", " "):
                    start = number.start - len(gap) - len(symbol)
                    if start >= 0 and text[start:number.start] == symbol + gap:
                        sign = SIGNS.get(text[start - 1], "") if start else ""
                        if sign and _free_before(text, start - 1, ()):
                            start -= 1
                        else:
                            sign = ""
                        scale, end = _scale(text, number.end, scales)
                        if _free_before(text, start, ()) and _free_after(text, end, ()):
                            found = (start, end, sign, scale)
                            break
                    end = number.end + len(gap) + len(symbol)
                    if text.startswith(gap + symbol, number.end) and _free_after(text, end, ()) \
                            and _free_before(text, number.start, ()):
                        found = (number.start, end, "", "")
                        break
                if found:
                    start, end, sign, scale = found
                    yield Span(start, end, Form.MONEY,
                               FrozenMap({"amount": FrozenMap({**number.amount(), "sign": sign}), "currency": code,
                                          "written_symbol": symbol, "scale": scale}), recognizer=self.name)
                    break


def _scale(text: str, end: int, scales: Sequence[str]) -> tuple[str, int]:
    """The scale word written after text[:end], attached or after one space, and the end of the span."""
    for gap in ("", " ", " "):
        for scale in scales:
            stop = end + len(gap) + len(scale)
            if text.startswith(gap + scale, end) and (stop == len(text) or not is_word_char(text[stop])):
                return scale, stop
    return "", end


@dataclass(frozen=True)
class Measure:
    """`10kg`, `25°C`, `5 km/h`, `15x8 cm` and `10 × 20 cm`, where a dimension mark reads as the language's
    word for "by", and `20-25°C`, where a range mark reads as its range word."""
    name: str = "measure"
    form: Form = Form.MEASURE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        symbols = data.get("symbols", FrozenMap())
        units = sorted(data.get("units", FrozenMap()), key=len, reverse=True)
        relations = {"dimension": data.get("dimension_marks", ()), "range": data.get("range_marks", ())}
        every_mark = tuple(mark for marks in relations.values() for mark in marks)
        numbers = numbers_in(text, request)
        by_start = {n.start: n for n in numbers}
        for index, number in enumerate(numbers):
            if not _free_before(text, number.start, symbols) or (
                    index and _linked(text, numbers[index - 1].end, every_mark, by_start) is number):
                continue
            amounts, end, relation = [number], number.end, ""
            for kind, marks in relations.items():
                while relation in ("", kind) and (following := _linked(text, end, marks, by_start)) is not None:
                    relation = kind
                    amounts.append(following)
                    end = following.end
            for gap in ("", " ", " "):
                unit = next((u for u in units if text.startswith(gap + u, end)
                             and _free_after(text, end + len(gap) + len(u), symbols)
                             and not _per_unit(text, end + len(gap) + len(u))), None)
                if unit is not None:
                    amount = amounts[0].amount() if len(amounts) == 1 else tuple(a.amount() for a in amounts)
                    yield Span(number.start, end + len(gap) + len(unit), Form.MEASURE,
                               FrozenMap({"amount": amount, "relation": relation, "unit": unit}), recognizer=self.name)
                    break


def _per_unit(text: str, end: int) -> bool:
    """Whether a slash and a letter continue a unit, as in `m/s` when the table holds only `m`."""
    return end + 1 < len(text) and text[end] == "/" and is_letter(text[end + 1])


def _linked(text: str, end: int, marks: Sequence[str], by_start: dict[int, Number]) -> Number | None:
    """The unsigned number that one of the marks joins to text[:end], with no space or one space on each side."""
    for mark in marks:
        for gap in ("", " "):
            following = by_start.get(end + 2 * len(gap) + len(mark))
            if following is not None and not following.sign and text.startswith(gap + mark + gap, end):
                return following
    return None


@dataclass(frozen=True)
class Telephone:
    """A digit run with phone evidence (section 4.3): `+` or `00` and a country code, a trunk prefix of a
    region in `phone_regions`, or a word before the run that names a phone.

    A run after a phone word that fails the numbering plan, such as `911` in `Call 911 now.`, stays as written, and
    so does a run with digits from two digit sets."""
    name: str = "telephone"
    form: Form = Form.TELEPHONE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        words = context_words(tokens)
        phone_words = frozenset(w.lower() for w in request.data.get("phone_words", ()))
        codes = sorted((plan["country_code"] for plan in PHONE_PLANS.values()), key=len, reverse=True)
        plans = [PHONE_PLANS[r] for r in sorted(request.params.phone_regions or ()) if r in PHONE_PLANS]
        for match in _bounded_matches(_PHONE, text):
            written = match.group()
            groups = [group for group in re.split("[ .()-]", written.lstrip("+")) if group]
            digits = "".join(groups)
            mixed = not one_digit_set(text[match.start():match.end()])
            if mixed or not 7 <= len(digits) <= 15:
                before = clause_window(text, words, match.start(), match.end(), -1, limit=1)
                if mixed or (not written.startswith("+") and before and before[0].lower() in phone_words):
                    yield Span(match.start(), match.end(), Form.TELEPHONE,
                               FrozenMap({"country_code": "", "groups": tuple(groups)}), recognizer=self.name,
                               keep=True)
                continue
            country_code = ""
            if written.startswith("+"):
                if len(groups) > 1 and len(groups[0]) <= 3:
                    country_code, groups = groups[0], groups[1:]
                else:
                    country_code = next((c for c in codes if groups[0].startswith(c)), "")
                    groups[0] = groups[0][len(country_code):]
                if not country_code:
                    continue
            elif digits.startswith("00"):
                if not any(digits[2:].startswith(code) for code in codes):
                    continue
            else:
                trunk = any(plan["trunk"] and digits.startswith(plan["trunk"])
                            and len(digits) - len(plan["trunk"]) in plan["lengths"] for plan in plans)
                before = clause_window(text, words, match.start(), match.end(), -1, limit=1)
                if not (trunk or (before and before[0].lower() in phone_words)):
                    continue
            yield Span(match.start(), match.end(), Form.TELEPHONE,
                       FrozenMap({"country_code": country_code, "groups": tuple(groups)}), recognizer=self.name)


def speak_lexicon(span: Span, context: SpanContext) -> str:
    return span.fields["spoken"]


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal through the language's cardinal speller, with the sign words and the lead words of its data.

    A lead word of "" stands for a space. Digits with a leading zero, which only a lead admits, read one by one.
    """
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)
    else:
        words = request.language.spellers[Form.CARDINAL].cardinal(digits, Features(), request)
    if fields["sign"]:
        words = f"{request.data['sign_words'][fields['sign']]} {words}"
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


LEXICON = Lexicon()
CARDINAL = Cardinal()
SHARED = {r.name: r for r in (LEXICON, CARDINAL, Decimal(), Fraction(), Idiom(), Range(), DateNumeric(), TimeClock(),
                              Percent(), Money(), Measure(), Telephone(), COLOR)}
"""The shared recognizers by name."""
