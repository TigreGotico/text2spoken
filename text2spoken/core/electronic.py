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
_SCHEME_URL = re.compile(f"([A-Za-z][A-Za-z0-9+.-]*)://{_HOST}{_REST}")
_EMAIL = re.compile(f"[A-Za-z0-9._+-]+@{_HOST}")
_WWW = re.compile(f"[Ww][Ww][Ww][.]{_HOST}{_REST}")
_DOMAIN = re.compile(f"{_HOST}{_REST}")
_BEFORE = frozenset("._%+-@/~#?=&")
"""Characters that continue an address to the left, so a match that starts after one starts inside an address."""
_TRAILING = ".,;:!?'\""
_PIECE = re.compile("[A-Za-z]+|[0-9]|.")


def _trimmed(text: str, start: int, end: int) -> int:
    """The end of an address without the punctuation that closes the sentence or a bracket around it."""
    while end > start:
        last = text[end - 1]
        if last in _TRAILING or (last == ")" and text.count("(", start, end) < text.count(")", start, end)):
            end -= 1
        else:
            break
    return end


def _free(text: str, start: int, end: int) -> bool:
    return ((start == 0 or not (is_word_char(text[start - 1]) or text[start - 1] in _BEFORE))
            and (end == len(text) or not (is_word_char(text[end]) or text[end] == "@")))


@dataclass(frozen=True)
class Electronic:
    name: str = "electronic"
    form: Form = Form.ELECTRONIC

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        schemes = request.data.get("electronic_schemes", FrozenMap())
        tlds = frozenset(request.data.get("electronic_tlds", ()))
        for kind, pattern in (("url", _SCHEME_URL), ("email", _EMAIL), ("url", _WWW), ("domain", _DOMAIN)):
            for match in pattern.finditer(text):
                start = match.start()
                end = _trimmed(text, start, match.end())
                scheme = match.group(1).lower() if pattern is _SCHEME_URL else ""
                if not _free(text, start, end) or (pattern is _SCHEME_URL and scheme not in schemes):
                    continue
                address = text[start + len(scheme) + 3 if scheme else start:end]
                if pattern is _DOMAIN:
                    host = re.match(_HOST, address).group()
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
