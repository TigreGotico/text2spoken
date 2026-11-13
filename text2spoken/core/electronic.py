"""The e-mail and web address recognizer and its verbalizer: the `ELECTRONIC` rows of design section 4.2 and the
reading of section 4.5.

A token between spaces that holds an address marker is spoken in full, even when it is not one valid address. The
recognizer claims the token whole, without the punctuation at its ends that belongs to the sentence and without its
`[[...]]` blocks and lexicon spans. The verbalizer reads the claim piece by piece from the tables of the language
file: a label as a word or letter by letter, each digit by its digit word, each symbol by its word, and a character
with no word as written. With the `SYMBOL` form, a character that the address tables do not name reads by the CLDR
name that `SYMBOL` gives it (design section 4.7), so a second pass finds no symbol for that form to read.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext, splits_token
from text2spoken.core.symbols import symbol_name
from text2spoken.core.tokens import Token, is_digit, is_letter, is_mark, protect_blocks
from text2spoken.params import FrozenMap, Form

_LABEL = "[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
_HOST = f"(?:{_LABEL}[.])+[A-Za-z]+"
_REST = "(?::[0-9]+)?(?:[/?#][A-Za-z0-9._~:/?#@!$&'()*+,;=%-]*)?"
_HOST_START = re.compile(_HOST)
_SCHEME = re.compile("([A-Za-z][A-Za-z0-9+.-]*)://")
_SCHEME_URL = re.compile(f"([A-Za-z][A-Za-z0-9+.-]*)://{_HOST}{_REST}")
_EMAIL = re.compile(f"[A-Za-z0-9._+-]+@{_HOST}")
_WWW = re.compile(f"[Ww][Ww][Ww][.]{_HOST}{_REST}")
_DOMAIN = re.compile(f"{_HOST}{_REST}")
_WWW_START = re.compile("[Ww][Ww][Ww][.]")
_TOKEN = re.compile("[^\t-\r\x1c-\x20\x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+")
"""A run of characters between spaces, with the space characters of `str.isspace`."""
_QUOTES = frozenset("'\"")
_CLOSING = frozenset(".,;:!?")
_OPENERS = {")": "(", "]": "[", "}": "{"}


def _marked(text: str, start: int, end: int, token: re.Match, tlds: frozenset[str]) -> bool:
    """Whether `text[start:end]`, a part of `token` outside its `[[...]]` blocks, holds an address marker: `@`
    between two characters that are not spaces, `www.`, `://`, or a full stop followed by a label of `tlds` that no
    letter or digit follows."""
    if (text.find("@", max(start, token.start() + 1), min(end, token.end() - 1)) != -1
            or text.find("://", start, end) != -1 or _WWW_START.search(text, start, end) is not None):
        return True
    dot = text.find(".", start, end)
    while dot != -1:
        for tld in tlds:
            after = dot + 1 + len(tld)
            if text.startswith(tld, dot + 1, end) and (after == len(text) or not (is_letter(text[after])
                                                                                  or is_digit(text[after]))):
                return True
        dot = text.find(".", dot + 1, end)
    return False


def _claim(text: str, start: int, end: int) -> tuple[int, int]:
    """The token without an opening bracket or quote at its start and the run of closing full stops, commas,
    semicolons, colons, `!`, `?`, brackets and quotes at its end, which belong to the sentence. A bracket that the
    address opens stays."""
    if unicodedata.category(text[start]) in ("Ps", "Pi", "Pf") or text[start] in _QUOTES:
        start += 1
    unclosed = {closer: text.count(opener, start, end) - text.count(closer, start, end)
                for closer, opener in _OPENERS.items()}
    while end > start:
        last = text[end - 1]
        category = unicodedata.category(last)
        if last in _OPENERS:
            if unclosed[last] >= 0:
                break
            unclosed[last] += 1
        elif not (last in _CLOSING or last in _QUOTES or category in ("Pi", "Pf", "Pe")):
            break
        end -= 1
    return start, end


def _merged(bounds: list[tuple[int, int]]) -> list[list[int]]:
    """The ranges in text order, with the ranges that overlap or touch joined into one."""
    merged: list[list[int]] = []
    for start, end in sorted(bounds):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def _parts(ranges: list[list[int]], index: int, start: int, stop: int) -> Iterator[tuple[int, int]]:
    """The parts of the range from `start` to `stop` outside the merged `ranges`, where `ranges[index]` is the first
    range that ends after `start`."""
    cursor = start
    while index < len(ranges) and ranges[index][0] < stop:
        if cursor < ranges[index][0]:
            yield cursor, ranges[index][0]
        cursor = max(cursor, ranges[index][1])
        index += 1
    if cursor < stop:
        yield cursor, stop


def _fields(written: str, schemes: FrozenMap, tlds: frozenset[str]) -> FrozenMap:
    """The kind of a claim: one e-mail address, URL or bare domain of design section 4.2, or `run` for any other
    claim. A scheme of the `electronic_schemes` table at the start goes to the `scheme` field."""
    start = _SCHEME.match(written)
    scheme = start.group(1).lower() if start and start.group(1).lower() in schemes else ""
    host = _HOST_START.match(written)
    if (scheme and _SCHEME_URL.fullmatch(written)) or _WWW.fullmatch(written):
        kind = "url"
    elif _EMAIL.fullmatch(written):
        kind = "email"
    elif host and host.group().rsplit(".", 1)[1] in tlds and _DOMAIN.fullmatch(written):
        kind = "domain"
    else:
        kind = "run"
    return FrozenMap({"kind": kind, "scheme": scheme, "address": written[len(scheme) + 3:] if scheme else written})


@dataclass(frozen=True)
class Electronic:
    name: str = "electronic"
    form: Form = Form.ELECTRONIC

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """The claim of each token that holds a marker outside its blocks, split around its blocks and lexicon spans
        (design section 4.5). A block passes through as written, so no marker inside it counts. A single space
        separates the reading of each part from a block or a lexicon span that touches it."""
        data = request.data
        tlds = frozenset(data.get("electronic_tlds", ()))
        schemes = data.get("electronic_schemes", FrozenMap())
        lexicon = [(span.start, span.end) for recognizer in request.language.recognizers
                   if recognizer.form is Form.LEXICON and recognizer.form in request.params.forms
                   for span in recognizer.find(text, tokens, request) if not splits_token(span, tokens, text)]
        blocks = list(protect_blocks(text))
        gaps = _merged(blocks + lexicon)
        block = gap = 0
        for token in _TOKEN.finditer(text):
            start, stop = token.span()
            while block < len(blocks) and blocks[block][1] <= start:
                block += 1
            while gap < len(gaps) and gaps[gap][1] <= start:
                gap += 1
            if any(_marked(text, part_start, part_end, token, tlds)
                   for part_start, part_end in _parts(blocks, block, start, stop)):
                claim_start, claim_end = _claim(text, start, stop)
                for part_start, part_end in _parts(gaps, gap, claim_start, claim_end):
                    yield Span(part_start, part_end, Form.ELECTRONIC,
                               _fields(text[part_start:part_end], schemes, tlds),
                               lead=" " if part_start > claim_start else "", trail=" " if part_end < claim_end else "",
                               recognizer=self.name)


def _label(run: str, data) -> list[str]:
    """A label: a word as written when it holds a letter outside ASCII or a combining mark, or when the
    `electronic_labels` table says so, or by default when it has three or more letters and a vowel of the language;
    else each letter by its name."""
    if not run.isascii():
        return [run]
    known = data.get("electronic_labels", FrozenMap()).get(run.lower())
    vowels = frozenset(data["electronic_vowels"])
    if known == "word" or (known is None and len(run) >= 3 and any(c in vowels for c in run.lower())):
        return [run]
    return [data["letter_names"][c] for c in run.lower()]


def _pieces(written: str) -> Iterator[str]:
    """The labels and the single characters of a claim, in order. A label is a run of letters and marks."""
    label = None
    for index, char in enumerate(written):
        if is_letter(char) or is_mark(char):
            if label is None:
                label = index
            continue
        if label is not None:
            yield written[label:index]
            label = None
        yield char
    if label is not None:
        yield written[label:]


def _words(written: str, request: Request) -> list[str]:
    """The reading of each piece: a label as in an address, a digit of any script by its digit word, a symbol by
    its word, else by its `SYMBOL` name, and a character with no word as written."""
    data = request.data
    named = Form.SYMBOL in request.params.forms
    words: list[str] = []
    for piece in _pieces(written):
        if is_letter(piece[0]) or is_mark(piece[0]):
            words += _label(piece, data)
        elif is_digit(piece):
            words.append(data["digit_words"][int(piece)])
        elif piece in data["electronic_symbols"]:
            words.append(data["electronic_symbols"][piece])
        else:
            name = symbol_name(piece, request) if named else None
            words.append(name or piece)
    return words


def speak_electronic(span: Span, context: SpanContext) -> str:
    request = context.request
    scheme = span.fields["scheme"]
    words = []
    if scheme and request.data["electronic_schemes"][scheme] == "read":
        words = _words(scheme + "://", request)
    return " ".join(words + _words(span.fields["address"], request))


ELECTRONIC = Electronic()
