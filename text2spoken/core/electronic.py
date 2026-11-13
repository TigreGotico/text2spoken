"""The e-mail and web address recognizer and its verbalizer: the `ELECTRONIC` rows of design section 4.2 and the
reading of section 4.5.

The recognizer claims an e-mail address, a URL that starts with a scheme of the `electronic_schemes` table or with
`www.`, and a bare domain whose top-level domain is in the `electronic_tlds` table. The verbalizer reads the
address piece by piece from the tables of the language file: a run of letters as a word or letter by letter, each
digit by its digit word, and each symbol by its word. An address with a character that the tables do not name
stays as written (design section 10).
"""
from __future__ import annotations

import re
from bisect import bisect_right
from itertools import accumulate
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_word_char
from text2spoken.errors import DeclinedReading
from text2spoken.params import FrozenMap, Form

_LABEL = "[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
_HOST = f"(?:{_LABEL}[.])+[A-Za-z]+"
_REST = "(?::[0-9]+)?(?:[/?#][A-Za-z0-9._~:/?#@!$&'()*+,;=%-]*)?"
_HOST_START = re.compile(_HOST)
_SCHEME_URL = re.compile(f"([A-Za-z][A-Za-z0-9+.-]*)://{_HOST}{_REST}")
_EMAIL = re.compile(f"[A-Za-z0-9._+-]+@{_HOST}")
_WWW = re.compile(f"[Ww][Ww][Ww][.]{_HOST}{_REST}")
_DOMAIN = re.compile(f"{_HOST}{_REST}")
_RUNS = {
    _SCHEME_URL: (re.compile("[A-Za-z0-9+.-]+"), re.compile("[A-Za-z]")),
    _EMAIL: (re.compile("[A-Za-z0-9._+-]+"), re.compile("[A-Za-z0-9._+-]")),
    _DOMAIN: (re.compile(f"{_LABEL}(?:[.]{_LABEL})*"), re.compile("[A-Za-z0-9]")),
}
"""For each pattern, a run of characters and the characters that can start the pattern. A match that starts inside
the run also starts at the first start character of the run, so `_matches` tries the pattern there only, and a long
run costs one try, not one try for each character."""
_WWW_START = re.compile("[Ww][Ww][Ww][.]")
_BEFORE = frozenset("._%+-@/~#?=&")
"""Characters that continue an address to the left, so a match that starts after one starts inside an address."""
_JOINERS = frozenset("-_+")
_CONTINUES = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._+-@")
"""A joiner of `_JOINERS` before a character of `_CONTINUES` continues an address to the right."""
_TOKEN = re.compile("[^\t-\r\x1c-\x20\x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+")
"""A run of characters between spaces, with the space characters of `str.isspace`."""
_TRAILING = ".,;:!?'\""
_PIECE = re.compile("[A-Za-z]+|[0-9]|.")


def _trimmed(text: str, start: int, end: int) -> int:
    """The end of an address without the punctuation that closes the sentence or a bracket around it."""
    opening, closing = text.count("(", start, end), text.count(")", start, end)
    while end > start:
        last = text[end - 1]
        if last == ")" and opening < closing:
            closing -= 1
        elif last not in _TRAILING:
            break
        end -= 1
    return end


def _free(text: str, start: int, end: int) -> bool:
    return ((start == 0 or not (is_word_char(text[start - 1]) or text[start - 1] in _BEFORE))
            and (end == len(text) or not (is_word_char(text[end]) or text[end] == "@"
                                          or (text[end] in _JOINERS and text[end + 1:end + 2] in _CONTINUES))))


def _matches(pattern: re.Pattern, text: str) -> Iterator[re.Match]:
    """The matches that `pattern.finditer(text)` gives, found with one try in each run of `_RUNS`."""
    runs, starts = _RUNS[pattern]
    end = 0
    for run in runs.finditer(text):
        first = starts.search(text, max(run.start(), end), run.end())
        if first and (match := pattern.match(text, first.start())):
            end = match.end()
            yield match


def _www_matches(text: str) -> Iterator[re.Match]:
    """The matches that `_WWW.finditer(text)` gives. A host that starts inside a chain of labels also starts at the
    start of the chain, so a chain where no host starts is read once, not once after each `www.` in it."""
    chains = list(_RUNS[_DOMAIN][0].finditer(text))
    starts = [chain.start() for chain in chains]
    hosts: dict[int, bool] = {}
    end = 0
    for prefix in _WWW_START.finditer(text):
        if prefix.start() < end:
            continue
        index = bisect_right(starts, prefix.end()) - 1
        if index >= 0 and prefix.end() < chains[index].end():
            chain = starts[index]
            if chain not in hosts:
                hosts[chain] = _HOST_START.match(text, chain) is not None
            if not hosts[chain]:
                continue
        if match := _WWW.match(text, prefix.start()):
            end = match.end()
            yield match


@dataclass(frozen=True)
class Electronic:
    name: str = "electronic"
    form: Form = Form.ELECTRONIC

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        tlds = frozenset(request.data.get("electronic_tlds", ()))
        addresses = list(self._addresses(text, request, tlds))
        yield from addresses
        yield from self._kept(text, addresses, tlds)

    def _kept(self, text: str, addresses: Sequence[Span], tlds: frozenset[str]) -> Iterator[Span]:
        """A token between spaces that holds a run of labels joined by full stops, ending in a label of
        `electronic_tlds`, but that holds no address, stays whole as written (design section 4.5)."""
        bounds = sorted((span.start, span.end) for span in addresses)
        starts, ends = [start for start, _ in bounds], list(accumulate((end for _, end in bounds), max))
        chains = _RUNS[_DOMAIN][0]
        for token in _TOKEN.finditer(text):
            index = bisect_right(starts, token.end() - 1) - 1
            if index >= 0 and ends[index] > token.start():
                continue
            if any(chain.group().rsplit(".", 1)[-1] in tlds
                   and ("." in chain.group() or text[chain.start() - 1:chain.start()] == ".")
                   for chain in chains.finditer(text, token.start(), token.end())):
                yield Span(token.start(), token.end(), Form.ELECTRONIC,
                           FrozenMap({"kind": "domain", "scheme": "", "address": token.group()}),
                           recognizer=self.name, keep=True)

    def _addresses(self, text: str, request: Request, tlds: frozenset[str]) -> Iterator[Span]:
        schemes = request.data.get("electronic_schemes", FrozenMap())
        for kind, pattern in (("url", _SCHEME_URL), ("email", _EMAIL), ("url", _WWW), ("domain", _DOMAIN)):
            for match in _www_matches(text) if pattern is _WWW else _matches(pattern, text):
                start = match.start()
                end = _trimmed(text, start, match.end())
                scheme = match.group(1).lower() if pattern is _SCHEME_URL else ""
                if not _free(text, start, end) or (pattern is _SCHEME_URL and scheme not in schemes):
                    continue
                address = text[start + len(scheme) + 3 if scheme else start:end]
                if pattern is _DOMAIN:
                    host = _HOST_START.match(address).group()
                    if host.rsplit(".", 1)[1] not in tlds:
                        continue
                yield Span(start, end, Form.ELECTRONIC,
                           FrozenMap({"kind": kind, "scheme": scheme, "address": address}), recognizer=self.name)


def _label(run: str, data) -> list[str]:
    """A run of letters: a word when the `electronic_labels` table says so, or by default when it has three or more
    letters and a vowel of the language; else each letter by its name."""
    known = data.get("electronic_labels", FrozenMap()).get(run.lower())
    vowels = frozenset(data["electronic_vowels"])
    if known == "word" or (known is None and len(run) >= 3 and any(c in vowels for c in run.lower())):
        return [run]
    return [data["letter_names"][c] for c in run.lower()]


def _words(written: str, data) -> list[str]:
    words: list[str] = []
    for piece in _PIECE.findall(written):
        if piece.isascii() and piece.isalpha():
            words += _label(piece, data)
        elif piece.isascii() and piece.isdigit():
            words.append(data["digit_words"][int(piece)])
        elif piece in data["electronic_symbols"]:
            words.append(data["electronic_symbols"][piece])
        else:
            raise DeclinedReading(f"no word for {piece!r} in an address")
    return words


def speak_electronic(span: Span, context: SpanContext) -> str:
    data = context.request.data
    scheme = span.fields["scheme"]
    words = []
    if scheme and data["electronic_schemes"][scheme] == "read":
        words = _words(scheme + "://", data)
    return " ".join(words + _words(span.fields["address"], data))


ELECTRONIC = Electronic()
