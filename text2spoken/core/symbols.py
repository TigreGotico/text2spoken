"""The `SYMBOL` form: a character that no other form claims, read by its CLDR name (design section 4.7).

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/<tag>.symbols.json`: the `tts` name of each character
outside ASCII whose Unicode general category is `Sm`, `Sc`, `Sk` or `So`, or that is one of `§ ¶ † ‡ •`, and
that is no emoji with emoji presentation by default. So `©` reads "copyright" and `→` reads "right-pointing arrow"
in English. A name that holds a character other than a letter, a space, `-` or `'`, such as "A button (blood
type)", does not read, because a reading holds words only (design section 11).

A character that a table of the language gives to another form belongs to that form: a character of the `symbols`
table or a unit symbol, as `°` and `‰` belong to `MEASURE`, an operator, and a symbol of the currency table, as `€`
and `¤` belong to `MONEY`. Such a character stays as written wherever it stands when its form does not read it, so
`It is 20° today.` gives no "twenty degree", `3/4 ‰` stays as written as `3/4 kg` does, `the € sign` stays as
written, and `−−3 × 3` stays as written on the first pass and on the second.

A character that the form reads is a word of the reading, so a phone word before it keeps no run of digits after
it: `Ligue → 1.234,56` reads the number, on the first pass and on the second. The phone word still names a phone
number, so `Call ☎ 2125550123.` reads digit by digit.

An emoji presentation selector (U+FE0F), a skin tone modifier or a zero width joiner next to a character makes it
part of an emoji sequence, which the `EMOJI` form reads, so `©` followed by U+FE0F stays.

A name is one word or more of the sentence, so it takes one space on each side where it touches a character that is
no space. It takes none after an opening bracket or quote, and none before a closing bracket or quote or another
mark of the Unicode general category `Po`, such as a full stop or a comma. A straight quote at the start of a token
opens, so `He said "© 2024"` reads `He said "copyright two thousand and twenty-four"`. A mark that the `leads` table
of the language reads as words before a number takes the space, so `™#1` reads "trade mark number one". So `©2024`
reads "copyright two thousand and twenty-four", `©®` reads "copyright registered", `§§ 5` reads "section section
five", `∈$2` reads "element of two dollars", `©-5` reads "copyright minus five", and `(©).` reads "(copyright)."

A language file may give its own name for a character in `symbol_names`, with a quoted source. That name replaces the
CLDR name for that character only.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

from text2spoken.core.currencies import cldr_part, currency_signs, words_only
from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_digit
from text2spoken.core.units import unit_table
from text2spoken.params import FrozenMap, Form

_PRESENTATION = "\ufe0f"
_JOINER = "\u200d"
_MODIFIERS = frozenset(map(chr, range(0x1F3FB, 0x1F400)))
_OPENING = ("Ps", "Pi")
_CLOSING = ("Pe", "Pf", "Po")
_QUOTES = "\"'"


@lru_cache(maxsize=64)
def _table(tag: str, own: FrozenMap) -> FrozenMap:
    cldr = cldr_part(tag, "symbols").get("symbols", FrozenMap())
    return FrozenMap({**{char: name for char, name in cldr.items() if words_only(name)}, **own})


def _names(request: Request) -> FrozenMap:
    """The name of each character that the variety names: the CLDR names with the `symbol_names` of the language
    file over them."""
    return _table(request.variety.tag, request.data.get("symbol_names", FrozenMap()))


def _owned(char: str, request: Request) -> bool:
    """Whether a table of the language gives the character to another form: the `symbols` table, a unit symbol, an
    operator or a symbol of the currency table."""
    data = request.data
    return (char in data.get("symbols", FrozenMap()) or char in unit_table(request)
            or char in data.get("operators", FrozenMap()) or char in currency_signs(request))


def symbol_name(char: str, request: Request) -> str | None:
    """The CLDR name of a character that the `SYMBOL` form reads, or None."""
    name = _names(request).get(char)
    return None if name is None or _owned(char, request) else name


def _in_emoji(text: str, index: int) -> bool:
    after = text[index + 1:index + 2]
    return after in (_PRESENTATION, _JOINER) or after in _MODIFIERS or text[index - 1:index] == _JOINER


def reads_symbol(text: str, index: int, request: Request) -> bool:
    """Whether the `SYMBOL` form reads the character text[index] as words."""
    char = text[index]
    return (Form.SYMBOL in request.params.forms and char in _names(request)
            and not _in_emoji(text, index) and not _owned(char, request))


@dataclass(frozen=True)
class Symbol:
    name: str = "symbol"
    form: Form = Form.SYMBOL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        leads = [lead for lead, words in request.data.get("leads", FrozenMap()).items() if words]
        for index, char in enumerate(text):
            if not reads_symbol(text, index, request):
                continue
            before = text[index - 1] if index else " "
            after = text[index + 1] if index + 1 < len(text) else " "
            opens = unicodedata.category(before) in _OPENING or (
                before in _QUOTES and (index < 2 or text[index - 2].isspace()))
            lead = "" if before.isspace() or opens else " "
            number = any(text.startswith(word, index + 1) and index + 1 + len(word) < len(text)
                         and is_digit(text[index + 1 + len(word)]) for word in leads)
            closes = after.isspace() or (unicodedata.category(after) in _CLOSING and not number)
            trail = "" if closes or reads_symbol(text, index + 1, request) else " "
            yield Span(index, index + 1, Form.SYMBOL, FrozenMap({"symbol": char}), lead=lead, trail=trail,
                       recognizer=self.name)


def speak_symbol(span: Span, context: SpanContext) -> str:
    return symbol_name(span.fields["symbol"], context.request)


SYMBOL = Symbol()
