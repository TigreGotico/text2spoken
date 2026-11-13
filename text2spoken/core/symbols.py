"""The `SYMBOL` form: a character that no other form claims, read by its CLDR name (design section 4.7).

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/<tag>.symbols.json`: the `tts` name of each character
outside ASCII whose Unicode general category is `Sm`, `Sc`, `Sk` or `So`, or that is one of `§ ¶ † ‡ • ‰ ‱`, and
that is no emoji with emoji presentation by default. So `©` reads "copyright" and `→` reads "right-pointing arrow"
in English. A name that holds a character other than a letter, a space, `-` or `'`, such as "A button (blood
type)", does not read, because a reading holds words only (design section 11).

A character that a table of the language gives to another form belongs to that form: a character of the `symbols`
table or a unit symbol, as `°` and `‰` belong to `MEASURE`, an operator, and a currency sign that `MONEY` reads. Such
a character stays as written when its form does not read it, so `It is 20° today.` gives no "twenty degree", `3/4 ‰`
stays as written as `3/4 kg` does, and `−−3 × 3` stays as written on the first pass and on the second.

A character that the form reads is a word of the reading, so it stands between a phone word and the digits after it
as a word does: `Ligue → 1.234,56` reads the number, on the first pass and on the second.

An emoji presentation selector (U+FE0F), a skin tone modifier or a zero width joiner next to a character makes it
part of an emoji sequence, which the `EMOJI` form reads, so `©` followed by U+FE0F stays.

A name takes one space before it when the character before it is no space and no punctuation, and one space after
it when a letter, a digit or a combining mark follows, so `©2024` reads "copyright two thousand and twenty-four"
and `©®` reads "copyright registered".
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

from text2spoken.core.currencies import cldr_part, currency_table
from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_punctuation, is_word_char
from text2spoken.core.units import unit_table
from text2spoken.params import FrozenMap, Form

_PRESENTATION = "\ufe0f"
_JOINER = "\u200d"
_MODIFIERS = frozenset(map(chr, range(0x1F3FB, 0x1F400)))


def _words_only(name: str) -> bool:
    return all(char.isalpha() or char.isspace() or char in "-'" for char in name)


@lru_cache(maxsize=None)
def _names(tag: str) -> FrozenMap:
    return FrozenMap((char, name) for char, name in cldr_part(tag, "symbols").get("symbols", FrozenMap()).items()
                     if _words_only(name))


@lru_cache(maxsize=64)
def _signs(table: FrozenMap) -> frozenset[str]:
    return frozenset(symbol for currency in table.values() for symbol in currency["symbols"])


def _owned(char: str, request: Request) -> bool:
    """Whether a table of the language gives the character to another form: the `symbols` table, a unit symbol, an
    operator or a currency sign that `MONEY` reads."""
    data = request.data
    return (char in data.get("symbols", FrozenMap()) or char in unit_table(request)
            or char in data.get("operators", FrozenMap()) or char in _signs(currency_table(request)))


def symbol_name(char: str, request: Request) -> str | None:
    """The CLDR name of a character that the `SYMBOL` form reads, or None."""
    name = _names(request.variety.tag).get(char)
    return None if name is None or _owned(char, request) else name


def _in_emoji(text: str, index: int) -> bool:
    after = text[index + 1:index + 2]
    return after in (_PRESENTATION, _JOINER) or after in _MODIFIERS or text[index - 1:index] == _JOINER


def reads_symbol(text: str, index: int, request: Request) -> bool:
    """Whether the `SYMBOL` form reads the character text[index] as words."""
    char = text[index]
    return (Form.SYMBOL in request.params.forms and char in _names(request.variety.tag)
            and not _in_emoji(text, index) and not _owned(char, request))


@dataclass(frozen=True)
class Symbol:
    name: str = "symbol"
    form: Form = Form.SYMBOL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for index, char in enumerate(text):
            if not reads_symbol(text, index, request):
                continue
            before = text[index - 1] if index else " "
            lead = "" if before.isspace() or is_punctuation(before) else " "
            trail = " " if index + 1 < len(text) and is_word_char(text[index + 1]) else ""
            yield Span(index, index + 1, Form.SYMBOL, FrozenMap({"symbol": char}), lead=lead, trail=trail,
                       recognizer=self.name)


def speak_symbol(span: Span, context: SpanContext) -> str:
    return symbol_name(span.fields["symbol"], context.request)


SYMBOL = Symbol()
