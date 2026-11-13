"""The recognizer and the verbalizer of the `LETTERS` form: runs of capital letters (design section 4.6).

A run is a token of capital letters that touches no other letter, digit or combining mark, with optional ASCII
digits before or after the letters. A run of one letter needs a digit. The `letter_runs` table of the language
decides first. Else a run of one or two letters reads letter by letter, and a longer run reads as a word when it
splits into syllables that the language allows: an optional onset of `letter_onsets`, a vowel of `letter_vowels`
and an optional coda of `letter_codas`. A run that reads as a word stays as written, so its span keeps the text.
A run that reads letter by letter gives the name of each letter from `letter_names` and the word of each digit from
`digit_words`.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from text2spoken.core.language import Request
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_letter, is_word_char
from text2spoken.params import FrozenMap, Form

_DIGITS = "0123456789"


def splits_into_syllables(word: str, vowels: frozenset[str], onsets: frozenset[str], codas: frozenset[str]) -> bool:
    """Whether `word` is a sequence of syllables, each an optional onset, a vowel and an optional coda. The search
    keeps the positions that a sequence of syllables can reach, so it takes linear time in the word."""
    def lengths(table: frozenset[str]) -> list[int]:
        return sorted({len(entry) for entry in table})

    onset_lengths, vowel_lengths, coda_lengths = [0, *lengths(onsets)], lengths(vowels), [0, *lengths(codas)]
    reached = [False] * (len(word) + 1)
    reached[0] = True
    for start in range(len(word)):
        if not reached[start]:
            continue
        for onset in onset_lengths:
            if onset and word[start:start + onset] not in onsets:
                continue
            nucleus = start + onset
            for vowel in vowel_lengths:
                if nucleus + vowel > len(word) or word[nucleus:nucleus + vowel] not in vowels:
                    continue
                for coda in coda_lengths:
                    end = nucleus + vowel + coda
                    if end <= len(word) and (not coda or word[nucleus + vowel:end] in codas):
                        reached[end] = True
    return reached[len(word)]


def reading(run: str, data: FrozenMap) -> Literal["word", "letters"] | None:
    """The reading of a run of capital letters with optional digits before or after them, or None when the text
    is no such run or when a letter of a run that reads letter by letter has no name."""
    head = len(run) - len(run.lstrip(_DIGITS))
    tail = len(run.rstrip(_DIGITS))
    letters = run[head:tail]
    if len(run) < 2 or not letters or not all(is_letter(char) and char.isupper() for char in letters):
        return None
    read = data.get("letter_runs", FrozenMap()).get(letters)
    if read is None:
        word = len(letters) > 2 and splits_into_syllables(
            letters.lower(), frozenset(data["letter_vowels"]), frozenset(data["letter_onsets"]),
            frozenset(data["letter_codas"]))
        read = "word" if word else "letters"
    if read == "word":
        return None if letters != run else "word"
    names = data["letter_names"]
    return "letters" if all(char.lower() in names for char in letters) else None


def spell(run: str, data: FrozenMap) -> str:
    """Each letter of the run by its name and each digit by its word, joined with single spaces."""
    names, digits = data["letter_names"], data["digit_words"]
    return " ".join(digits[int(char)] if char.isdigit() else names[char.lower()] for char in run)


def respell(text: str, data: FrozenMap) -> str:
    """The text with each run that reads letter by letter spelled, as the `LETTERS` form reads it."""
    pieces = []
    position = 0
    for start, end in _word_runs(text):
        if reading(text[start:end], data) == "letters":
            pieces += [text[position:start], spell(text[start:end], data)]
            position = end
    return "".join(pieces) + text[position:]


def _word_runs(text: str) -> Iterator[tuple[int, int]]:
    """The start and the end of each maximal run of letters, digits and combining marks."""
    start = None
    for index, char in enumerate(text):
        if is_word_char(char):
            if start is None:
                start = index
        elif start is not None:
            yield start, index
            start = None
    if start is not None:
        yield start, len(text)


@dataclass(frozen=True)
class Letters:
    name: str = "letters"
    form: Form = Form.LETTERS

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A span for each run of design section 4.6. A run that reads as a word keeps its text."""
        data = request.data
        for start, end in _word_runs(text):
            written = text[start:end]
            read = reading(written, data)
            if read is not None:
                yield Span(start, end, Form.LETTERS, FrozenMap({"letters": written, "reading": read}),
                           recognizer=self.name, keep=read == "word")


def speak_letters(span: Span, context: SpanContext) -> str:
    return spell(span.fields["letters"], context.request.data)


LETTERS = Letters()
