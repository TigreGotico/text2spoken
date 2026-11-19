"""Spans, features, the field schemas, and the classify and render loops (design sections 4.4, 5.1, 5.5)."""
from __future__ import annotations

import heapq
import logging
import warnings
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import KW_ONLY, dataclass, replace
from typing import TYPE_CHECKING, Literal, Protocol

from text2spoken.core.emoji import emoji_view, sequences_in
from text2spoken.core.tokens import (EMOJI_MARKS, Token, context_word, is_digit, is_letter, is_mark, is_punctuation,
                                     next_visible)
from text2spoken.errors import (ArgumentTypeError, DeclinedReading, HintWarning, InvalidHintError, Text2SpokenError,
                                UndefinedGrammaticalGender, UnreadFormError, require_type)
from text2spoken.params import Animacy, FrozenMap, Form, GrammaticalGender

if TYPE_CHECKING:
    from text2spoken.core.language import LanguageSpec, Request

LOG = logging.getLogger("text2spoken")

FIELDS: Mapping[Form, frozenset[str]] = {
    Form.LEXICON: frozenset({"spoken"}),
    Form.CARDINAL: frozenset({"digits", "sign", "lead", "prefix", "suffix", "script"}),
    Form.ORDINAL: frozenset({"digits", "marker", "prefix", "suffix", "script"}),
    Form.DECIMAL: frozenset({"integer", "fraction", "sign", "prefix", "suffix", "script"}),
    Form.FRACTION: frozenset({"whole", "numerator", "denominator", "sign", "prefix", "suffix"}),
    Form.RANGE: frozenset({"low", "high", "prefix", "suffix"}),
    Form.EXPRESSION: frozenset({"operands", "operators"}),
    Form.DATE: frozenset({"year", "month", "day", "written_order", "month_written", "era", "prefix", "suffix"}),
    Form.TIME: frozenset({"hour", "minute", "second", "period", "prefix", "suffix"}),
    Form.YEAR: frozenset({"digits", "suffix"}),
    Form.MONEY: frozenset({"amount", "currency", "written_symbol", "scale", "prefix", "suffix"}),
    Form.MEASURE: frozenset({"amount", "relation", "unit", "prefix", "suffix"}),
    Form.PERCENT: frozenset({"amount", "sign_position", "prefix", "suffix"}),
    Form.TELEPHONE: frozenset({"country_code", "groups", "prefix", "suffix"}),
    Form.IDENTIFIER: frozenset({"head", "digits"}),
    Form.LETTERS: frozenset({"letters", "reading", "clause"}),
    Form.ABBREVIATION: frozenset({"key"}),
    Form.IDIOM: frozenset({"key", "prefix", "suffix"}),
    Form.ROMAN: frozenset({"value", "role", "suffix"}),
    Form.COLOR: frozenset({"rgb", "alpha", "hex"}),
    Form.ELECTRONIC: frozenset({"kind", "scheme", "address"}),
    Form.SYMBOL: frozenset({"symbol"}),
    Form.EMOJI: frozenset({"sequence", "name"}),
}
"""The fields of each form (section 4.4). A recognizer emits exactly these."""


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    form: Form
    fields: FrozenMap
    _: KW_ONLY
    lead: str = ""
    trail: str = ""
    recognizer: str = ""
    keep: bool = False
    """A span that keeps its text as written: it claims its characters, so that no other span reads them."""


@dataclass(frozen=True, kw_only=True)
class Features:
    gender: GrammaticalGender | None = None
    animacy: Animacy | None = None
    noun_class: str | None = None
    number: Literal["singular", "plural", "dual"] | None = None
    case: str | None = None
    numeral_system: str | None = None
    definite: bool | None = None


@dataclass(frozen=True, kw_only=True)
class Analysis:
    text: str
    blocks: tuple[tuple[int, int], ...]
    """The protected blocks as (start, end) offsets, sorted, with no overlap. `render` relies on this order, so an
    Analysis built by hand keeps it."""
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
    """Whether the span overlaps a block. The blocks are in text order and do not overlap, so only the first block
    that ends after the span start can overlap it."""
    index = bisect_right(blocks, span.start, key=lambda block: block[1])
    return index < len(blocks) and blocks[index][0] < span.end


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


def _sides(span: Span, before: Mapping[int, int], after: Mapping[int, int]) -> tuple[tuple[int, int], ...]:
    """The joiner and the character beyond it, on the left and on the right of the span. `before` maps the end of each
    emoji sequence to its start, and `after` maps its start to its end. The sequence is one joiner, as one `SYMBOL`
    character is, so the character beyond it is outside the sequence."""
    left = before.get(span.start, span.start - 1)
    return (left, left - 1), (span.end, after.get(span.end, span.end + 1))


def _joined(text: str, span: Span, read: bytearray, holder: list[Span | None],
            sides: Sequence[tuple[int, int]]) -> bool:
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
    return any(side(joiner, beyond) for joiner, beyond in sides)


def _in_clause(span: Span, other: bytearray) -> bool:
    """Whether every other part of the clause of a `LETTERS` span stays as written in capitals: it is a run of the
    kind `stays`, and no span of another form reads it."""
    return all(kind == "stays" and not any(other[start:end])
               for start, end, kind in span.fields["clause"] if (start, end) != (span.start, span.end))


SAY_AS_SPANS = "say_as_spans"
"""The `Request.memo` key of the offsets of the spans that the recognizers of the say-as claim."""


def classify(text: str, tokens: Sequence[Token], blocks: Sequence[tuple[int, int]], request: Request) -> tuple[Span, ...]:
    """The spans that the recognizers claim, in claim order, by the rules of sections 2.1 and 4.2.

    A span that one character joins to a digit run waits while no span reads that run, and no other span claims a
    character of a waiting span. A claimed span wakes the waiting spans next to it, which are checked again in
    claim order, as they would be on a second pass over the output. A `keep` span claims its characters and
    stays out of the result, so its text stays as written. An `ELECTRONIC` span claims a token whole (section 4.5),
    so it does not wait on a joined digit. A `LEXICON` span claims before every recognizer (section 4.2), so it
    does not wait on a side where the key ends in a letter, or in a letter and its combining marks. On any other
    side it waits like any span, because a number recognizer refuses digits that one character joins to a digit,
    a symbol or an emoji. So with a key `cats`, `2,cats` reads "two,kats", and with a key `GPT-4`, `©` or `#️⃣`,
    `GPT-4/5`, `©,2` and `#️⃣,2` stay as written. A waiting `SYMBOL` or `EMOJI` span holds no character, so no span
    waits on it, and two spans cannot wait on each other through a symbol, as in `•∈$2§1`. A number abbreviation
    before its number, as `n.º` in `5-n.º 5`, does not wait: it is a key only before a digit, so a second pass, which
    reads the number after it, finds no key there and reads the `5` before it. A `TELEPHONE` span with a `joiner`
    waits on that mark in place of the character before it, and holds no character while it waits, so the digits read
    as they do with no phone span (`Telephone`).

    A word of a clause in capitals (`LETTERS`, section 4.6) stays as written while every other part of the clause
    stays as written in capitals. When another form claims a part, a part holds digits, or a part reads letter by
    letter, as `ROMAN` claims `VI` in `CAPÍTULO VI DE`, the word reads in lower case, so a second pass, which sees
    words in lower case and so no clause there, keeps it a word.

    With a say-as (section 17), the recognizers of the language for the forms of the say-as claim first, whatever
    `params.forms` holds, then the recognizer that takes the markup as evidence, then every recognizer of
    `params.forms` with the params of the call with no say-as, as the plain reading reads. A span
    of the say-as that its format refuses (`ResolvedSayAs.fits`) is no candidate, and nor is a span of the say-as that
    cuts a span of the analysis with no say-as, claimed, kept as written or waiting: a URL, an e-mail address or a
    phone number reads whole, as it reads with no say-as. Nor is a say-as span over the word next to a span that the
    plain reading keeps as written, because that word is the evidence that keeps it. A say-as span that waits holds its
    characters only against the other say-as spans: before the other recognizers claim, its characters are free, so
    the other text reads as it reads with no say-as. So with `digits`, `Flight 12 at 10:30` reads the time.

    An emoji sequence is one character to every other form, with `EMOJI` on or off, so a text reads as it reads with
    `😀` in place of the sequence (design section 4.7). The recognizers read the view of `emoji_view`, in which the
    digit of `1️⃣` is no digit. `EMOJI` and `ELECTRONIC` read the name of a sequence from the text as written
    (`written_text`). A sequence joins as one character when it holds U+FE0E, U+FE0F or U+20E3, and with `EMOJI` on,
    any sequence does.
    """
    return _claim(text, tokens, blocks, request)[0]


def _claim(text: str, tokens: Sequence[Token], blocks: Sequence[tuple[int, int]],
           request: Request) -> tuple[tuple[Span, ...], tuple[Span, ...], tuple[Span, ...]]:
    """The claimed spans, every span that holds characters (claimed, kept as written, or waiting), and the spans
    that hold characters as written."""
    emoji = Form.EMOJI in request.params.forms
    sequences = [(start, end) for start, end in sequences_in(text, request.memo)
                 if emoji or any(char in EMOJI_MARKS for char in text[start:end])]
    view = emoji_view(text, request.memo)
    request.memo[("written", view)] = text
    say_as = request.say_as
    recognizers = [recognizer for recognizer in request.language.recognizers if recognizer.form in request.params.forms]

    def found(group: Sequence[Recognizer], asked: Request) -> list[Span]:
        return [span for recognizer in group for span in recognizer.find(view, tokens, asked)
                if not (_inside(span, blocks)
                        or (span.form is not Form.ELECTRONIC and splits_token(span, tokens, text)))]

    first, others = [], request
    if say_as is not None:
        others = replace(request, params=say_as.plain, memo={("written", view): text}, say_as=None)
        first = [span for span in found(say_as.recognizers(request.language), request) if say_as.fits(span)]
    if first:
        _, units, held = _claim(text, tokens, blocks, others)
        unit_at: list[Span | None] = [None] * len(text)
        for unit in units:
            unit_at[unit.start:unit.end] = [unit] * (unit.end - unit.start)
        evidence = _evidence_words(text, tokens, held)
        first = [span for span in first if not (_cuts(span, unit_at) or any(evidence[span.start:span.end]))]
    say_as_count = len(first)
    candidates = [*first, *found(recognizers, others)]
    before = {end: start for start, end in sequences}
    after = dict(sequences)
    read = bytearray(len(text))
    other = bytearray(len(text))
    holder: list[Span | None] = [None] * len(text)
    neighbours: dict[int, list[int]] = {}
    claimed: list[Span] = []
    kept: list[Span] = []
    said: set[tuple[int, int]] = set()
    queue = list(range(len(candidates)))
    released = False
    while queue:
        index = heapq.heappop(queue)
        if index >= say_as_count and not released:
            holder = [None] * len(text)
            released = True
        span = candidates[index]
        if any(read[span.start:span.end]) or any(holder[p] not in (None, span) for p in range(span.start, span.end)):
            continue
        sides = _sides(span, before, after)
        headed = span.form is Form.TELEPHONE and "joiner" in span.fields
        if span.form is Form.LEXICON:
            last = span.end - 1
            while last > span.start and is_mark(view[last]):
                last -= 1
            sides = tuple(side for side, edge in zip(sides, (span.start, last)) if not is_letter(view[edge]))
        elif span.form is Form.ABBREVIATION and next_visible(view, span.end).isdigit() \
                and request.data.get("number_abbreviations", {}).get(span.fields["key"]) is not None:
            sides = ()
        elif headed:
            sides = ((span.fields["joiner"], span.fields["joiner"] - 1), sides[1])
        if span.form is not Form.ELECTRONIC and _joined(view, span, read, holder, sides):
            if span.form not in (Form.SYMBOL, Form.EMOJI) and not headed and not (released and index < say_as_count):
                for position in range(span.start, span.end):
                    holder[position] = span
            for position in (position for side in sides for position in side):
                neighbours.setdefault(position, []).append(index)
            continue
        if span.form is Form.LETTERS and span.fields["clause"] and not _in_clause(span, other):
            span = replace(span, fields=FrozenMap({**span.fields, "reading": "lower"}), keep=False)
        read[span.start:span.end] = b"\x01" * (span.end - span.start)
        if span.keep:
            kept.append(span)
        else:
            claimed.append(span)
            if index < say_as_count:
                said.add((span.start, span.end))
            if span.form is not Form.LETTERS:
                other[span.start:span.end] = b"\x01" * (span.end - span.start)
        for position in range(span.start, span.end):
            for waiting in neighbours.pop(position, ()):
                heapq.heappush(queue, waiting)
    if say_as is not None:
        request.memo[SAY_AS_SPANS] = frozenset(said)
    waiting = {id(span): span for span in holder if span is not None and not any(read[span.start:span.end])}
    held = (*kept, *waiting.values())
    return tuple(sorted(claimed, key=lambda s: s.start)), (*claimed, *held), held


def _evidence_words(text: str, tokens: Sequence[Token], held: Sequence[Span]) -> bytearray:
    """The words next to each span that stays as written: a recognizer reads them as the evidence that keeps the
    span as written, as `Call` keeps `112` in `Call 112+1.` and `kg` keeps `3/4` in `3/4 kg`."""
    marked = bytearray(len(text))
    words = [token for token in tokens if context_word(token.text) is not None]
    starts = [token.start for token in words]
    for span in held:
        before, after = bisect_left(starts, span.start) - 1, bisect_left(starts, span.end)
        for word in (words[before] if before >= 0 else None, words[after] if after < len(words) else None):
            if word is not None and (word.end <= span.start or word.start >= span.end):
                marked[word.start:word.end] = b"\x01" * (word.end - word.start)
    return marked


def _cuts(span: Span, unit_at: Sequence[Span | None]) -> bool:
    """Whether the span cuts a span of the plain analysis, which holds its characters as one unit. The units do not
    overlap, so a unit that the span cuts holds the first or the last character of the span."""
    first, last = unit_at[span.start], unit_at[span.end - 1]
    return (first is not None and first.start < span.start) or (last is not None and last.end > span.end)


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


class Clauses:
    """The clauses of the context words, for a caller that reads the whole clause around many spans. `around`
    gives the words of `clause_window` with no limit, after one pass over the words.

    Two neighbouring words are in one clause when the first does not end its clause and no clause ends between
    them. The windows before and after a span step over the words by this same rule."""

    def __init__(self, words: Sequence[Word], breaks: Sequence[int]):
        self.words, self.breaks = words, breaks
        joined = [not a.clause_end and not _clause_break(breaks, a.end, b.start) for a, b in zip(words, words[1:])]
        self.first = list(range(len(words)))
        for index, join in enumerate(joined, 1):
            if join:
                self.first[index] = self.first[index - 1]
        self.stop = list(range(1, len(words) + 1))
        for index in range(len(joined) - 1, -1, -1):
            if joined[index]:
                self.stop[index] = self.stop[index + 1]

    def around(self, start: int, end: int) -> tuple[range, range]:
        """The indexes of the words that `clause_window` with no limit gives before and after text[start:end]."""
        words, breaks = self.words, self.breaks
        before = bisect_right(words, start, key=lambda word: word.end)
        after = bisect_left(words, end, key=lambda word: word.start)
        back = ahead = range(0)
        if before and not words[before - 1].clause_end and not _clause_break(breaks, words[before - 1].end, start):
            back = range(self.first[before - 1], before)
        holder = words[after - 1] if after else None
        if (after < len(words) and not _clause_break(breaks, end, words[after].start)
                and not (holder and holder.start < end <= holder.end and holder.clause_end)):
            ahead = range(after, self.stop[after])
        return back, ahead


def check_hints(hints: Mapping[int, Features], analysis: Analysis) -> dict[int, Features]:
    request = analysis.request
    starts = {span.start for span in analysis.spans}
    checked = {}
    for key, features in hints.items():
        if not isinstance(key, int):
            raise ArgumentTypeError(f"a hint key must be an int offset, not {type(key).__name__}")
        if not isinstance(features, Features):
            raise ArgumentTypeError(f"a hint must be Features, not {type(features).__name__}")
        check_features(features, request.language, request.tag)
        if key not in starts:
            message = f"no span starts at offset {key!r}"
            if request.params.strict:
                raise InvalidHintError(message)
            warnings.warn(message, HintWarning, stacklevel=3)
            continue
        checked[key] = features
    return checked


def _unread_runs(segment: str, seen: str, symbols: frozenset[str], read_digits: bool) -> list[str]:
    """The runs of the segment that hold a digit or a form symbol, as the view `seen` of the segment shows them, so
    the digit of `1️⃣` is no unread digit."""
    return [run for run, view in zip(segment.split(), seen.split())
            if any((read_digits and is_digit(c)) or c in symbols for c in view)]


DECLINED = (DeclinedReading, NotImplementedError)
"""The errors with which a speller declines a span (design sections 5.4 and 10): it cannot read the number, or it
does not offer the method of the form. Any other error of a verbalizer is a defect, and it raises."""


def render(analysis: Analysis, hints: Mapping[int, Features] | None = None) -> str:
    """The spoken text of an analysis. With `LETTERS` on, a run of capitals in the reading of another form reads
    as the `LETTERS` form reads it, so a second pass leaves the reading unchanged (design section 11). When the
    verbalizer declines a say-as span, the text reads as if no say-as were given, with one log warning, or
    `UnreadFormError` in strict mode (design section 17.4)."""
    from text2spoken.core.letters import respell
    from text2spoken.core.say_as import READINGS

    require_type(analysis, "analysis", Analysis)
    if hints is not None:
        require_type(hints, "hints", Mapping)
    request = analysis.request
    language = request.language
    letters = Form.LETTERS in request.params.forms and Form.LETTERS in language.verbalizers
    hints = check_hints(hints or {}, analysis)
    words = context_words(analysis.tokens) if language.context_words else ()
    breaks = clause_breaks(analysis.text)
    say_as = request.say_as
    plain = request if say_as is None else replace(request, params=say_as.plain, say_as=None)
    out: list[str] = []
    passthrough: list[tuple[int, int]] = []
    position = 0
    for span in analysis.spans:
        out.append(analysis.text[position:span.start])
        passthrough.append((position, span.start))
        said = say_as is not None and say_as.claims(span, request)
        context = SpanContext(request if said else plain,
                              clause_window(analysis.text, words, span.start, span.end, -1, breaks=breaks),
                              clause_window(analysis.text, words, span.start, span.end, 1, breaks=breaks),
                              hints.get(span.start))
        written = analysis.text[span.start:span.end]
        try:
            speak = READINGS.get(span.recognizer) or language.verbalizers[span.form]
            spoken = speak(span, context)
            if letters and span.form not in (Form.LETTERS, Form.LEXICON):
                spoken = respell(spoken, request)
            spoken = language.attach(spoken, span.fields.get("prefix", ""), span.fields.get("suffix", ""))
            out.append(span.lead + spoken + span.trail)
        except DECLINED as error:
            if said:
                reason = f"the say-as {say_as.value!r} does not read {written!r} for {request.tag}: {error}"
                if request.params.strict:
                    raise UnreadFormError((written,), reason) from error
                LOG.warning("%s; the text reads as if no say-as were given", reason)
                unsaid = _without_say_as(analysis)
                starts = {other.start for other in unsaid.spans}
                return render(unsaid, {start: hint for start, hint in hints.items() if start in starts})
            if request.params.strict:
                raise UnreadFormError((written,), f"{span.form}: {error}") from error
            LOG.warning("unread %s span %r at %d: %s", span.form, written, span.start, error)
            out.append(written)
        except Text2SpokenError:
            raise
        except Exception as error:
            error.add_note(f"text2spoken: the {language.code} verbalizer of {span.form} fails on {written[:80]!r} "
                           f"({len(written)} characters) at {span.start}")
            raise
        position = span.end
    out.append(analysis.text[position:])
    passthrough.append((position, len(analysis.text)))
    _check_unread(analysis, passthrough)
    return "".join(out)


def _without_say_as(analysis: Analysis) -> Analysis:
    """The analysis of the same text with no say-as (design section 17.4)."""
    request = replace(analysis.request, params=analysis.request.say_as.plain, memo={}, say_as=None)
    return replace(analysis, spans=classify(analysis.text, analysis.tokens, analysis.blocks, request), request=request)


def _check_unread(analysis: Analysis, passthrough: list[tuple[int, int]]) -> None:
    request = analysis.request
    symbols = frozenset(symbol for symbol, form in request.data.get("symbols", {}).items()
                        if Form(form) in request.params.forms)
    read_digits = Form.CARDINAL in request.params.forms
    unread: list[str] = []
    view = emoji_view(analysis.text, request.memo)
    blocks = analysis.blocks
    for start, end in passthrough:
        cursor = start
        index = bisect_right(blocks, start, key=lambda block: block[1])
        while index < len(blocks) and blocks[index][0] < end:
            block_start, block_end = blocks[index]
            unread += _unread_runs(analysis.text[cursor:block_start], view[cursor:block_start], symbols, read_digits)
            cursor = block_end
            index += 1
        if cursor < end:
            unread += _unread_runs(analysis.text[cursor:end], view[cursor:end], symbols, read_digits)
    if not unread:
        return
    if request.params.strict:
        raise UnreadFormError(tuple(unread))
    for run in unread:
        LOG.warning("unread written form %r for %s", run, request.tag)

