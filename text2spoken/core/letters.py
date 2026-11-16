"""The recognizer and the verbalizer of the `LETTERS` form: runs of capital letters (design section 4.6).

A run is a token of capital letters that touches no other letter, digit or combining mark, with optional ASCII
digits before or after the letters. A run of one letter needs a digit. The `letter_runs` table of the language
decides first. Else a run of one or two letters reads letter by letter, and a longer run reads as a word when it
splits into syllables that the language allows: an optional onset of `letter_onsets`, a vowel of `letter_vowels`
and an optional coda of `letter_codas`. A consonant of `letter_free_consonants` may also stand where a reader adds a
vowel: as the coda of a syllable that another syllable follows, and after the last syllable of a run that holds a
consonant before a vowel. A run that is a well-formed Roman numeral, which `ROMAN` declines in its context, takes no
free consonant, so `XIV` reads as it reads without them, and `CIC`, which is no Roman numeral, reads ci-c.

A run with no digit that reads as a word stays as written, so its span keeps the text. The word check of the
language can make a run read as a word: a run of three letters or more that it knows reads as a word anywhere, as
tugalex knows `AIDS` in Portuguese, unless `letter_runs` lists it. In a clause in capitals, a run of `letter_words`,
the short words of the language, also reads as a word, and so does a run of two letters that the word check knows:
`SAIA DA SALA` keeps `DA`, `IF IT IS` keeps each word, and `A RTP NO AR` keeps `AR`. A clause in capitals is a chain
of capitals, with no digit, that only white space parts, and that holds two runs or more. Every run counts, however
it reads, and so does a capital alone that `letter_words` holds, as `I` in `I DO`. When another form reads the parts
next to such a word, or they read letter by letter, the word is written in lower case, so a second pass keeps it a
word: `CAPÍTULO VI DE` reads "CAPÍTULO sexto de".

A run that reads letter by letter gives the name of each letter from `letter_names`. The digits of a run read as a
cardinal when the letters read as a word (`COVID19` reads "COVID nineteen"), or when they are one to three digits
with no leading zero (`B52`). Any other digits read one by one, by their words in `digit_words` (`MP3`, `B007`).
"""
from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from text2spoken.core.language import Request
from text2spoken.core.roman import value as roman_value
from text2spoken.core.spans import DECLINED, Features, Span, SpanContext
from text2spoken.core.tokens import Token, is_letter, is_word_char
from text2spoken.params import FrozenMap, Form

_DIGITS = "0123456789"
Clause = tuple[tuple[int, int, str], ...]
"""The parts of a clause in capitals: the start, the end and the kind of each run and each capital alone."""


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


def reading(run: str, data: FrozenMap, known: bool = False) -> Literal["word", "letters"] | None:
    """The reading of a run of capital letters with optional digits before or after them, or None when the text
    is no such run or when a letter of a run that reads letter by letter has no name. `letter_runs` decides first.
    Else, with `known`, the run is a word of the language in its context, and it reads as a word."""
    head, letters, tail = _parts(run)
    if len(run) < 2 or not letters or not all(is_letter(char) and char.isupper() for char in letters):
        return None
    read = data.get("letter_runs", FrozenMap()).get(letters)
    if read is None and known:
        return "word"
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
    for (start, end), known, _ in _runs_in_context(text, request):
        written = text[start:end]
        read = reading(written, data, known)
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


def _runs_in_context(text: str, request: Request) -> list[tuple[tuple[int, int], bool, Clause]]:
    """Each maximal run of letters, digits and combining marks, whether the words of the language make it read as a
    word, and the clause in capitals that its word reading needs, or an empty tuple.

    A run of three letters or more that the word check of the language knows reads as a word anywhere. A run of
    `letter_words`, or a run of two letters that the word check knows, reads as a word in a clause in capitals: a
    chain of capitals that only white space parts, with two runs or more. Every run of capitals counts, however it
    reads, and so does a capital alone that `letter_words` holds. Any other capital alone links the chain. Each part
    of the clause is its start, its end and its kind: `stays` for a part that stays as written in capitals, `spelled`
    for a run that reads letter by letter, and `link`."""
    data = request.data
    listed = frozenset(data.get("letter_words", ()))
    known_word = next((r.known_word for r in request.language.recognizers if isinstance(r, Letters)), None)
    runs = list(_word_runs(text))
    words = [text[start:end] for start, end in runs]
    capitals = [all(is_letter(char) and char.isupper() for char in word) for word in words]
    knows = [capitals[i] and len(word) > 1 and known_word is not None and known_word(word.lower(), request)
             for i, word in enumerate(words)]
    anywhere = [known and len(word) > 2 for known, word in zip(knows, words)]
    needs = [capitals[i] and len(word) > 1 and not anywhere[i] and (word in listed or knows[i])
             for i, word in enumerate(words)]
    clauses: list[Clause] = [()] * len(runs)
    chain: list[int] = []

    def kind(i: int) -> str:
        if len(words[i]) == 1:
            return "stays" if words[i] in listed else "link"
        return "spelled" if reading(words[i], data, anywhere[i] or needs[i]) == "letters" else "stays"

    def close() -> None:
        if sum(len(words[i]) > 1 or words[i] in listed for i in chain) > 1:
            parts = tuple((*runs[i], kind(i)) for i in chain)
            for i in chain:
                if needs[i]:
                    clauses[i] = parts
        chain.clear()

    for index in range(len(words)):
        if chain and (not capitals[index] or not text[runs[chain[-1]][1]:runs[index][0]].isspace()):
            close()
        if capitals[index]:
            chain.append(index)
    close()
    return [(run, anywhere[i] or bool(clauses[i]), clauses[i]) for i, run in enumerate(runs)]


@dataclass(frozen=True)
class Letters:
    """The recognizer of the form. `known_word` is the word check of the language: it takes a run in lower case and
    the request, and tells whether the run is a word of the language."""
    name: str = "letters"
    form: Form = Form.LETTERS
    known_word: Callable[[str, Request], bool] | None = None

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A span for each run of design section 4.6. A run that reads as a word keeps its text. A word of a clause in
        capitals also gives its clause, because `classify` writes it in lower case when no part next to it stays as
        written in capitals."""
        data = request.data
        for (start, end), known, clause in _runs_in_context(text, request):
            written = text[start:end]
            read = reading(written, data, known)
            if read is not None:
                yield Span(start, end, Form.LETTERS, FrozenMap({"letters": written, "reading": read, "clause": clause}),
                           recognizer=self.name, keep=read == "word" and written == _parts(written)[1])


def speak_letters(span: Span, context: SpanContext) -> str:
    if span.fields["reading"] == "lower":
        return span.fields["letters"].lower()
    return spell(span.fields["letters"], context.request)


LETTERS = Letters()
