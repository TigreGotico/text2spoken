"""The shared recognizers, each with a name (design sections 4.2, 4.3, 5.3).

A recognizer reads characters, not tokens: money, telephone numbers and colours cross token gaps. Each
regular expression here uses the portable subset of section 8, and runs on the text with its digits folded to
ASCII, which keeps every offset.
"""
from __future__ import annotations

import re
import unicodedata
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from types import MappingProxyType

from text2spoken.core.color import COLOR
from text2spoken.core.currencies import currency_symbols
from text2spoken.core.dates import resolve as resolve_date
from text2spoken.core.electronic import ELECTRONIC
from text2spoken.core.emoji import sequences_in, touched_words, written_text
from text2spoken.core.language import Request, lexicon_entries
from text2spoken.core.letters import LETTERS
from text2spoken.core.numbers import SIGNS, Number, declared_marks, find_numbers, group_spaces, number_marks
from text2spoken.core.spans import (Features, Recognizer, SpanContext, Span, Word, clause_breaks, clause_window,
                                    context_words)
from text2spoken.core.spellers import bounded_integer, spell_digits
from text2spoken.core.symbols import EMOJI, SYMBOL, named_pieces
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import (EMOJI_MARKS, Token, context_word, digit_script, fold_digits, is_bounded, is_digit,
                                     is_letter, is_mark, is_word_char, next_visible, one_digit_set)
from text2spoken.core.units import joined_table, unit_table, units_at
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
        request.memo[key] = find_numbers(text, number_marks(request.data, request.params.decimal_mark),
                                         declared_marks(request.data))
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
        """The caller's keys match the text as written, so a key such as `#️⃣` matches. An emoji sequence that holds
        U+FE0E, U+FE0F or U+20E3 is one character, as `😀` is. A match neither starts nor ends inside it, so a key `1`
        leaves the `1` of `1️⃣`. Next to a key, the sequence is no word character, so a key `x` matches in `1️⃣x` as
        in `😀x`. A sequence that touches a word stays as written with that word (`touched_words`), so there it is a
        word character, and no match starts or ends inside the word or the sequence: a key `A` does not match in
        `A1️⃣`, the keys `org` and `x.org` do not match in `x.org1️⃣`, and a key `cats` does not match in `2,cats1️⃣`.
        A key `2` matches there, and the view keeps that `2` too."""
        entries = lexicon_entries(request.tag, request.params.lexicon)
        by_first = _keys_by_first_character(entries)
        text = written_text(text, request)
        sequences = [(start, end) for start, end in sequences_in(text, request.memo)
                     if any(char in EMOJI_MARKS for char in text[start:end])]
        touched = {start for _, start, _ in touched_words(text, request.memo)}
        inside = {index for start, end in sequences for index in range(start + 1, end)}
        apart = {start for start, _ in sequences} - touched

        def limit(index: int) -> bool:
            return index in apart or _lexicon_limit(text, index)

        position = 0
        while position < len(text):
            key = next((k for k in by_first.get(text[position], ()) if text.startswith(k, position)
                        and position not in inside and position + len(k) not in inside
                        and limit(position - 1) and limit(position + len(k))), None)
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


_DASHES = "-\u2010\u2011\u2012\u2013\u2014\u2212"
"""The hyphen, the dashes and the minus sign."""


@dataclass(frozen=True)
class RbnfCardinal(Cardinal):
    """The cardinal of a language with no file (section 6.1). A number with a minus stays as written where the
    minus may mark something else, or where the number goes on past the span: a list item at the start of a line,
    as in `-3 mele`; a range or a code after a number or a dash, as in `5 -10`, `5--10` and `333 -1234567`; an
    amount next to a symbol of `symbols`, which the language keeps as written, as in `-50 €` and `€ -50`; or a
    number grouped with a space, as in `-1 000`, where the span holds only the first group. A number that a space
    alone parts from such a minus number stays as written too, so that a second pass finds the digit next to the
    minus again (section 11): `5` in `5 -10`, and `000` in `-1 000`. A dash is no digit, so `5` in `5--10` reads."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        symbols = request.data.get("symbols", FrozenMap())
        spans = list(super().find(text, tokens, request))
        kept = set()
        for index, span in enumerate(spans):
            if not span.fields["sign"]:
                continue
            sign = span.start + len(span.fields["prefix"])
            line_start = text.rfind("\n", 0, sign) + 1
            before = text[line_start:sign].rstrip()
            number_end = span.end - len(span.fields["suffix"])
            after = text[number_end:].lstrip()
            neighbours = []
            if before and is_digit(before[-1]):
                neighbours.append((index - 1, line_start + len(before) - 1))
            if text[number_end:number_end + 1].isspace() and after and is_digit(after[0]):
                neighbours.append((index + 1, len(text) - len(after)))
            if neighbours or not before or before[-1] in _DASHES or before[-1] in symbols or after[:1] in symbols:
                kept.add(index)
            for other, digit in neighbours:
                if 0 <= other < len(spans) and spans[other].start <= digit < spans[other].end:
                    kept.add(other)
        return (replace(span, keep=True) if index in kept else span for index, span in enumerate(spans))


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
_GLUED = re.compile("(?:[ /:.,–-]?[0-9]+)*")
_DIGIT_RUN = re.compile("[0-9]+")


@lru_cache(maxsize=8)
def _phone_pattern(spaces: str) -> re.Pattern:
    """A run of digit groups that a space of `spaces`, a full stop or a hyphen parts, with an optional `+` and an
    area code in brackets."""
    return re.compile(f"[+]?(?:[(][0-9]+[)] ?)?[0-9]+(?:[{re.escape(spaces)}.-][0-9]+)*")


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


def grouped_matches(pattern: re.Pattern | str, text: str, request: Request) -> Iterator[tuple[str, int, int]]:
    """The matches of `digit_run_matches` in the folded text, each as the text it matched and its span in `text`.

    The pattern reads the text without the spaces that `find_numbers` reads as group marks (`group_spaces`), so a
    `[0-9]+` of the pattern reads `1 000` whole, as `find_numbers` does: `1 000-2 000` is one range of two numbers,
    and no match starts or ends inside `1 000`. A language with no space in a run of group marks reads the folded
    text as it is."""
    key = ("grouped", text)
    if key not in request.memo:
        folded = fold_digits(text)
        spaces = frozenset(group_spaces(text, number_marks(request.data, request.params.decimal_mark),
                                        declared_marks(request.data)))
        kept = tuple(i for i in range(len(text)) if i not in spaces)
        request.memo[key] = ("".join(folded[i] for i in kept), kept) if spaces else (folded, None)
    view, kept = request.memo[key]
    for match in digit_run_matches(pattern, view):
        start, end = match.span()
        if kept is not None:
            start, end = kept[start], kept[end - 1] + 1
        yield match.group(), start, end


def _affixed_matches(pattern: re.Pattern, text: str, request: Request) \
        -> Iterator[tuple[str, int, int, int, int, str, str]]:
    """The matches of `grouped_matches`, each with the span it matched, and the start and the end of the span with
    its declared affixes, which no word character, digit or cluster mark continues on either side."""
    for written, matched_start, matched_end in grouped_matches(pattern, text, request):
        bounds = _affixes(text, matched_start, matched_end, request.data)
        start, end, prefix, suffix = bounds if bounds is not None else (matched_start, matched_end, "", "")
        if _edge(text, start, end):
            yield written, matched_start, matched_end, start, end, prefix, suffix


GAPS = ("", " ", "\u00a0")
"""The gaps that may stand between a number and its unit, symbol, percent sign or scale word: none, a space and a
no-break space. A language that writes other gaps lists them all in `number_gaps`."""


def number_gaps(data) -> tuple[str, ...]:
    """The gaps of the language between a number and its unit, symbol, percent sign or scale word."""
    return tuple(data.get("number_gaps", GAPS))


def _unit_after(text: str, end: int, units: Iterable[str], gaps: Sequence[str] = GAPS) -> bool:
    """Whether a unit of the language follows text[:end], attached or after one gap."""
    return any(text.startswith(gap + unit, end) and is_bounded(text, end + len(gap), end + len(gap) + len(unit))
               for gap in gaps for unit in units)


@dataclass(frozen=True)
class Fraction:
    name: str = "fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A symbol of the language next to the fraction or a unit after it leaves a reading that is not clear,
        as in `$5/6` and `3/4 kg`, so the fraction stays as written, as do digits from two digit sets."""
        symbols = request.data.get("symbols", FrozenMap())
        units = unit_table(request)
        for written, matched_start, matched_end, start, end, prefix, suffix in _affixed_matches(_FRACTION, text,
                                                                                                 request):
            sign = "-" if written[0] in "-−" else "+" if written[0] == "+" else ""
            numerator, denominator = written.lstrip("-+−").split("/")
            if sign and matched_start > 0 and is_word_char(text[matched_start - 1]):
                continue
            unclear = (not (_free_before(text, start, symbols) and _free_after(text, end, symbols))
                       or _unit_after(text, end, units, number_gaps(request.data))
                       or not one_digit_set(text[matched_start:matched_end]))
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
        for written, matched_start, matched_end, start, end, prefix, suffix in _affixed_matches(
                re.compile(f"[0-9]+(?:{mark})[0-9]+"), text, request):
            low, high = re.split(mark, written)
            low_value, high_value = bounded_integer(low), bounded_integer(high)
            descending = high_value is not None and (low_value is None or low_value >= high_value)
            yield Span(start, end, Form.RANGE,
                       FrozenMap({"low": low, "high": high, "prefix": prefix, "suffix": suffix}), recognizer=self.name,
                       keep=descending or not one_digit_set(text[matched_start:matched_end]))


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
    has one. Any other hour with no minutes needs a written day period, as in `9am`."""
    name: str = "time_clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._times(text, tokens, request), text, request)

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        words = context_words(tokens)
        breaks = clause_breaks(text)
        time_words = frozenset(w.lower() for w in data.get("time_words", ()))
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
                if not (needs == "none" or period is not None or suffix
                        or (before and before[0].lower() in time_words)):
                    continue
                yield Span(start, end + len(suffix), Form.TIME,
                           FrozenMap({"hour": hour, "minute": minute, "second": second, "period": period,
                                      "prefix": "", "suffix": suffix}), trail=trail, recognizer=self.name)


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
                    for gap in number_gaps(request.data):
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
    """With `scale_before_symbol`, a scale word may also stand between a number and a symbol after it, as in
    `180 mil €`."""
    name: str = "money"
    form: Form = Form.MONEY
    scale_before_symbol: bool = False

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._amounts(text, tokens, request), text, request)

    def _amounts(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A currency symbol before or after a number. Before a symbol that comes first, a sign may stand, and
        after its number a scale word of the language, attached or after one space: `-$5`, `$2 million`, `$1m`.

        Each symbol next to a number gives a candidate, before the number and after it, and the claim takes the first
        that no earlier span holds. So a symbol that one amount reads is not the symbol of the next number: in
        `5 R$ 10£` the second amount is `10£`. A symbol that a phone number holds is still free for the amount after
        it: `Call 999 £ 5 now.` reads "five pounds". A number with a decimal comma in a variety with the decimal
        point reads only next to `€` (`_comma_decimals`)."""
        every_symbol = currency_symbols(request)
        euro = tuple((symbol, code) for symbol, code in every_symbol if code == "EUR")
        scales = sorted(request.data.get("scales", FrozenMap()), key=len, reverse=True)
        numbers = [(number, every_symbol) for number in self.numbers(text, tokens, request)]
        numbers += [(number, euro) for number in _comma_decimals(text, request)]
        for number, symbols in numbers:
            if number.sign:
                continue
            for symbol, code in symbols:
                for (start, end, prefix, suffix), sign, scale in self._sides(text, number, symbol, scales, request):
                    yield Span(start, end, Form.MONEY,
                               FrozenMap({"amount": FrozenMap({**number.amount(), "sign": sign}), "currency": code,
                                          "written_symbol": symbol, "scale": scale, "prefix": prefix,
                                          "suffix": suffix}), recognizer=self.name)

    def numbers(self, text: str, tokens: Sequence[Token], request: Request) -> Sequence[Number]:
        """The numbers that a currency symbol may stand next to."""
        return numbers_in(text, request)

    def _sides(self, text: str, number: Number, symbol: str, scales: Sequence[str],
               request: Request) -> Iterator[tuple[tuple[int, int, str, str], str, str]]:
        """The bounds, the sign and the scale of the amount with the symbol before the number, then of the amount
        with the symbol after it, for each side where the symbol stands."""
        gaps = number_gaps(request.data)
        for gap in gaps:
            start = number.start - len(gap) - len(symbol)
            if start >= 0 and text[start:number.start] == symbol + gap:
                sign = SIGNS.get(text[start - 1], "") if start else ""
                if sign and _free_before(text, start - 1, ()):
                    start -= 1
                else:
                    sign = ""
                scale, end = _scale(text, number.end, scales, gaps)
                if (bounds := _affixes(text, start, end, request.data, ())) is not None:
                    yield bounds, sign, scale
                    break
        scaled = _scale(text, number.end, scales, gaps) if self.scale_before_symbol else ("", number.end)
        for gap in gaps:
            for scale, after in dict.fromkeys((scaled, ("", number.end))):
                end = after + len(gap) + len(symbol)
                if text.startswith(gap + symbol, after) \
                        and (bounds := _affixes(text, number.start, end, request.data, ())) is not None:
                    yield bounds, "", scale
                    return


def _comma_decimals(text: str, request: Request) -> tuple[Number, ...]:
    """In a variety whose decimal mark is the point, the numbers with a decimal comma and one or two digits after
    it, as in `23,88`. The marks of the variety do not parse such a number, because a group has three digits (CLDR
    49 decimal format `#,##0.###` of en, es and de), and only a script that declares the decimal comma gives one. CLDR
    49 writes a euro amount
    with this comma in de, es, fr and it (currency format `#,##0.00 ¤`, decimal mark `,`)."""
    if request.params.decimal_mark != ".":
        return ()
    comma = tuple(marks for marks in number_marks(request.data, ",") if marks[1] == ",")
    if not comma:
        return ()
    return tuple(number for number in find_numbers(text, comma, declared_marks(request.data))
                 if number.fraction is not None and len(number.fraction) <= 2)


def _scale(text: str, end: int, scales: Sequence[str], gaps: Sequence[str] = GAPS) -> tuple[str, int]:
    """The scale word written after text[:end], attached or after one gap, and the end of the span."""
    for gap in gaps:
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
            for gap in number_gaps(data):
                candidates = units_at(text, end + len(gap), request)
                if not gap:
                    candidates = (*candidates, *(u for u in joined_table(request) if text.startswith(u, end)))
                unit = next((u for u in candidates if text.startswith(gap, end)
                             and _suffix(text, end + len(gap) + len(u), data) is not None
                             and not _per_unit(text, end + len(gap) + len(u))
                             and not _elided(text, end + len(gap) + len(u), data)), None)
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


def _elided(text: str, end: int, data) -> bool:
    """Whether a mark of `elision_marks` and a letter continue a unit, as in `l'eau` after `3 l` in French: the
    unit symbol is the first letter of an elided word."""
    return end + 1 < len(text) and text[end] in data.get("elision_marks", ()) and is_letter(text[end + 1])


def _linked(text: str, end: int, marks: Sequence[str], by_start: dict[int, Number]) -> Number | None:
    """The unsigned number that one of the marks joins to text[:end], with no space or one space on each side."""
    for mark in marks:
        for gap in ("", " "):
            following = by_start.get(end + 2 * len(gap) + len(mark))
            if following is not None and not following.sign and text.startswith(gap + mark + gap, end):
                return following
    return None


def _spoken_words(text: str, tokens: Sequence[Token], request: Request) -> tuple[Word, ...]:
    """The context words of the text, where the characters that `SYMBOL` reads and the emoji sequences that `EMOJI`
    reads stand for their names. A sequence of such pieces that only spaces part is one word, whose text is the
    names, so it fills one slot of a window however many words the names hold."""
    marks = named_pieces(text, request)
    if not marks:
        return context_words(tokens)
    runs: list[list[tuple[int, int, str]]] = []
    for mark in marks:
        if runs and not text[runs[-1][-1][1]:mark[0]].strip():
            runs[-1].append(mark)
        else:
            runs.append([mark])
    found = [Word(run[0][0], run[-1][1], " ".join(name for _, _, name in run), False) for run in runs]
    starts = [start for start, _, _ in marks]
    for token in tokens:
        first, piece = len(found), token.start
        for start, end, _ in (*marks[bisect_left(starts, token.start):bisect_left(starts, token.end)],
                              (token.end, token.end + 1, "")):
            word = context_word(text[piece:start])
            if word is not None:
                offset = text.index(word, piece)
                found.append(Word(offset, offset + len(word), word, False))
            piece = end
        if len(found) > first:
            found[-1] = replace(found[-1], clause_end=token.clause_end)
    return tuple(sorted(found, key=lambda word: word.start))


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

    In the window, the characters that `SYMBOL` reads count by their names, and a sequence of them that only spaces
    part fills one slot. A slot names the run when one of its words is a phone word, so `☎000` reads "telephone zero
    zero zero", as "telephone 000" does, and a name between a phone word and the run does not push the phone word
    out: `Call me ⇒ 911` and `Call 911 or → 112.` read digit by digit. A run stays as written only when the last
    word before it is a phone word, as on a second pass. So in pt-BR, where `☎` reads "telefone no gancho",
    `☎3 91P` reads the number, and `Ligue → 1.234,56` reads the number. A list link does not count those
    characters, so `Call ⇒ 999 or → 112.` reads both runs digit by digit. For the same reason, a lexicon key as
    that last word counts by its spoken words: with a key `call` for "kall", `call+351` reads the number.

    Three tables of regexes hold the written shapes of a language. A run that a shape of `phone_unit_shapes`
    matches whole reads digit by digit as one unit with no other evidence. A run that a shape of
    `phone_kept_shapes` matches whole stays as written when it has no phone reading. A run that a shape of
    `no_phone_shapes` matches whole has no phone shape.

    `spaces` holds the spaces that may part two groups of a run, and `plans` the numbering plans that the recognizer
    reads, by region. A language whose `phone_regions` option offers a region that `PHONE_PLANS` lacks passes the
    plans it reads.

    By default the window holds the one word right before the run. Four fields widen it. `reach` is the number of
    words back that a phone word may stand. With `content_words`, a word of `function_words` does not count toward
    the reach, and the window stays within eight words of the clause, as in `Ligue para o 112.` A phone word of the
    window that is not right before the run names a run with a phone shape when `names_shaped` is set, and a short
    code that ends its clause or that a function word follows when `names_short_codes` is set, as in `Call the
    police on 999 now.`, and not the count in `The phone rang 101 times.`

    A language file that names phone numbers by context of its own subclasses this recognizer and replaces the
    methods `trimmed`, `window` and `names_back` as it needs. `EnglishTelephone` replaces only `trimmed`."""
    name: str = "telephone"
    form: Form = Form.TELEPHONE
    reach: int = 1
    content_words: bool = False
    names_shaped: bool = False
    names_short_codes: bool = False
    spaces: str = " "
    plans: FrozenMap = PHONE_PLANS

    def trimmed(self, text: str, start: int, written: str, request: Request) -> str:
        """The run of digit groups that starts at `start`, less a last group that the language reads apart."""
        return written

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        """The indices of the words that may hold a phone word for the run."""
        index = bisect_right(words, start, key=lambda word: word.end)
        if not self.content_words:
            return range(index - len(clause_window(text, words, start, end, -1, limit=self.reach, breaks=breaks)),
                         index)
        function_words = frozenset(request.data.get("function_words", ()))
        before = clause_window(text, words, start, end, -1, limit=8, breaks=breaks)
        counted = [i for i in range(index - len(before), index) if words[i].text.lower() not in function_words]
        return range(counted[-self.reach] if len(counted) >= self.reach else index - len(before), index)

    def names_back(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
                   shaped: bool, short_code: bool, request: Request) -> bool:
        """Whether a phone word of the window that is not right before the run names it."""
        if self.names_shaped and shaped:
            return True
        if not (self.names_short_codes and short_code):
            return False
        function_words = frozenset(request.data.get("function_words", ()))
        following = clause_window(text, words, start, end, 1, limit=1, breaks=breaks)
        return all(word.lower() in function_words for word in following)

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        words = _spoken_words(text, tokens, request)
        lexicon = {span.end: span.fields["spoken"] for span in Lexicon().find(text, tokens, request)} \
            if Form.LEXICON in request.params.forms else {}
        covered = frozenset(index for start, end, _ in named_pieces(text, request) for index in range(start, end))
        breaks = clause_breaks(text)
        phone_words = frozenset(w.lower() for w in request.data.get("phone_words", ()))
        shapes = [re.compile(shape) for shape in request.data.get("phone_shapes", ())]
        unit_shapes = [re.compile(shape) for shape in request.data.get("phone_unit_shapes", ())]
        kept_shapes = [re.compile(shape) for shape in request.data.get("phone_kept_shapes", ())]
        no_shapes = [re.compile(shape) for shape in request.data.get("no_phone_shapes", ())]
        short_codes = frozenset(request.data.get("short_codes", ()))
        codes = sorted((plan["country_code"] for plan in self.plans.values()), key=len, reverse=True)
        plans = [self.plans[r] for r in sorted(request.params.phone_regions or ()) if r in self.plans]
        links = "|".join(map(re.escape, request.data.get("list_links", ())))
        listed = re.compile(f",? (?:{links}) |, " if links else ", ")
        operators = "".join(request.data.get("operators", ()))
        operand = re.compile(f"[{re.escape(operators)}][0-9]") if operators else None
        named_end = None
        folded = fold_digits(text)
        kept_end = 0
        for match in _phone_pattern(self.spaces).finditer(folded):
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
            groups = [group for group in re.split(f"[{re.escape(self.spaces)}.()-]", written.lstrip("+")) if group]
            digits = "".join(groups)
            shaped = not any(shape.fullmatch(written) for shape in no_shapes) and (
                written.startswith("+") or digits.startswith("0") or any(c in self.spaces + ".()-" for c in written))
            window = self.window(text, words, breaks, start, end, request)
            phone_ends = [words[i].end for i in window if phone_words.intersection(words[i].text.lower().split())]
            between = range(phone_ends[-1], start - len(prefix)) if phone_ends else range(0)
            direct = bool(phone_ends) and not any(is_word_char(text[index]) for index in between)
            spoken = lexicon.get(words[window[-1]].end, words[window[-1]].text) if window else ""
            keeps = direct and bool(phone_words.intersection(spoken.lower().split()[-1:]))
            country_code = ""
            if written.startswith("+"):
                if len(groups) > 1 and len(groups[0]) <= 3:
                    country_code, groups = groups[0], groups[1:]
                else:
                    country_code = next((c for c in codes if groups[0].startswith(c)), "")
                    groups[0] = groups[0][len(country_code):]
            short_code = "".join(groups) in short_codes
            gap = "" if named_end is None else re.sub(" {2,}", " ", "".join(
                char for index, char in enumerate(text[named_end:start], named_end)
                if index not in covered))
            named = (direct
                     or (bool(phone_ends) and self.names_back(text, words, breaks, start, end, shaped, short_code,
                                                               request))
                     or (named_end is not None and listed.fullmatch(gap) is not None))
            named_end = end + len(suffix) if named else None
            unknown_code = written.startswith("+") and not country_code
            if glued:
                if not (keeps and len(digits) >= 3 and (shaped or short_code or len(digits) >= 7)):
                    continue
                chained = _GLUED.match(folded, end).group()
                if chained and end + len(chained) < len(text) and is_word_char(text[end + len(chained)]):
                    chained = re.sub("[ /:.,–-]?[0-9]+$", "", chained)
                end = kept_end = named_end = end + len(chained)
            first, last = start - len(prefix), end + len(suffix)
            written_only = FrozenMap({"country_code": "", "groups": tuple(groups), "prefix": prefix, "suffix": suffix})
            if glued or not one_digit_set(text[start:end]) or (keeps and (len(digits) > 15 or unknown_code)):
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
        words = spell_digits(digits, request)
    else:
        words = request.language.spellers[Form.CARDINAL].cardinal(digits, Features(), request)
    words = signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def signed(words: str, sign: str, request: Request) -> str:
    """The words of a number after the word of its sign in `sign_words`."""
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def speak_rbnf_cardinal(span: Span, context: SpanContext) -> str:
    """The cardinal of a language with no file (section 6.1). A number with a minus reads through the `-x` rule of
    the RBNF cardinal rule set, which writes the sign word before or after the number, with or without a space."""
    if span.fields["sign"] == "-":
        request = context.request
        return request.language.spellers[Form.CARDINAL].negative_cardinal(span.fields["digits"], Features(), request)
    return speak_cardinal(span, context)


def amount_words(amount: FrozenMap, request: Request, features: Features = Features()) -> str:
    """A `DECIMAL` record through the spellers of the language, with its sign: the decimal speller when the record
    has fraction digits, else the cardinal speller with `features`."""
    spellers = request.language.spellers
    if amount["fraction"]:
        words = spellers[Form.DECIMAL].decimal(amount["integer"], amount["fraction"], features, request)
    else:
        words = spellers[Form.CARDINAL].cardinal(amount["integer"] or "0", features, request)
    return signed(words, amount["sign"], request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return amount_words(span.fields, context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields, request = span.fields, context.request
    words = request.language.spellers[Form.FRACTION].fraction(fields["numerator"], fields["denominator"], Features(),
                                                              request)
    return signed(words, fields["sign"], request)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    return context.request.language.spellers[Form.ORDINAL].ordinal(span.fields["digits"], Features(), context.request)


def speak_range(span: Span, context: SpanContext) -> str:
    """The two ends as cardinals, with the `range_word` between them."""
    request = context.request
    cardinal = request.language.spellers[Form.CARDINAL].cardinal
    low, high = (cardinal(span.fields[end], Features(), request) for end in ("low", "high"))
    return f"{low} {request.data['range_word']} {high}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """The amount, then the word of the `percent` table."""
    request = context.request
    return f"{amount_words(span.fields['amount'], request)} {request.data['percent']['word']}"


def speak_expression(span: Span, context: SpanContext) -> str:
    """Each operand as a cardinal with its sign, and the word of each operator from `operators`: `-2+3=1` reads
    "minus two plus three equals one", and `3 − −3` "three minus minus three"."""
    request = context.request
    cardinal = request.language.spellers[Form.CARDINAL].cardinal

    def operand(written: str) -> str:
        return signed(cardinal(written.lstrip(_OPERAND_SIGNS), Features(), request), SIGNS.get(written[0], ""),
                      request)

    operands = span.fields["operands"]
    words = [operand(operands[0])]
    for operator, written in zip(span.fields["operators"], operands[1:]):
        words += [request.data["operators"][operator], operand(written)]
    return " ".join(words)


def speak_telephone(span: Span, context: SpanContext) -> str:
    """Each group digit by digit, after the sign word of `+` and the country code when the number has one."""
    request = context.request
    groups = [spell_digits(group, request) for group in span.fields["groups"]]
    if span.fields["country_code"]:
        groups.insert(0, f"{request.data['sign_words']['+']} {spell_digits(span.fields['country_code'], request)}")
    return " ".join(groups)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """The reading of the key in the first of `titles`, `abbreviations` and `number_abbreviations` that holds it."""
    data = context.request.data
    key = span.fields["key"]
    for table in ("titles", "abbreviations", "number_abbreviations"):
        if data[table].get(key) is not None:
            return data[table][key]
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


def speak_idiom(span: Span, context: SpanContext) -> str:
    return context.request.data["idioms"][span.fields["key"]]


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


_OPERAND_SIGNS = "-−+"
"""The signs that an operand of an expression may carry."""


@dataclass(frozen=True)
class Expression:
    """`5+3`, `2 × 2 = 4`, `-2+3=1`: operators between integers, with no letter on either side. Each integer may
    carry one sign, `-`, `−` or `+`, right before its digits. `−` and `+` are both signs and operators: `−3−3` is
    "minus three minus three", and `3 − −3` is "three minus minus three".

    An operator right after the last integer stays with the expression, so `1+1 × 10%` keeps `1+1 ×` as
    written: the percentage claims `10`, and a second pass finds `1+1 × ten` with the same open operator.

    Two signs before one integer, as in `--3+3` and `3+--3`, keep the expression as written. So does a symbol of
    the `symbols` table next to the expression, as in `$−3+3`, because no form reads a number next to one."""
    name: str = "expression"
    form: Form = Form.EXPRESSION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        operators = re.escape("".join(request.data["operators"]))
        open_operator = re.compile(f" ?[{operators}]")
        symbols = request.data["symbols"]
        for written, start, end in grouped_matches(request.data["patterns"]["expression"], text, request):
            if (not (is_bounded(text, start, end) and one_digit_set(text[start:end]))
                    or open_operator.match(text, end)):
                continue
            written = written.replace(" ", "")
            first = re.match(f"[{_OPERAND_SIGNS}]?[0-9]+", written).group()
            pairs = re.findall(f"([{operators}])([{_OPERAND_SIGNS}]*[0-9]+)", written[len(first):])
            if not pairs:
                continue
            signs, others = zip(*pairs)
            unclear = (any(len(operand) - len(operand.lstrip(_OPERAND_SIGNS)) > 1 for operand in others)
                       or (start > 0 and (text[start - 1] in symbols
                                          or (text[start - 1] in _OPERAND_SIGNS and not first[0].isdigit())))
                       or (end < len(text) and text[end] in symbols))
            yield Span(start, end, Form.EXPRESSION, FrozenMap({"operands": (first, *others), "operators": signs}),
                       recognizer=self.name, keep=unclear)


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, a number abbreviation before a number, and the abbreviations of the
    table, as in `Dr. Smith`, `No. 5` and `etc.` A key of `sentence_final` that ends the sentence, before a capital
    letter or at the end of the text, keeps its full stop as the trail of the span. A title before a capital
    letter comes before a name, so it keeps no full stop.

    A language file that reads other tables replaces `tables`, and one that refuses a key in some places replaces
    `refuses`."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def tables(self, data) -> tuple[tuple[str, Iterable[str], Callable[[str], bool]], ...]:
        """Each table: its name, its keys, and the test that the character after a key passes. A key with no
        reading, as in a variety that removes a key of the language, is no key."""
        def keys(table) -> list[str]:
            return [key for key, value in table.items() if value is not None]

        return (("titles", keys(data["titles"]), str.isupper),
                ("number_abbreviations", keys(data["number_abbreviations"]), str.isdigit),
                ("abbreviations", keys(data["abbreviations"]), lambda _: True))

    def refuses(self, text: str, position: int, table: str, data) -> bool:
        """Whether the key of `table` at `position` stays as written."""
        return False

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        final = frozenset(data["sentence_final"])
        for table, keys, follows in self.tables(data):
            for key in sorted(keys, key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    if is_bounded(text, position, end) and follows(following) \
                            and not self.refuses(text, position, table, data):
                        sentence_end = table != "titles" and key in final \
                            and (following == "" or following.isupper())
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}),
                                   trail="." if sentence_end else "", recognizer=self.name)
                    position = text.find(key, end)


SPACE_GROUPS = re.compile("[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{3})+(?:,[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{1,3})*)?"
                          "|[0-9]+,[0-9]{3}(?:[ \u00a0\u202f][0-9]{1,3})+")
"""Digits in groups of three with a space, a no-break space or a narrow no-break space between them, in the
whole part or in the fraction after a decimal comma: `36 524`, `123 456 789,987 546`, `0,264 7` (Araua 203,
section 3.2.1.1, page 12)."""


@dataclass(frozen=True)
class SpaceGroups:
    """`36 524`, `30 000`: digits in groups of three with a space between them. The span stays as written in every
    language that lists this recognizer, whatever its group mark, so that no other recognizer reads each group as
    a number of its own."""
    name: str = "space_groups"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in SPACE_GROUPS.finditer(fold_digits(text)):
            start, end = match.span()
            script = digit_script(text[start:end])
            if script is None or (start and is_word_char(text[start - 1])) or not _cluster_edge(text, start, end):
                continue
            digits = re.sub("[^0-9]", "", match.group())
            yield Span(start, end, Form.CARDINAL,
                       FrozenMap({"digits": digits, "sign": "", "lead": "", "prefix": "", "suffix": "",
                                  "script": script}), recognizer=self.name, keep=True)


LEXICON = Lexicon()
CARDINAL = Cardinal()
RBNF_CARDINAL = RbnfCardinal()
SHARED = {r.name: r for r in (LEXICON, CARDINAL, Decimal(), Fraction(), Idiom(), Range(), DateNumeric(), TimeClock(),
                              Percent(), Money(), Measure(), Telephone(), Expression(), Abbreviation(), SpaceGroups(),
                              COLOR, ELECTRONIC, LETTERS, SYMBOL, EMOJI)}
"""The shared recognizers by name."""
