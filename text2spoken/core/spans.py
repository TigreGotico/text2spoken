"""Spans, features, the field schemas, and the classify and render loops (design sections 4.4, 5.1, 5.5)."""
from __future__ import annotations

import heapq
import logging
import warnings
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

from text2spoken.core.tokens import Token, context_word, is_digit, is_punctuation
from text2spoken.errors import HintWarning, InvalidHintError, Text2SpokenError, UndefinedGrammaticalGender, UnreadFormError
from text2spoken.params import Animacy, FrozenMap, Form, GrammaticalGender

if TYPE_CHECKING:
    from text2spoken.core.language import LanguageSpec, Request

LOG = logging.getLogger("text2spoken")

FIELDS: Mapping[Form, frozenset[str]] = {
    Form.LEXICON: frozenset({"spoken"}),
    Form.CARDINAL: frozenset({"digits", "sign", "lead", "prefix", "suffix", "script"}),
    Form.ORDINAL: frozenset({"digits", "marker", "prefix", "suffix", "script"}),
    Form.DECIMAL: frozenset({"integer", "fraction", "sign", "prefix", "suffix", "script"}),
    Form.FRACTION: frozenset({"numerator", "denominator", "sign", "prefix", "suffix"}),
    Form.RANGE: frozenset({"low", "high", "prefix", "suffix"}),
    Form.EXPRESSION: frozenset({"operands", "operators"}),
    Form.DATE: frozenset({"year", "month", "day", "written_order", "month_written", "prefix", "suffix"}),
    Form.TIME: frozenset({"hour", "minute", "second", "period", "suffix"}),
    Form.YEAR: frozenset({"digits", "suffix"}),
    Form.MONEY: frozenset({"amount", "currency", "written_symbol", "scale", "prefix", "suffix"}),
    Form.MEASURE: frozenset({"amount", "relation", "unit", "prefix", "suffix"}),
    Form.PERCENT: frozenset({"amount", "sign_position", "prefix", "suffix"}),
    Form.TELEPHONE: frozenset({"country_code", "groups", "prefix", "suffix"}),
    Form.IDENTIFIER: frozenset({"head", "digits"}),
    Form.LETTERS: frozenset({"letters", "digits"}),
    Form.ABBREVIATION: frozenset({"key"}),
    Form.IDIOM: frozenset({"key", "prefix", "suffix"}),
    Form.ROMAN: frozenset({"value", "role", "suffix"}),
    Form.COLOR: frozenset({"rgb", "alpha", "hex"}),
}
"""The fields of each form (section 4.4). A recognizer emits exactly these."""


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    form: Form
    fields: FrozenMap
    lead: str = ""
    trail: str = ""
    recognizer: str = ""
    keep: bool = False
    """A span that keeps its text as written: it claims its characters, so that no other span reads them."""


@dataclass(frozen=True)
class Features:
    gender: GrammaticalGender | None = None
    animacy: Animacy | None = None
    noun_class: str | None = None
    number: Literal["singular", "plural", "dual"] | None = None
    case: str | None = None
    numeral_system: str | None = None
    definite: bool | None = None


@dataclass(frozen=True)
class Analysis:
    text: str
    blocks: tuple[tuple[int, int], ...]
    tokens: tuple[Token, ...]
    spans: tuple[Span, ...]
    request: Request


@dataclass(frozen=True)
class SpanContext:
    request: Request
    before: tuple[str, ...]
    after: tuple[str, ...]
    hint: Features | None


class Recognizer(Protocol):
    name: str
    form: Form

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterable[Span]: ...


Verbalizer = Callable[[Span, SpanContext], str]


def check_features(features: Features, language: LanguageSpec, lang: str) -> None:
    """Raise UndefinedGrammaticalGender for a value that the language does not define.

    A dimension that the language does not have at all, such as gender in English, has no effect.
    """
    for value, defined in ((features.gender, language.genders), (features.animacy, language.animacies),
                           (features.noun_class, language.noun_classes),
                           (features.numeral_system, language.numeral_systems)):
        if value is not None and defined and value not in defined:
            raise UndefinedGrammaticalGender(lang, str(value), frozenset(str(v) for v in defined))


def _inside(span: Span, blocks: Sequence[tuple[int, int]]) -> bool:
    return any(span.start < end and start < span.end for start, end in blocks)


def _boundary_allowed(text: str, position: int) -> bool:
    """A digit next to a non-digit, or a punctuation character on either side, such as the apostrophe of
    `l'ACME` or the dash of `9am-5pm`."""
    before, after = text[position - 1], text[position]
    return is_digit(before) != is_digit(after) or is_punctuation(before) or is_punctuation(after)


def splits_token(span: Span, tokens: Sequence[Token], text: str) -> bool:
    """Whether a span edge falls inside a token at a point the rule of section 2.1 refuses."""
    for edge in (span.start, span.end):
        index = bisect_right(tokens, edge, key=lambda token: token.start) - 1
        if index < 0:
            continue
        token = tokens[index]
        lead_start = edge == span.start and bool(span.fields.get("lead"))
        if token.start < edge < token.end and not (lead_start or _boundary_allowed(text, edge)):
            return True
    return False


def _joiner(char: str) -> bool:
    return not (char.isspace() or is_digit(char))


def _joined(text: str, span: Span, read: bytearray, holder: list[Span | None]) -> bool:
    """Whether one character that is not a digit or a space joins the span, on either side, to a digit that no
    span reads, or to a character of a waiting span of another form. A joiner that a waiting span of the same
    form holds is no joiner: the two spans are one range, as in `$5-$10`."""
    def side(joiner: int, beyond: int) -> bool:
        if not (0 <= beyond < len(text) and _joiner(text[joiner]) and not read[joiner] and not read[beyond]):
            return False
        partner = holder[joiner]
        if partner is not None and partner.form is span.form:
            return False
        waiting = holder[beyond]
        return is_digit(text[beyond]) or (waiting is not None and waiting.form is not span.form)
    return side(span.start - 1, span.start - 2) or side(span.end, span.end + 1)


def classify(text: str, tokens: Sequence[Token], blocks: Sequence[tuple[int, int]], request: Request) -> tuple[Span, ...]:
    """The spans that the recognizers claim, in claim order, by the rules of sections 2.1 and 4.2.

    A span that one character joins to a digit run waits while no span reads that run, and no other span claims a
    character of a waiting span. A claimed span wakes the waiting spans next to it, which are checked again in
    claim order, as they would be on a second pass over the output. A `keep` span claims its characters and
    stays out of the result, so its text stays as written.
    """
    candidates = [span for recognizer in request.language.recognizers if recognizer.form in request.params.forms
                  for span in recognizer.find(text, tokens, request)
                  if not (_inside(span, blocks) or splits_token(span, tokens, text))]
    read = bytearray(len(text))
    holder: list[Span | None] = [None] * len(text)
    neighbours: dict[int, list[int]] = {}
    claimed: list[Span] = []
    queue = list(range(len(candidates)))
    while queue:
        index = heapq.heappop(queue)
        span = candidates[index]
        if any(read[span.start:span.end]) or any(holder[p] not in (None, span) for p in range(span.start, span.end)):
            continue
        if _joined(text, span, read, holder):
            for position in range(span.start, span.end):
                holder[position] = span
            for position in (span.start - 2, span.start - 1, span.end, span.end + 1):
                neighbours.setdefault(position, []).append(index)
            continue
        read[span.start:span.end] = b"\x01" * (span.end - span.start)
        if not span.keep:
            claimed.append(span)
        for position in range(span.start, span.end):
            for waiting in neighbours.pop(position, ()):
                heapq.heappush(queue, waiting)
    return tuple(sorted(claimed, key=lambda s: s.start))


@dataclass(frozen=True)
class Word:
    """A context word: its offsets in the text, its text, and whether a clause ends after its token."""
    start: int
    end: int
    text: str
    clause_end: bool


def context_words(tokens: Sequence[Token]) -> tuple[Word, ...]:
    found = []
    for token in tokens:
        word = context_word(token.text)
        if word is not None:
            offset = token.start + token.text.index(word)
            found.append(Word(offset, offset + len(word), word, token.clause_end))
    return tuple(found)


def clause_breaks(text: str) -> tuple[int, ...]:
    """The positions in text that end a clause: `;`, `!` or `?`, or `.` before a capital letter."""
    breaks: list[int] = []
    visible = ""
    for index in range(len(text) - 1, -1, -1):
        char = text[index]
        if char in ";!?" or (char == "." and visible.isupper()):
            breaks.append(index)
        if not char.isspace():
            visible = char
    return tuple(reversed(breaks))


def _clause_break(breaks: Sequence[int], start: int, end: int) -> bool:
    """Whether a clause ends in text[start:end]."""
    index = bisect_left(breaks, start)
    return index < len(breaks) and breaks[index] < end


def clause_window(text: str, words: Sequence[Word], start: int, end: int, direction: int,
                  limit: int = 3, breaks: Sequence[int] | None = None) -> tuple[str, ...]:
    """Up to `limit` context words before (direction -1) or after (+1) text[start:end], within its clause.

    The words are in text order. A word that holds the end of text[start:end] and ends its clause stops the
    window after it. `breaks` are the clause_breaks of text, for a caller that looks up many windows.
    """
    if breaks is None:
        breaks = clause_breaks(text)
    if direction < 0:
        index = bisect_right(words, start, key=lambda word: word.end)
        edge, candidates = start, (words[i] for i in range(index - 1, -1, -1))
    else:
        index = bisect_left(words, end, key=lambda word: word.start)
        if index and words[index - 1].start < end <= words[index - 1].end and words[index - 1].clause_end:
            return ()
        edge, candidates = end, (words[i] for i in range(index, len(words)))
    found: list[str] = []
    for word in candidates:
        if len(found) == limit:
            break
        if direction < 0:
            if word.clause_end or _clause_break(breaks, word.end, edge):
                break
            edge = word.start
        else:
            if _clause_break(breaks, edge, word.start):
                break
            edge = word.end
        found.append(word.text)
        if direction > 0 and word.clause_end:
            break
    return tuple(reversed(found)) if direction < 0 else tuple(found)


def check_hints(hints: Mapping[int, Features], analysis: Analysis) -> dict[int, Features]:
    request = analysis.request
    starts = {span.start for span in analysis.spans}
    checked = {}
    for key, features in hints.items():
        if not isinstance(features, Features):
            raise TypeError(f"a hint must be Features, not {type(features).__name__}")
        check_features(features, request.language, request.tag)
        if key not in starts:
            message = f"no span starts at offset {key!r}"
            if request.params.strict:
                raise InvalidHintError(message)
            warnings.warn(message, HintWarning, stacklevel=3)
            continue
        checked[key] = features
    return checked


def _unread_runs(segment: str, symbols: frozenset[str], read_digits: bool) -> list[str]:
    runs = []
    for run in segment.split():
        if any((read_digits and is_digit(c)) or c in symbols for c in run):
            runs.append(run)
    return runs


def render(analysis: Analysis, hints: Mapping[int, Features] | None = None) -> str:
    request = analysis.request
    language = request.language
    hints = check_hints(hints or {}, analysis)
    words = context_words(analysis.tokens) if language.context_words else ()
    breaks = clause_breaks(analysis.text)
    out: list[str] = []
    passthrough: list[tuple[int, int]] = []
    position = 0
    for span in analysis.spans:
        out.append(analysis.text[position:span.start])
        passthrough.append((position, span.start))
        context = SpanContext(request, clause_window(analysis.text, words, span.start, span.end, -1, breaks=breaks),
                              clause_window(analysis.text, words, span.start, span.end, 1, breaks=breaks),
                              hints.get(span.start))
        written = analysis.text[span.start:span.end]
        try:
            spoken = language.verbalizers[span.form](span, context)
            spoken = language.attach(spoken, span.fields.get("prefix", ""), span.fields.get("suffix", ""))
            out.append(span.lead + spoken + span.trail)
        except Text2SpokenError:
            raise
        except Exception as error:
            if request.params.strict:
                raise UnreadFormError((written,), f"{span.form}: {error}") from error
            LOG.warning("unread %s span %r at %d: %s", span.form, written, span.start, error)
            out.append(written)
        position = span.end
    out.append(analysis.text[position:])
    passthrough.append((position, len(analysis.text)))
    _check_unread(analysis, passthrough)
    return "".join(out)


def _check_unread(analysis: Analysis, passthrough: list[tuple[int, int]]) -> None:
    request = analysis.request
    symbols = frozenset(symbol for symbol, form in request.data.get("symbols", {}).items()
                        if Form(form) in request.params.forms)
    read_digits = Form.CARDINAL in request.params.forms
    unread: list[str] = []
    for start, end in passthrough:
        cursor = start
        for block_start, block_end in analysis.blocks:
            if block_end <= cursor or block_start >= end:
                continue
            unread += _unread_runs(analysis.text[cursor:block_start], symbols, read_digits)
            cursor = block_end
        if cursor < end:
            unread += _unread_runs(analysis.text[cursor:end], symbols, read_digits)
    if not unread:
        return
    if request.params.strict:
        raise UnreadFormError(tuple(unread))
    for run in unread:
        LOG.warning("unread written form %r for %s", run, request.tag)

