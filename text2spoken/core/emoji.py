"""The emoji sequences of a text and their spoken names, for the `EMOJI` form (design section 4.7).

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/<tag>.emoji.json`, which maps each emoji sequence of the
Unicode emoji files, without U+FE0F, to the spoken form of its CLDR `tts` name, or to null when the name does not read
as words.

An emoji sequence is the longest key of a table at a position, with each U+FE0F in it and after it ignored, followed by
the skin tones, U+FE0F and the zero width joiners after it, where each joiner takes the next key. The keys of every
table find the sequences, so a text cuts the same way in each language. A sequence reads by its name in the table of
the variety. A sequence that is no key reads by the name of its first key. A sequence with no name stays as written.
"""
from __future__ import annotations

import unicodedata
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.currencies import cldr_part
from text2spoken.core.language import Request
from text2spoken.core.tokens import EMOJI_MARKS, STAND_IN, is_word_char

SELECTOR = "️"
JOINER = "‍"
MODIFIERS = frozenset(map(chr, range(0x1F3FB, 0x1F400)))


@lru_cache(maxsize=1)
def _keys() -> tuple[frozenset[str], int]:
    """The keys of every emoji table, and the length of the longest."""
    keys = frozenset(key for path in (files("text2spoken") / "data" / "cldr").iterdir()
                     if path.name.endswith(".emoji.json") for key in cldr_part(path.name[:-11], "emoji")["names"])
    return keys, max(map(len, keys))


def _key_end(text: str, index: int) -> int | None:
    """The end of the longest key at text[index], with the U+FE0F in it and after it, or None."""
    keys, longest = _keys()
    key, end, position = "", None, index
    while position < len(text) and len(key) < longest:
        char = text[position]
        position += 1
        if char != SELECTOR:
            key += char
            if key in keys:
                end = position
        elif not key:
            return None
    if end is not None and text[end:end + 1] == SELECTOR:
        end += 1
    return end


def sequence_at(text: str, index: int) -> tuple[int, int] | None:
    """The end of the first key and the end of the emoji sequence that start at text[index], or None."""
    first = _key_end(text, index)
    if first is None:
        return None
    end = first
    while end < len(text):
        if text[end] == SELECTOR or text[end] in MODIFIERS:
            end += 1
        elif text[end] == JOINER and (following := _key_end(text, end + 1)) is not None:
            end = following
        else:
            break
    return first, end


def sequences_in(text: str, memo: dict) -> tuple[tuple[int, int], ...]:
    """The start and the end of each emoji sequence of the text, in text order. `memo` keeps them for the call."""
    key = ("sequences", text)
    if key not in memo:
        found, index = [], 0
        while index < len(text):
            sequence = sequence_at(text, index)
            if sequence is None:
                index += 1
            else:
                found.append((index, sequence[1]))
                index = sequence[1]
        memo[key] = tuple(found)
    return memo[key]


def touches_word(text: str, start: int, end: int) -> bool:
    """Whether the emoji sequence text[start:end] stays as written because it touches a word. Design section 4.7: "An
    emoji sequence that starts with a letter or a digit and touches a letter or a digit on its left stays as written
    (`12️⃣`)." The sequence must hold U+FE0E, U+FE0F or U+20E3, as each sequence that the view hides does."""
    return (start > 0 and is_word_char(text[start]) and is_word_char(text[start - 1])
            and any(char in EMOJI_MARKS for char in text[start:end]))


def touched_words(text: str, memo: dict) -> tuple[tuple[int, int, int], ...]:
    """The start of the touched word, the start and the end of each emoji sequence that touches a word
    (`touches_word`), in text order. Design section 4.7: such a sequence "stays as written, together with the word it
    touches". The word is the run of letters, digits and marks right before the sequence, back to the sequence before
    it. A space, a symbol or a punctuation mark ends it, so the `2` of `2,cats1️⃣` and the date of
    `12/03/2024.Next1️⃣` stay out of it and read. `memo` keeps the result for the call."""
    key = ("touched", text)
    if key not in memo:
        found, previous = [], 0
        for start, end in sequences_in(text, memo):
            if touches_word(text, start, end):
                word = start
                while word > previous and is_word_char(text[word - 1]):
                    word -= 1
                found.append((word, start, end))
            previous = end
        memo[key] = tuple(found)
    return memo[key]


def emoji_view(text: str, memo: dict) -> str:
    """The text as every form other than `EMOJI` and `ELECTRONIC` reads it. A character of an emoji sequence that
    U+FE0E, U+FE0F or U+20E3 follows belongs to the sequence (design section 4.7). When it is no symbol, as the digit
    of `1️⃣` and the `#` of `#️⃣` are, it is U+FFFC here, a symbol that no form reads, so no number takes it. A symbol
    stays, because `SYMBOL` already leaves a symbol that such a mark follows. The view has the length of the text, so
    a span of the view is the same span of the text.

    A sequence that touches a word stays as written together with the word it touches (`touched_words`), so every
    character of that word is U+FFFC too: `Code 12️⃣` keeps `12️⃣`, and `I have 2,cats1️⃣` still reads the `2`. `memo`
    keeps the view for the call."""
    key = ("view", text)
    if key not in memo:
        chars = list(text)
        for word, start, _ in touched_words(text, memo):
            chars[word:start + 1] = STAND_IN * (start + 1 - word)
        for start, end in sequences_in(text, memo):
            for index in range(start, end - 1):
                if text[index + 1] in EMOJI_MARKS and not unicodedata.category(text[index]).startswith(("S", "M")):
                    chars[index] = STAND_IN
        memo[key] = "".join(chars)
    return memo[key]


def written_text(text: str, request: Request) -> str:
    """The text as written, for a text that may be the view of `classify`. The recognizers read the view, and a
    recognizer that names an emoji sequence reads the sequence as written."""
    return request.memo.get(("written", text), text)


def emoji_reading(text: str, start: int, request: Request) -> tuple[int, str | None] | None:
    """The end of the emoji sequence at text[start] and its spoken name, None when no name reads it, or None when no
    sequence starts there."""
    found = sequence_at(text, start)
    if found is None:
        return None
    first, end = found
    names = cldr_part(request.variety.tag, "emoji").get("names", {})
    key = text[start:end].replace(SELECTOR, "")
    return end, names[key] if key in names else names.get(text[start:first].replace(SELECTOR, ""))
