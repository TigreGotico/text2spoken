"""The shared recognizers, each with a name (design sections 4.2, 4.3, 5.3).

A recognizer reads characters, not tokens: money, telephone numbers and colours cross token gaps. Each
regular expression here uses the portable subset of section 8, and runs on the text with its digits folded to
ASCII, which keeps every offset.
"""
from __future__ import annotations

import re
import unicodedata
from bisect import bisect_right
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from types import MappingProxyType

from text2spoken.core.color import COLOR
from text2spoken.core.dates import resolve as resolve_date
from text2spoken.core.language import Request, lexicon_entries
from text2spoken.core.numbers import SIGNS, Number, find_numbers, number_marks
from text2spoken.core.spans import (Features, Recognizer, SpanContext, Span, Word, clause_breaks, clause_window,
                                    context_words)
from text2spoken.core.spellers import DigitSpeller, bounded_integer
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


GAPS = ("", " ", "\u00a0", "\u202f")
"""The gaps that may stand between a number and its unit, symbol or day period: none, a space, a no-break space and
a narrow no-break space, which French typography puts before `%`, `€` and units."""


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


def _affixes(text: str, start: int, end: int, data, symbols=None) -> tuple[int, int, str, str] | None:
    """The span with a declared proclitic before it and a declared case ending after it, or None when a
    letter that is neither touches it.

    `symbols` are the characters that may not touch the span. By default they are the `symbols` table of the
    language."""
    before = _prefix(text, start, data, symbols)
    after = _suffix(text, end, data, symbols)
    if before is None or after is None:
        return None
    return before[0], after[0], before[1], after[1]


def _prefix(text: str, start: int, data, symbols=None) -> tuple[int, str] | None:
    """The start of the span with a declared proclitic before text[start:], or None when other letters touch it."""
    symbols = data.get("symbols", FrozenMap()) if symbols is None else symbols
    prefix = next((p for p in sorted(data.get("proclitics", ()), key=len, reverse=True)
                   if start >= len(p) and text[start - len(p):start] == p
                   and _free_before(text, start - len(p), symbols)), "")
    if prefix:
        return start - len(prefix), prefix
    if not _free_before(text, start, symbols):
        return None
    return start, ""


def _suffix(text: str, end: int, data, symbols=None) -> tuple[int, str] | None:
    """The end of the span with a declared case ending after text[:end], or None when other letters touch it."""
    symbols = data.get("symbols", FrozenMap()) if symbols is None else symbols
    letters = end
    while letters < len(text) and (is_letter(text[letters]) or is_mark(text[letters])):
        letters += 1
    suffix = text[end:letters]
    if suffix and suffix not in data.get("case_suffixes", ()):
        return None
    if not _free_after(text, letters, symbols):
        return None
    return letters, suffix


def _lead(text: str, start: int, leads) -> str:
    """The longest declared lead that ends right before the digits at `start`.

    No lead follows a digit or a lead with words, so `##5` stays as written, while `#1-#5` reads both numbers.
    A lead with words follows no word character either, so `C#5` stays as written, while a lead that stands for
    a space joins a word, as in `sub-23`.
    """
    for lead in sorted(leads, key=len, reverse=True):
        if not text.endswith(lead, 0, start):
            continue
        before = start - len(lead) - 1
        if before < 0 or not (is_digit(text[before])
                              or any(leads[other] and text.endswith(other, 0, before + 1) for other in leads)
                              or (leads[lead] and is_word_char(text[before]))):
            return lead
    return ""


def _continued(text: str, end: int) -> bool:
    """Whether the run goes on after text[:end]: a format character, such as the zero-width joiner of
    `7pm\u200d9`, or one character that is not a space or a digit and then a digit."""
    return end < len(text) and (unicodedata.category(text[end]) == "Cf" or (
        end + 1 < len(text) and not text[end].isspace() and not is_digit(text[end]) and is_digit(text[end + 1])))


def _sentence_period(text: str, end: int) -> bool:
    """Whether a period at text[end - 1] also ends the sentence: the text ends, or a capital letter follows."""
    following = next_visible(text, end)
    return following == "" or following.isupper()


def join_ranges(spans: Iterator[Span], text: str, request: Request) -> Iterator[Span]:
    """The spans, where a mark of the `range_marks` table alone between two of them joins them as a range, as in
    `9am-5pm` and `1939-1945`. The `join_range` hook of the language takes the pair and the `range_word`, which
    is empty when the language has none, and gives the joined pair: by default the first span takes the mark and a
    trail of the range word. A language that marks a range with case endings gives each span its ending.

    Spans that range marks chain join as one run, as in `9am-5pm-7pm`: the second span of each pair, as the hook
    gives it, is the first of the next pair. A joiner and a digit after the last span of the chain, as in
    `1990-91-92`, keep every span of it apart: they wait, and the run stays as written."""
    range_word = request.data.get("range_word", "")
    marks = request.data.get("range_marks", ())
    chains: list[list[Span]] = []
    for span in sorted(spans, key=lambda span: span.start):
        if chains and text[chains[-1][-1].end:span.start] in marks:
            chains[-1].append(span)
        else:
            chains.append([span])
    for chain in chains:
        joined = not _continued(text, chain[-1].end)
        span = chain[0]
        for following in chain[1:]:
            if joined and not span.trail:
                span, following = request.language.join_range(span, following, range_word)
            yield span
            span = following
        yield span


@dataclass(frozen=True)
class Lexicon:
    name: str = "lexicon"
    form: Form = Form.LEXICON

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        entries = lexicon_entries(request.tag, request.params.lexicon)
        by_first = _keys_by_first_character(entries)
        position = 0
        while position < len(text):
            key = next((k for k in by_first.get(text[position], ()) if text.startswith(k, position)
                        and _lexicon_limit(text, position - 1) and _lexicon_limit(text, position + len(k))), None)
            if key is None:
                position += 1
                continue
            yield Span(position, position + len(key), Form.LEXICON, FrozenMap({"spoken": entries[key]}),
                       recognizer=self.name)
            position += len(key)


@lru_cache(maxsize=128)
def _keys_by_first_character(entries: FrozenMap) -> Mapping[str, tuple[str, ...]]:
    """The lexicon keys by their first character, the longest first, so that a lookup tries only the keys that
    can start at a position, in the order of the whole table. The cache shares the result, so it is read-only."""
    by_first: dict[str, list[str]] = {}
    for key in sorted(entries, key=len, reverse=True):
        by_first.setdefault(key[0], []).append(key)
    return MappingProxyType({first: tuple(keys) for first, keys in by_first.items()})


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
_HOUR = re.compile("[0-9][0-9]?")
_JOINERS = "/:.,-–"
_PHONE = re.compile("[+]?(?:[(][0-9]+[)] ?)?[0-9]+(?:[ \u00a0\u202f.-][0-9]+)*")
_GLUED = re.compile("(?:[ /:.,–-]?[0-9]+)*")
_DIGIT_RUN = re.compile("[0-9]+")


def _cluster_edge(text: str, start: int, end: int) -> bool:
    """Whether no digit, and no cluster mark between two digits, continues text[start:end] on either side.

    A mark before a sign joins no two digits, so `-1/2` in `$12.-1/2` has an edge. `classify` holds it until a
    span reads `12`, as on a second pass."""
    before_ok = start == 0 or not (is_digit(text[start - 1])
                                   or (text[start - 1] in _JOINERS and start > 1 and is_digit(text[start - 2])
                                       and is_digit(text[start])))
    after_ok = end == len(text) or not (is_digit(text[end])
                                        or (text[end] in _JOINERS and end + 1 < len(text) and is_digit(text[end + 1])))
    return before_ok and after_ok


def _edge(text: str, start: int, end: int) -> bool:
    """Whether no word character, digit or cluster mark continues text[start:end] on either side."""
    return _cluster_edge(text, start, end) and is_bounded(text, start, end)


def digit_run_matches(pattern: re.Pattern | str, folded: str) -> Iterator[re.Match]:
    """The matches of `pattern.finditer(folded)`, for a pattern that starts with an optional character that is no
    digit and then `[0-9]+`, as `[-+−]?[0-9]+/[0-9]+`.

    `finditer` tries each start inside a digit run, and each try reads to the end of the run, so one long run takes
    quadratic time. A match that starts inside a run also starts one digit earlier, so the scan tries only the
    character before each run and its first digit, and takes linear time."""
    pattern = re.compile(pattern)
    end = 0
    for run in _DIGIT_RUN.finditer(folded):
        if run.end() <= end:
            continue
        for start in (end,) if run.start() < end else (run.start() - 1, run.start()):
            if start >= end and (match := pattern.match(folded, start)) is not None:
                yield match
                end = match.end()
                break


def _affixed_matches(pattern: re.Pattern, text: str, data) -> Iterator[tuple[re.Match, int, int, str, str]]:
    """Matches in the folded text, each with its declared affixes, the start and the end of the span, that no
    word character, digit or cluster mark continues on either side."""
    for match in digit_run_matches(pattern, fold_digits(text)):
        bounds = _affixes(text, *match.span(), data)
        start, end, prefix, suffix = bounds if bounds is not None else (*match.span(), "", "")
        if _edge(text, start, end):
            yield match, start, end, prefix, suffix


def _unit_after(text: str, end: int, units: Iterable[str]) -> bool:
    """Whether a unit of the language follows text[:end], attached or after one space."""
    return any(text.startswith(gap + unit, end) and is_bounded(text, end + len(gap), end + len(gap) + len(unit))
               for gap in GAPS for unit in units)


@dataclass(frozen=True)
class Fraction:
    name: str = "fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A symbol of the language next to the fraction or a unit after it leaves a reading that is not clear,
        as in `$5/6` and `3/4 kg`, so the fraction stays as written, as do digits from two digit sets."""
        symbols = request.data.get("symbols", FrozenMap())
        units = request.data.get("units", FrozenMap())
        for match, start, end, prefix, suffix in _affixed_matches(_FRACTION, text, request.data):
            written = match.group()
            sign = "-" if written[0] in "-−" else "+" if written[0] == "+" else ""
            numerator, denominator = written.lstrip("-+−").split("/")
            if sign and match.start() > 0 and is_word_char(text[match.start() - 1]):
                continue
            unclear = (not (_free_before(text, start, symbols) and _free_after(text, end, symbols))
                       or _unit_after(text, end, units) or not one_digit_set(text[match.start():match.end()]))
            top, bottom = bounded_integer(numerator), bounded_integer(denominator)
            if unclear or (bottom is not None and 2 <= bottom <= 100 and top is not None and top < bottom):
                yield Span(start, end, Form.FRACTION,
                           FrozenMap({"numerator": numerator, "denominator": denominator, "sign": sign,
                                      "prefix": prefix, "suffix": suffix}), recognizer=self.name, keep=unclear)


@dataclass(frozen=True)
class Idiom:
    name: str = "idiom"
    form: Form = Form.IDIOM

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for key in request.data.get("idioms", FrozenMap()):
            position = text.find(key)
            while position != -1:
                end = position + len(key)
                bounds = _affixes(text, position, end, request.data, ())
                if bounds is not None and not (bounds[1] < len(text) and text[bounds[1]] == "/"):
                    start, stop, prefix, suffix = bounds
                    yield Span(start, stop, Form.IDIOM, FrozenMap({"key": key, "prefix": prefix, "suffix": suffix}),
                               recognizer=self.name)
                position = text.find(key, end)


@dataclass(frozen=True)
class Range:
    name: str = "range"
    form: Form = Form.RANGE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """Two numbers that a mark of the `range_marks` table joins. A pair that does not go up, as in `2024-25`,
        and digits from two digit sets keep the whole range as written."""
        marks = request.data.get("range_marks", ())
        if not marks:
            return
        mark = "|".join(map(re.escape, marks))
        for match, start, end, prefix, suffix in _affixed_matches(re.compile(f"[0-9]+(?:{mark})[0-9]+"), text,
                                                                  request.data):
            low, high = re.split(mark, match.group())
            low_value, high_value = bounded_integer(low), bounded_integer(high)
            descending = high_value is not None and (low_value is None or low_value >= high_value)
            yield Span(start, end, Form.RANGE,
                       FrozenMap({"low": low, "high": high, "prefix": prefix, "suffix": suffix}), recognizer=self.name,
                       keep=descending or not one_digit_set(text[match.start():match.end()]))


@dataclass(frozen=True)
class DateNumeric:
    name: str = "date_numeric"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        folded = fold_digits(text)
        for match in digit_run_matches(_DATE, folded):
            start, end = match.span()
            if not (_cluster_edge(text, start, end) and one_digit_set(text[start:end])):
                continue
            fields = tuple(re.split("[/.-]", match.group()))
            resolved = resolve_date(fields, request.params.date_order)
            bounds = _affixes(text, match.start(), match.end(), request.data)
            if resolved is None or bounds is None:
                continue
            year, month, day, order = resolved
            start, end, prefix, suffix = bounds
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": order,
                                  "month_written": "digits", "prefix": prefix, "suffix": suffix}),
                       recognizer=self.name)


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

    The `clock_marks` table gives each mark between the hour and the minutes, whether a seconds field may follow
    with the same mark, and the evidence that the time needs: `evidence` (a time word, a time suffix or a day
    period), `day_period` (a written day period, as for `9.30 am` in English, where `9.30` alone is a decimal) or
    `none` (the mark itself, as for `14h30` in Portuguese). A mark with `closes_hour` may also close an hour with
    no minutes, as for `14h` in Portuguese. A seconds field is no evidence, because a duration such as `1:23:45`
    has one. Any other hour with no minutes needs a written day period, as in `9am`.

    A word of `weak_time_words`, such as `by` in `by 5:45`, is evidence for hours and minutes only: `ran by
    1:23:45` has a seconds field, so it stays a duration. A word of `cued_time_words`, such as `for`, is evidence
    for hours and minutes only when one of `time_cue_words` stands within three words of the time in its clause,
    as `tomorrow` does in `set for 7:30 tomorrow morning`: `bake for 1:30` is a duration."""
    name: str = "time_clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._times(text, tokens, request), text, request)

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        words = context_words(tokens)
        breaks = clause_breaks(text)
        time_words = frozenset(w.lower() for w in data.get("time_words", ()))
        weak_words = frozenset(w.lower() for w in data.get("weak_time_words", ()))
        cued_words = frozenset(w.lower() for w in data.get("cued_time_words", ()))
        cue_words = frozenset(w.lower() for w in data.get("time_cue_words", ()))
        periods = data.get("day_periods", FrozenMap())
        suffixes = data.get("time_suffixes", ())
        folded = fold_digits(text)
        clocks = []
        for clock in data.get("clock_marks", ()):
            mark = re.escape(clock["mark"])
            minutes = "[0-9][0-9]" + (f"(?:{mark}[0-9][0-9])?" if clock["seconds"] else "")
            if clock.get("closes_hour", False):
                minutes = f"(?:{minutes})?"
            clocks.append((re.compile(f"[0-9][0-9]?{mark}{minutes}"), clock["mark"], clock["needs"]))
        for pattern, mark, needs in (*clocks, (_HOUR, "", "day_period")):
            for match in pattern.finditer(folded):
                start, end = match.span()
                if (not _cluster_edge(text, start, end) or (start and is_word_char(text[start - 1]))
                        or not one_digit_set(text[start:end])):
                    continue
                if mark:
                    parts = match.group().split(mark)
                    fields = clock_fields(parts[0], parts[1] or "00", parts[2] if len(parts) == 3 else None)
                else:
                    fields = (int(match.group()), 0, None)
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
                elif needs == "day_period":
                    continue
                suffix = next((s for s in suffixes if text.startswith(s, end)), "")
                if end + len(suffix) < len(text) and is_word_char(text[end + len(suffix)]):
                    continue
                before = clause_window(text, words, start, end, -1, limit=1, breaks=breaks)
                weak = second is None and bool(before) and (
                    before[0].lower() in weak_words
                    or (before[0].lower() in cued_words and any(
                        word.lower() in cue_words for direction in (-1, 1) for word in clause_window(
                            text, words, start, end, direction, limit=3, breaks=breaks))))
                if not (needs == "none" or period is not None or suffix
                        or (before and before[0].lower() in time_words) or weak):
                    continue
                yield Span(start, end + len(suffix), Form.TIME,
                           FrozenMap({"hour": hour, "minute": minute, "second": second, "period": period,
                                      "suffix": suffix}), trail=trail, recognizer=self.name)


@dataclass(frozen=True)
class Percent:
    """`20%`, and `10%-20%`, where a dash alone between two percentages reads the range word. A dash right after
    a percent sign is no minus sign."""
    name: str = "percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._percents(text, request), text, request)

    def _percents(self, text: str, request: Request) -> Iterator[Span]:
        percent = request.data.get("percent")
        if percent is None:
            return
        for number in numbers_in(text, request):
            if number.sign and any(text.endswith(sign, 0, number.start) for sign in percent["signs"]):
                number = replace(number, start=number.start + 1, sign="")
            if percent["position"] in ("after", "either"):
                for sign in percent["signs"]:
                    for gap in GAPS:
                        end = number.end + len(gap) + len(sign)
                        if text.startswith(gap + sign, number.end) \
                                and (bounds := _affixes(text, number.start, end, request.data, ())) is not None:
                            yield Span(bounds[0], bounds[1], Form.PERCENT,
                                       FrozenMap({"amount": number.amount(), "sign_position": "after",
                                                  "prefix": bounds[2], "suffix": bounds[3]}), recognizer=self.name)
            if percent["position"] in ("before", "either"):
                for sign in percent["signs"]:
                    start = number.start - len(sign)
                    if start >= 0 and text[start:number.start] == sign \
                            and (bounds := _affixes(text, start, number.end, request.data, ())) is not None:
                        yield Span(bounds[0], bounds[1], Form.PERCENT,
                                   FrozenMap({"amount": number.amount(), "sign_position": "before",
                                              "prefix": bounds[2], "suffix": bounds[3]}), recognizer=self.name)


@dataclass(frozen=True)
class Money:
    name: str = "money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._amounts(text, tokens, request), text, request)

    def _amounts(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A currency symbol before or after a number. Before a symbol that comes first, a sign may stand, and
        after its number a scale word of the language, attached or after one space: `-$5`, `$2 million`, `$1m`."""
        symbols = [(symbol, code) for code, currency in request.data.get("currencies", FrozenMap()).items()
                   for symbol in currency["symbols"]]
        scales = sorted(request.data.get("scales", FrozenMap()), key=len, reverse=True)
        for number in numbers_in(text, request):
            for symbol, code in sorted(symbols, key=lambda pair: len(pair[0]), reverse=True):
                found = None
                for gap in GAPS:
                    start = number.start - len(gap) - len(symbol)
                    if not number.sign and start >= 0 and text[start:number.start] == symbol + gap:
                        sign = SIGNS.get(text[start - 1], "") if start else ""
                        if sign and _free_before(text, start - 1, ()):
                            start -= 1
                        else:
                            sign = ""
                        scale, end = _scale(text, number.end, scales)
                        bounds = _affixes(text, start, end, request.data, ())
                        if bounds is not None:
                            found = (bounds, sign, scale)
                            break
                    end = number.end + len(gap) + len(symbol)
                    if text.startswith(gap + symbol, number.end) \
                            and (bounds := _affixes(text, number.start, end, request.data, ())) is not None:
                        found = (bounds, number.sign, "")
                        break
                if found:
                    (start, end, prefix, suffix), sign, scale = found
                    yield Span(start, end, Form.MONEY,
                               FrozenMap({"amount": FrozenMap({**number.amount(), "sign": sign}), "currency": code,
                                          "written_symbol": symbol, "scale": scale, "prefix": prefix,
                                          "suffix": suffix}), recognizer=self.name)
                    break


def _scale(text: str, end: int, scales: Sequence[str]) -> tuple[str, int]:
    """The scale word written after text[:end], attached or after one space, and the end of the span."""
    for gap in GAPS:
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
        units = sorted(data.get("units", FrozenMap()), key=len, reverse=True)
        relations = {"dimension": data.get("dimension_marks", ()), "range": data.get("range_marks", ())}
        every_mark = tuple(mark for marks in relations.values() for mark in marks)
        numbers = numbers_in(text, request)
        by_start = {n.start: n for n in numbers}
        for index, number in enumerate(numbers):
            before = _prefix(text, number.start, data)
            if before is None or (index and _linked(text, numbers[index - 1].end, every_mark, by_start) is number):
                continue
            amounts, end, relation = [number], number.end, ""
            for kind, marks in relations.items():
                while relation in ("", kind) and (following := _linked(text, end, marks, by_start)) is not None:
                    relation = kind
                    amounts.append(following)
                    end = following.end
            for gap in GAPS:
                unit = next((u for u in units if text.startswith(gap + u, end)
                             and _suffix(text, end + len(gap) + len(u), data) is not None
                             and not _per_unit(text, end + len(gap) + len(u))
                             and not _elided(text, end + len(gap) + len(u))), None)
                if unit is not None:
                    stop, suffix = _suffix(text, end + len(gap) + len(unit), data)
                    amount = amounts[0].amount() if len(amounts) == 1 else tuple(a.amount() for a in amounts)
                    yield Span(before[0], stop, Form.MEASURE,
                               FrozenMap({"amount": amount, "relation": relation, "unit": unit,
                                          "prefix": before[1], "suffix": suffix}), recognizer=self.name)
                    break


def _per_unit(text: str, end: int) -> bool:
    """Whether a slash and a letter continue a unit, as in `m/s` when the table holds only `m`."""
    return end + 1 < len(text) and text[end] == "/" and is_letter(text[end + 1])


def _elided(text: str, end: int) -> bool:
    """Whether an apostrophe and a letter continue a unit, as in `l'eau` after `3 l`: the unit is a word that
    elides, not a symbol."""
    return end + 1 < len(text) and text[end] in "'\u2019" and is_letter(text[end + 1])


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
    region in `phone_regions`, a shape of the `phone_shapes` table, as in `(212) 555-0123`, or a phone word that
    names the run.

    A phone word names the run right after it, with no letter or digit between them. A run that a word of
    `list_links` or a comma joins to a named run is named too, as `112` in `Call 999 or 112.` Readings only add
    words before a run, so a run that a first pass leaves unnamed stays unnamed on a second pass.

    A named run of 7 to 15 digits reads digit by digit. A shorter named run reads digit by digit only when it is a
    short code, so `Call 100 customers.` reads a count. A run right after a phone word that no plan reads stays as
    written: a run after `+` with no known country code, as in `Call +999.`, a run of more than 15 digits, and a
    phone-shaped run, a short code or a run of 7 or more digits that a letter, or a joiner or an operator and a
    digit, continue, as in `Call 0800 123 456/7.` and `Call 112+1.` The kept run takes the digits that joiners
    chain to it, but not a group that a letter continues. Such a run is never named further back, so
    `Call 911 or 112+1.` reads the expression. A run with digits from two digit sets stays as written.

    Three tables of regexes hold the written shapes of a language. A run that a shape of `phone_unit_shapes`
    matches whole reads digit by digit as one unit with no other evidence. A run that a shape of
    `phone_kept_shapes` matches whole stays as written when it has no phone reading. A run that a shape of
    `no_phone_shapes` matches whole has no phone shape.

    A language file that names phone numbers by context of its own subclasses this recognizer and replaces the
    methods `trimmed`, `window` and `names_back`, as `EnglishTelephone` does."""
    name: str = "telephone"
    form: Form = Form.TELEPHONE

    def trimmed(self, text: str, start: int, written: str, request: Request) -> str:
        """The run that `_PHONE` matched at `start`, less a last group that the language reads apart."""
        return written

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        """The indices of the words that may hold a phone word for the run: the word right before it."""
        index = bisect_right(words, start, key=lambda word: word.end)
        return range(index - len(clause_window(text, words, start, end, -1, limit=1, breaks=breaks)), index)

    def names_back(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
                   shaped: bool, short_code: bool, request: Request) -> bool:
        """Whether a phone word of the window that is not right before the run names it."""
        return False

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        words = context_words(tokens)
        breaks = clause_breaks(text)
        phone_words = frozenset(w.lower() for w in request.data.get("phone_words", ()))
        shapes = [re.compile(shape) for shape in request.data.get("phone_shapes", ())]
        unit_shapes = [re.compile(shape) for shape in request.data.get("phone_unit_shapes", ())]
        kept_shapes = [re.compile(shape) for shape in request.data.get("phone_kept_shapes", ())]
        no_shapes = [re.compile(shape) for shape in request.data.get("no_phone_shapes", ())]
        short_codes = frozenset(request.data.get("short_codes", ()))
        codes = sorted((plan["country_code"] for plan in PHONE_PLANS.values()), key=len, reverse=True)
        plans = [PHONE_PLANS[r] for r in sorted(request.params.phone_regions or ()) if r in PHONE_PLANS]
        links = "|".join(map(re.escape, request.data.get("list_links", ())))
        listed = re.compile(f",? (?:{links}) |, " if links else ", ")
        operators = "".join(request.data.get("operators", ()))
        operand = re.compile(f"[{re.escape(operators)}][0-9]") if operators else None
        named_end = None
        folded = fold_digits(text)
        kept_end = 0
        for match in _PHONE.finditer(folded):
            if match.start() < kept_end:
                continue
            start = match.start()
            written = self.trimmed(text, start, match.group(), request)
            end = start + len(written)
            glued = not _edge(text, start, end) or (operand is not None and operand.match(folded, end) is not None)
            prefix = suffix = ""
            if glued and (bounds := _affixes(text, start, end, request.data)) is not None \
                    and (bounds[2] or bounds[3]) and _edge(text, bounds[0], bounds[1]) \
                    and (operand is None or operand.match(folded, bounds[1]) is None):
                glued, prefix, suffix = False, bounds[2], bounds[3]
            groups = [group for group in re.split("[ \u00a0\u202f.()-]", written.lstrip("+")) if group]
            digits = "".join(groups)
            shaped = not any(shape.fullmatch(written) for shape in no_shapes) and (
                written.startswith("+") or digits.startswith("0") or any(c in " \u00a0\u202f.()-" for c in written))
            phone_ends = [words[i].end for i in self.window(text, words, breaks, start, end, request)
                          if words[i].text.lower() in phone_words]
            direct = bool(phone_ends) and not any(map(is_word_char, text[phone_ends[-1]:start - len(prefix)]))
            country_code = ""
            if written.startswith("+"):
                if len(groups) > 1 and len(groups[0]) <= 3:
                    country_code, groups = groups[0], groups[1:]
                else:
                    country_code = next((c for c in codes if groups[0].startswith(c)), "")
                    groups[0] = groups[0][len(country_code):]
            short_code = "".join(groups) in short_codes
            named = (direct
                     or (bool(phone_ends) and self.names_back(text, words, breaks, start, end, shaped, short_code,
                                                               request))
                     or (named_end is not None and listed.fullmatch(text[named_end:start]) is not None))
            named_end = end + len(suffix) if named else None
            unknown_code = written.startswith("+") and not country_code
            if glued:
                if not (direct and len(digits) >= 3 and (shaped or short_code or len(digits) >= 7)):
                    continue
                chained = _GLUED.match(folded, end).group()
                if chained and end + len(chained) < len(text) and is_word_char(text[end + len(chained)]):
                    chained = re.sub("[ /:.,–-]?[0-9]+$", "", chained)
                end = kept_end = named_end = end + len(chained)
            first, last = start - len(prefix), end + len(suffix)
            written_only = FrozenMap({"country_code": "", "groups": tuple(groups), "prefix": prefix, "suffix": suffix})
            if glued or not one_digit_set(text[start:end]) or (direct and (len(digits) > 15 or unknown_code)):
                yield Span(first, last, Form.TELEPHONE, written_only, recognizer=self.name, keep=True)
                continue
            if any(shape.fullmatch(written) for shape in unit_shapes):
                yield Span(first, last, Form.TELEPHONE, written_only, recognizer=self.name)
                continue
            if unknown_code or len(digits) > 15:
                reads = False
            elif 7 <= len(digits):
                reads = (named or bool(country_code) or any(shape.fullmatch(written) for shape in shapes)
                         or (any(digits[2:].startswith(code) for code in codes) if digits.startswith("00")
                             else any(plan["trunk"] and digits.startswith(plan["trunk"])
                                      and len(digits) - len(plan["trunk"]) in plan["lengths"] for plan in plans)))
            else:
                reads = named and short_code
            if reads:
                yield Span(first, last, Form.TELEPHONE,
                           FrozenMap({"country_code": country_code, "groups": tuple(groups), "prefix": prefix,
                                      "suffix": suffix}), recognizer=self.name)
            elif any(shape.fullmatch(written) for shape in kept_shapes):
                yield Span(first, last, Form.TELEPHONE, written_only, recognizer=self.name, keep=True)


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


@dataclass(frozen=True)
class OrdinalStop:
    """A digit run and a full stop that a letter follows, as in `1.º` and `1.er`. With `bare_stop`, also a full
    stop that a space and more text follow, as in `am 3. Mai`: the CLDR root rule `digits-ordinal`, `=#,##0=.`,
    writes an ordinal as the number and a full stop, and a locale with no rule of its own keeps it. There, the
    stop does not tell an ordinal from the end of a sentence."""
    bare_stop: bool = False
    name: str = "ordinal_stop"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            stop = number.end
            if number.fraction is not None or not text.startswith(".", stop) \
                    or not _cluster_edge(text, number.start, stop):
                continue
            end = stop + 1
            while end < len(text) and (is_letter(text[end]) or is_mark(text[end])):
                end += 1
            if end > stop + 1 or (self.bare_stop and text[end:end + 1].isspace() and next_visible(text, end)):
                yield Span(number.start, end, Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": text[stop:end], "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Written:
    """The spans of a shape recognizer, kept as written. A language with no file reads no money, percent,
    measure, numeric date or ordinal, so these spans claim the digits of each such form before the cardinal
    recognizer reads them (section 6.1). The form is `CARDINAL`, the reading that the spans guard."""
    shape: Recognizer
    form: Form = Form.CARDINAL

    @property
    def name(self) -> str:
        return self.shape.name

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return (replace(span, keep=True) for span in self.shape.find(text, tokens, request))


UNIT_SYMBOLS = ("km", "cm", "mm", "µm", "nm", "kg", "mg", "µg", "ml", "mL", "cl", "cL", "dl", "dL", "km/h", "m/s",
                "m²", "m³", "km²", "cm²", "cm³", "mm²", "kWh", "Wh", "kW", "MW", "GW", "mAh", "Hz", "kHz", "MHz",
                "GHz", "kJ", "kPa", "hPa", "°C", "°")
"""Unit symbols that every language writes the same way. A one-letter symbol is a word in some language, as `s`
and `v` are in Slovene, so none is here."""


@lru_cache(maxsize=1)
def written_shapes() -> FrozenMap:
    """The tables of the shape recognizers for a language with no file: every currency symbol of the Unicode
    Basic Multilingual Plane, the percent and per mille signs, and the unit symbols."""
    currencies = tuple(char for char in map(chr, range(0x10000)) if unicodedata.category(char) == "Sc")
    percent = ("%", "٪", "‰")
    return FrozenMap({
        "currencies": FrozenMap({"Sc": FrozenMap({"symbols": currencies})}),
        "percent": FrozenMap({"signs": percent, "position": "either"}),
        "units": FrozenMap((unit, FrozenMap()) for unit in UNIT_SYMBOLS),
        "symbols": FrozenMap({**{c: "money" for c in currencies}, **{s: "percent" for s in percent}, "°": "measure"}),
    })


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 (section 4.2): after a year word, as in `In 1984`; two years that a range mark
    joins, the lower one first, as in `1939-1945`, or a year and a higher two-digit end after a year word, as in
    `during 1939-45`; and a number that a link joins to a year, as in `In 1066 and 1215`. A comma alone links
    only inside a list that a link word ends, as in `In 1066, 1215 and 1415`.

    A count read as a year is wrong, so the follower of a linked list decides for all its years, and a range is
    one link of a list. A lowercase word that is not in `function_words` blocks them, as in `in 1234 steps`, and
    so do a unit of the units table in any case, an operator and a dimension mark, as in `in 2048 MB` and
    `in 1920 × 1080`."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._years(text, tokens, request), text, request)

    def _years(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        year_words = frozenset(data["year_words"])
        function_words = frozenset(data["function_words"])
        marks = frozenset(data["range_marks"])
        units = frozenset(unit.lower() for unit in data["units"])
        signs = frozenset(data["operators"]) | frozenset(data["dimension_marks"]) | {"*", "/"}
        word_link = re.compile(",? (?:" + "|".join(map(re.escape, data["year_links"])) + ") ")
        words = context_words(tokens)
        breaks = clause_breaks(text)
        numbers = [n for n in numbers_in(text, request) if not n.sign and n.fraction is None
                   and n.end - n.start in (2, 4) and is_bounded(text, n.start, n.end)]

        def year(number: Number) -> bool:
            return number.end - number.start == 4 and 1000 <= int(number.integer) <= 2099

        def after_year_word(number: Number) -> bool:
            before = clause_window(text, words, number.start, number.end, -1, limit=1, breaks=breaks)
            return bool(before) and before[0].lower() in year_words

        def free(end: int) -> bool:
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
            if start in (end, len(text)):
                return True
            stop = start
            while stop < len(text) and not text[stop].isspace():
                stop += 1
            follower = text[start:stop].rstrip(".,;:!?)")
            if (text[start] in signs and not is_letter(text[start])) or follower.lower() in units:
                return False
            stop = start
            while stop < len(text) and is_letter(text[stop]):
                stop += 1
            word = text[start:stop]
            return not word.islower() or word in function_words

        claimed = {}
        partners = {}
        for first, second in zip(numbers, numbers[1:]):
            if not (year(first) and text[first.end:second.start] in marks):
                continue
            if year(second) and int(first.integer) < int(second.integer):
                claimed |= {first: first.integer, second: second.integer}
                partners |= {first: second, second: first}
            elif (second.end - second.start == 2 and int(first.integer) % 100 < int(second.integer)
                  and after_year_word(first)):
                claimed |= {first: first.integer, second: first.integer[:2] + second.integer}
                partners |= {first: second, second: first}
        chains: list[list[Number]] = []
        for number in numbers:
            if not (year(number) or number in claimed):
                continue
            gap = text[chains[-1][-1].end:number.start] if chains else ""
            if chains and (gap == ", " or word_link.fullmatch(gap) or partners.get(number) is chains[-1][-1]):
                chains[-1].append(number)
            elif number in claimed or after_year_word(number):
                chains.append([number])
        for chain in chains:
            while len(chain) > 1 and text[chain[-2].end:chain[-1].start] == ", ":
                chain.pop()
            if free(chain[-1].end):
                claimed |= {number: number.integer for number in chain if number not in claimed}
            else:
                for number in chain:
                    claimed.pop(number, None)
        for number, digits in claimed.items():
            yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": digits, "suffix": ""}),
                       recognizer=self.name)


@dataclass(frozen=True)
class Expression:
    """`5+3`, `2 × 2 = 4`, `-2+3=1`: operators between integers, with no letter on either side. The first
    integer may carry a minus sign. `−` is both that sign and an operator: `−3−3` is "minus three minus three".

    An operator right after the last integer stays with the expression, so `1+1 × 10%` keeps `1+1 ×` as
    written: the percentage claims `10`, and a second pass finds `1+1 × ten` with the same open operator.

    Only the first integer may carry a sign, and no form reads a number next to a symbol of the `symbols` table.
    So a signed later operand, as in `3 − −3`, and a symbol next to the expression, as in `$−3+3`, keep the
    expression as written."""
    name: str = "expression"
    form: Form = Form.EXPRESSION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        operators = re.escape("".join(request.data["operators"]))
        open_operator = re.compile(f" ?[{operators}]")
        symbols = request.data["symbols"]
        for match in digit_run_matches(request.data["patterns"]["expression"], fold_digits(text)):
            start, end = match.span()
            if (not (is_bounded(text, start, end) and one_digit_set(text[start:end]))
                    or open_operator.match(text, end)):
                continue
            written = match.group().replace(" ", "")
            first = re.match("[-−]?[0-9]+", written).group()
            signs, others = zip(*re.findall(f"([{operators}])([-−]?[0-9]+)", written[len(first):]))
            unclear = (any(not operand[0].isdigit() for operand in others)
                       or (start > 0 and text[start - 1] in symbols) or (end < len(text) and text[end] in symbols))
            yield Span(start, end, Form.EXPRESSION, FrozenMap({"operands": (first, *others), "operators": signs}),
                       recognizer=self.name, keep=unclear)


LEXICON = Lexicon()
CARDINAL = Cardinal()
SHARED = {r.name: r for r in (LEXICON, CARDINAL, Decimal(), Fraction(), Idiom(), Range(), DateNumeric(), TimeClock(),
                              Percent(), Money(), Measure(), Telephone(), COLOR, Year(), Expression())}
"""The shared recognizers by name."""
