"""The colour recognizer: the `COLOR` rows of design section 4.2."""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import accumulate

from text2spoken.core.language import Request
from text2spoken.core.spans import Clauses, Span, clause_breaks, context_words
from text2spoken.core.tokens import Token, is_word_char
from text2spoken.params import FrozenMap, Form

_HEX = re.compile("#(?:[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])(?:[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])?(?:[0-9A-Fa-f][0-9A-Fa-f])?")
_DIGITS = frozenset("0123456789")


def hex_fields(code: str) -> FrozenMap | None:
    """`rgb` as six lowercase hex digits, `alpha` as two or None, and `hex` as the digits that the text writes,
    from 3, 6 or 8 hex digits after `#`."""
    digits = code[1:].lower()
    if len(digits) == 3:
        return FrozenMap({"rgb": "".join(d * 2 for d in digits), "alpha": None, "hex": code[1:]})
    if len(digits) in (6, 8):
        return FrozenMap({"rgb": digits[:6], "alpha": digits[6:] or None, "hex": code[1:7]})
    return None


def _is_color_word(word: str, color_words: frozenset[str]) -> bool:
    return word.lower() in color_words or word.lower().rsplit("-", 1)[-1] in color_words


@dataclass(frozen=True)
class Color:
    name: str = "color"
    form: Form = Form.COLOR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        color_words = frozenset(w.lower() for w in request.data.get("color_words", ()))
        words = context_words(tokens)
        clauses = Clauses(words, clause_breaks(text))
        colored = list(accumulate((_is_color_word(word.text, color_words) for word in words), initial=0))
        for match in _HEX.finditer(text):
            start, end = match.span()
            if (start and is_word_char(text[start - 1])) or (end < len(text) and is_word_char(text[end])):
                continue
            fields = hex_fields(match.group())
            if fields is None:
                continue
            digits = set(match.group()[1:])
            mixed = bool(digits & _DIGITS) and bool(digits - _DIGITS)
            if not mixed and not any(colored[side.stop] > colored[side.start] for side in clauses.around(start, end)):
                continue
            yield Span(start, end, Form.COLOR, fields, recognizer=self.name)


COLOR = Color()
