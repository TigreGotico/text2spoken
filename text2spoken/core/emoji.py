"""The emoji sequences of a text and their CLDR names, for the `EMOJI` form (design section 4.7).

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/emoji-sequences.json`, each sequence of the Unicode emoji files
as Unicode writes it, and `text2spoken/data/cldr/<tag>.emoji.json`, the CLDR `tts` name of each sequence. CLDR keys a
sequence without U+FE0F, so the lookup ignores U+FE0F.

An emoji is the longest sequence of the file at a position, with each U+FE0F in it and a U+FE0F after it. A character
with text presentation by default, such as `❤` or `©`, is an emoji only before U+FE0F, a skin tone or a zero width
joiner, so a bare `❤` stays with `SYMBOL`. Any other character that is no space is an emoji before one of these too,
so `a🏽` and `⋂🏿` belong to `EMOJI`. An emoji sequence is an emoji with the skin tones, U+FE0F and zero width joiners
after it, where each joiner takes the emoji after it. So `👍🏽` is one sequence, and `😂😂` is two.

A sequence reads by its name. A sequence with no name reads by the name of its first emoji, and an emoji with no name
stays as written, as `a🏽` does. A name reads in three steps. First, each quote mark goes, and each `:`, `,`, `(` and
`)` becomes a space. U+2019 between two letters is an apostrophe, not a quote mark, so it stays. Second, the result goes
through `normalize` with the same language and forms, without `EMOJI`, so pt-PT `polegar para cima: tipo de pele 4`
reads "polegar para cima tipo de pele quatro" and en `1st place medal` reads "first place medal". Third, a reading that
still holds a character other than a letter, a combining mark, a space, `-`, `'` or U+2019 does not read, and the
emoji stays as written, as en `flag: Antigua & Barbuda` and `keycap: #` do. So en `one o’clock` reads.
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import replace
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.currencies import cldr_part
from text2spoken.core.language import Request
from text2spoken.core.tokens import EMOJI_MARKS, STAND_IN
from text2spoken.params import Form, NormalizationParams

SELECTOR = "️"
JOINER = "‍"
MODIFIERS = frozenset(map(chr, range(0x1F3FB, 0x1F400)))
REGIONAL_INDICATORS = frozenset(map(chr, range(0x1F1E6, 0x1F200)))
_QUOTES = frozenset("\"“”‘’")
_APOSTROPHE = "’"
_SPACES = frozenset(":,()")


@lru_cache(maxsize=1)
def _sequences() -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """The sequences with U+FE0F removed, each start of one, and the characters that Unicode writes with U+FE0F as
    an emoji of their own: the characters with text presentation by default."""
    path = files("text2spoken") / "data" / "cldr" / "emoji-sequences.json"
    written = json.loads(path.read_text(encoding="utf-8"))["sequences"]
    keys = frozenset(sequence.replace(SELECTOR, "") for sequence in written)
    starts = frozenset(key[:end] for key in keys for end in range(1, len(key) + 1))
    text = frozenset(sequence[0] for sequence in written if sequence[1:] == SELECTOR)
    return keys, starts, text


def _second_indicator(text: str, index: int) -> bool:
    """Whether text[index] is a regional indicator that pairs with the one before it. UAX #29 rules GB12 and GB13
    pair regional indicators from the start of a run: "Do not break within emoji flag sequences. That is, do not
    break between regional indicator (RI) symbols if there is an odd number of RI characters before the break
    point." So `🇵🇵🇹` is the pair `🇵🇵` and a lone `🇹`, and no flag of Portugal."""
    count = 0
    while index - count > 0 and text[index - count - 1] in REGIONAL_INDICATORS:
        count += 1
    return text[index] in REGIONAL_INDICATORS and count % 2 == 1


def _emoji(text: str, index: int, joined: bool) -> int | None:
    """The end of the emoji at text[index], or None. A character that is no space, before U+FE0F, a skin tone or a
    zero width joiner, is an emoji, even when the emoji files do not hold it. After a zero width joiner (`joined`),
    a character with text presentation is an emoji with nothing after it."""
    if text[index:index + 1] in ("", SELECTOR) or _second_indicator(text, index):
        return None
    keys, starts, text_presentation = _sequences()
    key, end, position = "", None, index
    while position < len(text):
        char = text[position]
        position += 1
        if char == SELECTOR:
            continue
        key += char
        if key not in starts:
            break
        if key in keys:
            end = position
    after = text[index + 1:index + 2]
    marked = (after == SELECTOR or after == JOINER or after in MODIFIERS) and not text[index].isspace()
    if end == index + 1 and text[index] in text_presentation and not (joined or marked):
        return None
    if end is None:
        if joined or not marked:
            return None
        end = index + 1
    return end + 1 if text[end:end + 1] == SELECTOR else end


def sequence_at(text: str, index: int) -> tuple[int, int] | None:
    """The end of the first emoji and the end of the emoji sequence that start at text[index], or None."""
    first = _emoji(text, index, False)
    if first is None:
        return None
    end = first
    while end < len(text):
        if text[end] == SELECTOR or text[end] in MODIFIERS:
            end += 1
        elif text[end] == JOINER and (following := _emoji(text, end + 1, True)) is not None:
            end = following
        else:
            break
    return first, end


@lru_cache(maxsize=64)
def sequences_in(text: str) -> tuple[tuple[int, int], ...]:
    """The start and the end of each emoji sequence of the text, in text order."""
    found, index = [], 0
    while index < len(text):
        sequence = sequence_at(text, index)
        if sequence is None:
            index += 1
        else:
            found.append((index, sequence[1]))
            index = sequence[1]
    return tuple(found)


@lru_cache(maxsize=64)
def emoji_view(text: str) -> str:
    """The text as every form other than `EMOJI` and `ELECTRONIC` reads it. A character of an emoji sequence that
    U+FE0E, U+FE0F or U+20E3 follows belongs to the sequence (design section 4.7). When it is no symbol, as the digit
    of `1️⃣` and the `#` of `#️⃣` are, it is U+FFFC here, a symbol that no form reads, so no number takes it. A symbol
    stays, because `SYMBOL` already leaves a symbol that such a mark follows. The view has the length of the text, so
    a span of the view is the same span of the text."""
    chars = list(text)
    for start, end in sequences_in(text):
        for index in range(start, end - 1):
            if text[index + 1] in EMOJI_MARKS and not unicodedata.category(text[index]).startswith(("S", "M")):
                chars[index] = STAND_IN
    return "".join(chars)


def written_text(text: str, request: Request) -> str:
    """The text as written, for a text that may be the view of `classify`. The recognizers read the view, and a
    recognizer that names an emoji sequence reads the sequence as written."""
    return request.memo.get(("written", text), text)


def _apostrophe(name: str, index: int) -> bool:
    """Whether name[index] is U+2019 between two letters, an apostrophe and no quote mark."""
    return (name[index] == _APOSTROPHE and 0 < index < len(name) - 1
            and name[index - 1].isalpha() and name[index + 1].isalpha())


@lru_cache(maxsize=4096)
def name_reading(name: str, tag: str, params: NormalizationParams) -> str | None:
    """The reading of a CLDR name in the three steps, or None when the reading holds a character that is no word."""
    from text2spoken.core.pipeline import normalize

    plain = "".join(" " if char in _SPACES else "" if char in _QUOTES and not _apostrophe(name, index) else char
                    for index, char in enumerate(name))
    spoken = normalize(" ".join(plain.split()), tag, replace(params.without(Form.EMOJI), strict=False))
    if all(char.isalpha() or unicodedata.category(char).startswith("M") or char == " " or char in "-'’"
           for char in spoken):
        return spoken
    return None


def emoji_name(text: str, start: int, request: Request) -> tuple[int, str | None] | None:
    """The end of the emoji sequence at text[start] and the CLDR name that it reads by, None when no name holds it,
    or None when no sequence starts there."""
    found = sequence_at(text, start)
    if found is None:
        return None
    first, end = found
    names = cldr_part(request.variety.tag, "emoji").get("names", {})
    return end, names.get(text[start:end].replace(SELECTOR, "")) or names.get(text[start:first].replace(SELECTOR, ""))
