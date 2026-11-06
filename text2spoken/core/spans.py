"""Spans, features, the field schemas, and the classify and render loops (design sections 4.4, 5.1, 5.5)."""
from __future__ import annotations

import logging
import warnings
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

from text2spoken.core.tokens import Token, context_word, is_digit, is_word_char
from text2spoken.errors import HintWarning, InvalidHintError, Text2SpokenError, UndefinedGrammaticalGender, UnreadFormError
from text2spoken.params import Animacy, FrozenMap, Form, GrammaticalGender

if TYPE_CHECKING:
    from text2spoken.core.language import LanguageSpec, Request

LOG = logging.getLogger("text2spoken")

FIELDS: Mapping[Form, frozenset[str]] = {
    Form.LEXICON: frozenset({"spoken"}),
    Form.CARDINAL: frozenset({"digits", "sign", "prefix", "suffix", "script"}),
    Form.ORDINAL: frozenset({"digits", "marker", "prefix", "suffix", "script"}),
    Form.DECIMAL: frozenset({"integer", "fraction", "sign", "prefix", "suffix", "script"}),
    Form.FRACTION: frozenset({"numerator", "denominator", "sign", "prefix", "suffix"}),
    Form.RANGE: frozenset({"low", "high", "prefix", "suffix"}),
    Form.EXPRESSION: frozenset({"operands", "operators"}),
    Form.DATE: frozenset({"year", "month", "day", "written_order", "month_written", "suffix"}),
    Form.TIME: frozenset({"hour", "minute", "second", "period", "suffix"}),
    Form.YEAR: frozenset({"digits", "suffix"}),
    Form.MONEY: frozenset({"amount", "currency", "written_symbol"}),
    Form.MEASURE: frozenset({"amount", "unit"}),
    Form.PERCENT: frozenset({"amount", "sign_position"}),
    Form.TELEPHONE: frozenset({"country_code", "groups"}),
    Form.IDENTIFIER: frozenset({"head", "digits"}),
    Form.LETTERS: frozenset({"letters", "digits"}),
    Form.ABBREVIATION: frozenset({"key"}),
    Form.IDIOM: frozenset({"key"}),
    Form.ROMAN: frozenset({"value", "role", "suffix"}),
    Form.COLOR: frozenset({"rgb", "alpha"}),
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


def _boundary_allowed(text: str, position: int, form: Form) -> bool:
    before, after = text[position - 1], text[position]
    if is_digit(before) != is_digit(after):
        return True
    return form is Form.LEXICON and (before in "'’" or after in "'’")


def splits_token(span: Span, tokens: Sequence[Token], text: str) -> bool:
    """Whether a span edge falls inside a token at a point the rule of section 2.1 refuses."""
    for token in tokens:
        for edge in (span.start, span.end):
            if token.start < edge < token.end and not _boundary_allowed(text, edge, span.form):
                return True
    return False


def classify(text: str, tokens: Sequence[Token], blocks: Sequence[tuple[int, int]], request: Request) -> tuple[Span, ...]:
    claimed: list[Span] = []
    for recognizer in request.language.recognizers:
        if recognizer.form not in request.params.forms:
            continue
        for span in recognizer.find(text, tokens, request):
            if (_inside(span, blocks) or splits_token(span, tokens, text)
                    or any(span.start < c.end and c.start < span.end for c in claimed)):
                continue
            claimed.append(span)
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


def _clause_break(text: str, start: int, end: int) -> bool:
    """Whether the text between two words ends a clause: `;`, `!` or `?`, or `.` before a capital letter."""
    gap = text[start:end]
    if any(c in ";!?" for c in gap):
        return True
    return any(char == "." and text[start + i + 1:].lstrip()[:1].isupper() for i, char in enumerate(gap))


def clause_window(text: str, words: Sequence[Word], start: int, end: int, direction: int,
                  limit: int = 3) -> tuple[str, ...]:
    """Up to `limit` context words before (direction -1) or after (+1) text[start:end], within its clause."""
    if direction < 0:
        edge, candidates = start, [w for w in reversed(words) if w.end <= start]
    else:
        edge, candidates = end, [w for w in words if w.start >= end]
    found: list[str] = []
    for word in candidates:
        if len(found) == limit:
            break
        if direction < 0:
            if word.clause_end or _clause_break(text, word.end, edge):
                break
            edge = word.start
        else:
            if _clause_break(text, edge, word.start):
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
    out: list[str] = []
    passthrough: list[tuple[int, int]] = []
    position = 0
    for span in analysis.spans:
        out.append(analysis.text[position:span.start])
        passthrough.append((position, span.start))
        context = SpanContext(request, clause_window(analysis.text, words, span.start, span.end, -1),
                              clause_window(analysis.text, words, span.start, span.end, 1), hints.get(span.start))
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


def is_bounded(text: str, start: int, end: int) -> bool:
    """Whether the characters on either side of text[start:end] are not word characters."""
    return (start == 0 or not is_word_char(text[start - 1])) and (end == len(text) or not is_word_char(text[end]))
