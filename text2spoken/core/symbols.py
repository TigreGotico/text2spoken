"""The `SYMBOL` form, a character that no other form claims read by its CLDR name, and the `EMOJI` form, an emoji
sequence read by its CLDR name (design section 4.7).

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
part of an emoji sequence, which the `EMOJI` form reads, so `©` followed by U+FE0F stays. The `EMOJI` form is off by
default. With it on, each emoji sequence reads by its name (`text2spoken.core.emoji`), so `😂😂` reads "face with tears
of joy face with tears of joy", and `❤` followed by U+FE0F reads "red heart".

A name of either form is one word or more of the sentence, so it takes one space on each side where it touches a
character that is no space. It takes none after an opening bracket or quote, and none before a closing bracket or quote
or another mark of the Unicode general category `Po`, such as a full stop or a comma. A straight quote at the start of a
token opens, so `He said "© 2024"` reads `He said "copyright two thousand and twenty-four"`. A mark that the `leads`
table of the language reads as words before a number takes the space, so `™#1` reads "trade mark number one". So `©2024`
reads "copyright two thousand and twenty-four", `©®` reads "copyright registered", `§§ 5` reads "section section five",
`∈$2` reads "element of two dollars", `©-5` reads "copyright minus five", and `(©).` reads "(copyright)." With `EMOJI`
on, `(😂).` reads "(face with tears of joy)."

A language file may give its own name for a character in `symbol_names`, with a quoted source. That name replaces the
CLDR name for that character only.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

from text2spoken.core.currencies import cldr_part, currency_signs, words_only
from text2spoken.core.emoji import JOINER, MODIFIERS, SELECTOR, emoji_name, name_reading, sequence_at
from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_digit, is_word_char
from text2spoken.core.units import unit_table
from text2spoken.params import FrozenMap, Form

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
    return after in (SELECTOR, JOINER) or after in MODIFIERS or text[index - 1:index] == JOINER


def reads_symbol(text: str, index: int, request: Request) -> bool:
    """Whether the `SYMBOL` form reads the character text[index] as words."""
    char = text[index]
    return (Form.SYMBOL in request.params.forms and char in _names(request)
            and not _in_emoji(text, index) and not _owned(char, request))


def _emoji_reading(text: str, start: int, request: Request) -> tuple[int, str, str | None] | None:
    """The end, the CLDR name and the reading of the emoji sequence at text[start], or None when no sequence with a
    name starts there. The reading is None when the name does not read, or when the sequence starts with a letter or
    a digit that a letter or a digit before it joins, as the digit of `x.org1️⃣` is joined: such a sequence stays as
    written, as a number joined to a word does."""
    found = emoji_name(text, start, request)
    if found is None or found[1] is None:
        return None
    end, name = found
    if start and is_word_char(text[start]) and is_word_char(text[start - 1]):
        return end, name, None
    return end, name, name_reading(name, request.tag, request.params)


def reads_emoji(text: str, index: int, request: Request) -> bool:
    """Whether the `EMOJI` form reads an emoji sequence that starts at text[index]."""
    if Form.EMOJI not in request.params.forms:
        return False
    found = _emoji_reading(text, index, request)
    return found is not None and found[2] is not None


def _emoji_readings(text: str, request: Request) -> Iterator[tuple[int, int, str, str]]:
    """The start, the end, the CLDR name and the reading of each emoji sequence that the `EMOJI` form reads, in text
    order."""
    index = 0
    while index < len(text):
        found = sequence_at(text, index)
        if found is None:
            index += 1
            continue
        reading = _emoji_reading(text, index, request)
        if reading is not None and reading[2] is not None:
            yield index, *reading
        index = found[1]


def named_pieces(text: str, request: Request) -> list[tuple[int, int, str]]:
    """The start, the end and the name of each piece of the text that `SYMBOL` or `EMOJI` reads, in text order."""
    symbols = [(index, index + 1, symbol_name(char, request)) for index, char in enumerate(text)
               if reads_symbol(text, index, request)]
    if Form.EMOJI not in request.params.forms:
        return symbols
    return sorted(symbols + [(start, end, reading) for start, end, _, reading in _emoji_readings(text, request)])


def _spacing(text: str, start: int, end: int, leads: Sequence[str], request: Request) -> tuple[str, str]:
    """The lead and the trail of a name that reads text[start:end]."""
    before = text[start - 1] if start else " "
    after = text[end] if end < len(text) else " "
    opens = unicodedata.category(before) in _OPENING or (
        before in _QUOTES and (start < 2 or text[start - 2].isspace()))
    lead = "" if before.isspace() or opens else " "
    number = any(text.startswith(word, end) and end + len(word) < len(text) and is_digit(text[end + len(word)])
                 for word in leads)
    closes = after.isspace() or (unicodedata.category(after) in _CLOSING and not number)
    trail = "" if closes or reads_symbol(text, end, request) or reads_emoji(text, end, request) else " "
    return lead, trail


def _leads(request: Request) -> list[str]:
    return [lead for lead, words in request.data.get("leads", FrozenMap()).items() if words]


@dataclass(frozen=True)
class Symbol:
    name: str = "symbol"
    form: Form = Form.SYMBOL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        leads = _leads(request)
        for index, char in enumerate(text):
            if reads_symbol(text, index, request):
                lead, trail = _spacing(text, index, index + 1, leads, request)
                yield Span(index, index + 1, Form.SYMBOL, FrozenMap({"symbol": char}), lead=lead, trail=trail,
                           recognizer=self.name)


def speak_symbol(span: Span, context: SpanContext) -> str:
    return symbol_name(span.fields["symbol"], context.request)


@dataclass(frozen=True)
class Emoji:
    name: str = "emoji"
    form: Form = Form.EMOJI

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        leads = _leads(request)
        for start, end, name, _ in _emoji_readings(text, request):
            lead, trail = _spacing(text, start, end, leads, request)
            yield Span(start, end, Form.EMOJI, FrozenMap({"sequence": text[start:end], "name": name}), lead=lead,
                       trail=trail, recognizer=self.name)


def speak_emoji(span: Span, context: SpanContext) -> str:
    request = context.request
    return name_reading(span.fields["name"], request.tag, request.params)


SYMBOL = Symbol()
EMOJI = Emoji()
