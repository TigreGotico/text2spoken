"""The recognizer and the verbalizer of the `LETTERS` form: runs of capital letters (design section 4.6).

A run is a token of capital letters that touches no other letter, digit or combining mark, with optional ASCII
digits before or after the letters. A run of one letter needs a digit. The `letter_runs` table of the language
decides first. Else a run of one or two letters reads letter by letter, and a longer run reads as a word when it
splits into syllables that the language allows: an optional onset of `letter_onsets`, a vowel of `letter_vowels`
and an optional coda of `letter_codas`. A consonant of `letter_free_consonants` may also stand where a reader adds a
vowel: as the coda of a syllable that another syllable follows, and after the last syllable of a run that holds a
consonant before a vowel. A run that is a well-formed Roman numeral, which `ROMAN` declines in its context, takes no
free consonant, so `XIV` reads as it reads without them, and `CIC`, which is no Roman numeral, reads ci-c.

A run with no digit that reads as a word stays as written, so its span keeps the text. In a text in capitals, a run
of `letter_words`, the short function words of the language, also reads as a word: `SAIA DA SALA` keeps `DA`. A run
sits in a text in capitals when only white space parts it from a chain of runs of capitals with no digit, and a run
of three letters or more in the chain reads as a word.

A run that reads letter by letter gives the name of each letter from `letter_names`. The digits of a run read as a
cardinal when the letters read as a word (`COVID19` reads "COVID nineteen"), or when they are one to three digits
with no leading zero (`B52`). Any other digits read one by one, by their words in `digit_words` (`MP3`, `B007`).
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from text2spoken.core.language import Request
from text2spoken.core.roman import value as roman_value
from text2spoken.core.spans import DECLINED, Features, Span, SpanContext
from text2spoken.core.tokens import Token, is_letter, is_word_char
from text2spoken.params import FrozenMap, Form

_DIGITS = "0123456789"


def splits_into_syllables(word: str, vowels: frozenset[str], onsets: frozenset[str], codas: frozenset[str],
                          free: frozenset[str] = frozenset()) -> bool:
    """Whether `word` is a sequence of syllables, each an optional onset, a vowel and an optional coda. A consonant of
    `free` may also close a syllable that another syllable follows. One consonant of `free` may follow the last
    syllable when the word holds a letter other than a vowel before a vowel, and when each letter that is neither a
    vowel nor in `free` stands in an onset of two or more letters, as h stands in the Portuguese onset ch. The search
    keeps the positions that a sequence of syllables can reach, so it takes linear time in the word."""
    def lengths(table: frozenset[str]) -> list[int]:
        return sorted({len(entry) for entry in table})

    onset_lengths, vowel_lengths, coda_lengths = [0, *lengths(onsets)], lengths(vowels), [0, *lengths(codas)]
    reached = [False] * (len(word) + 1)
    closed = [False] * (len(word) + 1)
    reached[0] = True
    for start in range(len(word)):
        if not reached[start]:
            continue
        for onset in onset_lengths:
            if onset and word[start:start + onset] not in onsets:
                continue
            nucleus = start + onset
            for vowel in vowel_lengths:
                after = nucleus + vowel
                if after > len(word) or word[nucleus:after] not in vowels:
                    continue
                for coda in coda_lengths:
                    end = after + coda
                    if end <= len(word) and (not coda or word[after:end] in codas):
                        reached[end] = closed[end] = True
                if word[after:after + 1] in free:
                    reached[after + 1] = True
    if closed[len(word)]:
        return True
    if not word or word[-1] not in free or not closed[len(word) - 1]:
        return False
    sounded = vowels | free
    silent = sorted((onset for onset in onsets if len(onset) > 1 and not set(onset) <= sounded), key=len, reverse=True)
    rest = re.sub("|".join(map(re.escape, silent)), "", word) if silent else word
    return all(char in sounded for char in rest) \
        and any(char not in vowels and following in vowels for char, following in zip(word, word[1:]))


def _parts(run: str) -> tuple[str, str, str]:
    """The digits before the letters, the letters and the digits after them."""
    head = len(run) - len(run.lstrip(_DIGITS))
    tail = len(run.rstrip(_DIGITS))
    return run[:head], run[head:tail], run[tail:]


def reading(run: str, data: FrozenMap, capitals: bool = False) -> Literal["word", "letters"] | None:
    """The reading of a run of capital letters with optional digits before or after them, or None when the text
    is no such run or when a letter of a run that reads letter by letter has no name. With `capitals`, the run sits
    in a text in capitals, where a run of `letter_words` reads as a word."""
    head, letters, tail = _parts(run)
    if len(run) < 2 or not letters or not all(is_letter(char) and char.isupper() for char in letters):
        return None
    if capitals and letters == run and letters in data.get("letter_words", ()):
        return "word"
    read = data.get("letter_runs", FrozenMap()).get(letters)
    if read is None:
        free = frozenset() if roman_value(letters) else frozenset(data.get("letter_free_consonants", ()))
        word = len(letters) > 2 and splits_into_syllables(
            letters.lower(), frozenset(data["letter_vowels"]), frozenset(data["letter_onsets"]),
            frozenset(data["letter_codas"]), free)
        read = "word" if word else "letters"
    if read == "word":
        return "word"
    names = data["letter_names"]
    return "letters" if all(char.lower() in names for char in letters) else None


def _digits(digits: str, word: bool, request: Request) -> list[str]:
    """The words of the digits of a run: a cardinal after letters that read as a word, or for one to three digits
    with no leading zero, else the word of each digit."""
    if not digits:
        return []
    speller = request.language.spellers.get(Form.CARDINAL)
    if speller is not None and not digits.startswith("0") and (word or len(digits) <= 3):
        try:
            return [speller.cardinal(digits, Features(), request)]
        except DECLINED:
            pass
    return [request.data["digit_words"][int(char)] for char in digits]


def spell(run: str, request: Request) -> str:
    """The run read aloud: the letters as written when they read as a word, else each letter by its name, and the
    digits by `_digits`, joined with single spaces."""
    data = request.data
    head, letters, tail = _parts(run)
    word = reading(letters, data) == "word"
    spoken = [letters] if word else [data["letter_names"][char.lower()] for char in letters]
    return " ".join([*_digits(head, word, request), *spoken, *_digits(tail, word, request)])


def respell(text: str, request: Request) -> str:
    """The text with each run that reads letter by letter, or that holds digits, read as the `LETTERS` form reads
    it."""
    data = request.data
    pieces = []
    position = 0
    for (start, end), capitals in _runs_in_context(text, data):
        written = text[start:end]
        read = reading(written, data, capitals)
        if read == "letters" or (read == "word" and written != _parts(written)[1]):
            pieces += [text[position:start], spell(written, request)]
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


def _runs_in_context(text: str, data: FrozenMap) -> list[tuple[tuple[int, int], bool]]:
    """Each maximal run of letters, digits and combining marks, and whether it sits in a text in capitals: only
    white space parts it from a chain of runs of capital letters with no digit that holds a run of three letters or
    more that reads as a word."""
    runs = list(_word_runs(text))
    words = [text[start:end] for start, end in runs]
    capitals = [False] * len(runs)
    chain: list[int] = []

    def close() -> None:
        if any(len(words[i]) > 2 and reading(words[i], data) == "word" for i in chain):
            for i in chain:
                capitals[i] = True
        chain.clear()

    for index, word in enumerate(words):
        upper = all(is_letter(char) and char.isupper() for char in word)
        if chain and (not upper or not text[runs[chain[-1]][1]:runs[index][0]].isspace()):
            close()
        if upper:
            chain.append(index)
    close()
    return list(zip(runs, capitals))


@dataclass(frozen=True)
class Letters:
    name: str = "letters"
    form: Form = Form.LETTERS

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A span for each run of design section 4.6. A run that reads as a word keeps its text."""
        data = request.data
        for (start, end), capitals in _runs_in_context(text, data):
            written = text[start:end]
            read = reading(written, data, capitals)
            if read is not None:
                yield Span(start, end, Form.LETTERS, FrozenMap({"letters": written, "reading": read}),
                           recognizer=self.name, keep=read == "word" and written == _parts(written)[1])


def speak_letters(span: Span, context: SpanContext) -> str:
    return spell(span.fields["letters"], context.request)


LETTERS = Letters()
