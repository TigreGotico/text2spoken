"""Tokens, the tokenizer hook, inline blocks and digit folding (design section 2.1)."""
from __future__ import annotations

import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from text2spoken.errors import TokenizerError


@dataclass(frozen=True)
class Token:
    start: int
    end: int
    text: str
    clause_end: bool = False


class Tokenizer(Protocol):
    def __call__(self, text: str, lang: str) -> Sequence[Token]: ...


def default_tokenizer(text: str, lang: str) -> tuple[Token, ...]:
    import quebra_frases

    return tuple(Token(start, end, word) for start, end, word in quebra_frases.span_indexed_word_tokenize(text))


def is_mark(char: str) -> bool:
    return unicodedata.category(char).startswith("M")


def is_letter(char: str) -> bool:
    return unicodedata.category(char).startswith("L")


def is_digit(char: str) -> bool:
    return unicodedata.category(char) == "Nd"


def is_punctuation(char: str) -> bool:
    return unicodedata.category(char).startswith("P")


def next_visible(text: str, index: int) -> str:
    """The first character at or after `index` that is not whitespace, or "" at the end of the text."""
    while index < len(text) and text[index].isspace():
        index += 1
    return text[index] if index < len(text) else ""


def is_word_char(char: str) -> bool:
    """A letter, a digit or a combining mark: the characters a word is made of."""
    return is_letter(char) or is_digit(char) or is_mark(char)


def is_bounded(text: str, start: int, end: int) -> bool:
    """Whether the characters on either side of text[start:end] are not word characters."""
    return (start == 0 or not is_word_char(text[start - 1])) and (end == len(text) or not is_word_char(text[end]))


def check_tokens(tokens: Sequence[Token], text: str) -> tuple[Token, ...]:
    """The tokens, in order, after the checks of section 2.1; a tokenizer that breaks one raises."""
    checked = tuple(tokens)
    previous_end = 0
    for token in checked:
        if not isinstance(token, Token):
            raise TokenizerError(f"a tokenizer must return Token values, not {type(token).__name__}")
        if not (isinstance(token.start, int) and isinstance(token.end, int) and 0 <= token.start < token.end <= len(text)):
            raise TokenizerError(f"token {token!r} is outside the text or empty")
        if text[token.start:token.end] != token.text:
            raise TokenizerError(f"token {token!r} does not match the text {text[token.start:token.end]!r}")
        if token.start < previous_end:
            raise TokenizerError(f"token {token!r} is out of order or overlaps the token before it")
        previous_end = token.end
    return checked


_WORD_SEPARATORS = frozenset("\u200b")
"""Format characters that separate words, such as the zero-width space between Thai or Khmer words."""


def join_split_words(tokens: Sequence[Token], text: str, number_marks: frozenset[str]) -> tuple[Token, ...]:
    """Rejoin words that a tokenizer split at a combining mark, a format character or a declared number mark."""
    joined: list[Token] = []
    for token in tokens:
        if joined:
            last = joined[-1]
            gap = text[last.end:token.start]
            marks_only = gap != "" and all(is_mark(c) or (unicodedata.category(c) == "Cf" and c not in _WORD_SEPARATORS)
                                           for c in gap)
            number_join = (len(gap) == 1 and gap in number_marks
                           and is_digit(text[last.end - 1]) and is_digit(text[token.start]))
            if marks_only or number_join:
                joined[-1] = Token(last.start, token.end, text[last.start:token.end], token.clause_end)
                continue
        joined.append(token)
    extended = []
    for token in joined:
        end = token.end
        while end < len(text) and is_mark(text[end]):
            end += 1
        extended.append(token if end == token.end else Token(token.start, end, text[token.start:end], token.clause_end))
    return tuple(extended)


def protect_blocks(text: str) -> tuple[tuple[int, int], ...]:
    """The `[[...]]` blocks, which pass through byte for byte."""
    blocks = []
    position = 0
    while (start := text.find("[[", position)) != -1:
        end = text.find("]]", start + 2)
        if end == -1:
            break
        blocks.append((start, end + 2))
        position = end + 2
    return tuple(blocks)


def context_word(token_text: str) -> str | None:
    """The token text without the punctuation at its ends, or None for a token of punctuation or symbols only."""
    if not any(is_letter(c) or is_digit(c) for c in token_text):
        return None
    start, end = 0, len(token_text)
    while not is_word_char(token_text[start]):
        start += 1
    while not is_word_char(token_text[end - 1]):
        end -= 1
    return token_text[start:end]


@lru_cache(maxsize=256)
def fold_digits(text: str) -> str:
    """The text with every decimal digit (category Nd) as its ASCII digit; the length does not change."""
    return "".join(str(unicodedata.decimal(c)) if is_digit(c) else c for c in text)


_SCRIPT_OF_DIGIT_BLOCK = {
    "DIGIT": "Latn", "FULLWIDTH": "Latn", "ARABIC-INDIC": "Arab", "EXTENDED": "Arab", "DEVANAGARI": "Deva",
    "BENGALI": "Beng", "GURMUKHI": "Guru", "GUJARATI": "Gujr", "ORIYA": "Orya", "TAMIL": "Taml", "TELUGU": "Telu",
    "KANNADA": "Knda", "MALAYALAM": "Mlym", "THAI": "Thai", "LAO": "Laoo", "TIBETAN": "Tibt", "MYANMAR": "Mymr",
    "KHMER": "Khmr", "MONGOLIAN": "Mong", "NKO": "Nkoo",
}


def digit_script(digits: str) -> str | None:
    """The ISO 15924 code of the script of a run of digits, `Zyyy` for an unlisted block, None for mixed scripts."""
    scripts = {_SCRIPT_OF_DIGIT_BLOCK.get(unicodedata.name(c).split()[0], "Zyyy") for c in digits if is_digit(c)}
    return scripts.pop() if len(scripts) == 1 else None
