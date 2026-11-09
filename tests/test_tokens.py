"""The tokenizer hook, the token checks, the word joins and the context words (design section 2.1)."""
import csv
import unicodedata
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fixtures import quebra_frases_pr25
from text2spoken import Token, TokenizerError, analyze, normalize
from text2spoken.core.spans import Clauses, clause_breaks, clause_window, context_words
from text2spoken.core.tokens import (check_tokens, default_tokenizer, digit_script, fold_digits, join_split_words,
                                     protect_blocks)


def pr25_tokenizer(text, lang):
    return tuple(Token(a, b, t) for a, b, t in quebra_frases_pr25.span_indexed_word_tokenize(text))


def words(text, tokenizer, marks=frozenset()):
    tokens = join_split_words(check_tokens(tokenizer(text, "und"), text), text, marks)
    return [w.text for w in context_words(tokens)]


# Each row: the text and its context words, written by hand from the rule of section 2.1.
ROWS = [
    ("मेरे पास ५ किताबें", ["मेरे", "पास", "५", "किताबें"]),
    ("اشتريتُ ٣ سَيّاراتٍ", ["اشتريتُ", "٣", "سَيّاراتٍ"]),
    (unicodedata.normalize("NFD", "3 cafés às 14:30"), ["3", unicodedata.normalize("NFD", "cafés"),
                                                        unicodedata.normalize("NFD", "às"), "14:30"]),
    ("O Dr. Silva pagou 2,50 € às 14:30.", ["O", "Dr", "Silva", "pagou", "2,50", "às", "14:30"]),
    ("background-color: #fff;", ["background-color", "fff"]),
    ("25°C e 5 km/h", ["25", "C", "e", "5", "km", "h"]),
    ("+351 912 345 678", ["351", "912", "345", "678"]),
    ("1995/03/07an", ["1995/03/07", "an"]),
    ("Er kam am 3. Mai.", ["Er", "kam", "am", "3", "Mai"]),
    ("۵‌تا کتاب", ["۵‌تا", "کتاب"]),
]


@pytest.mark.parametrize("text,expected", ROWS)
def test_context_words_are_equal_on_both_tokenizers(text, expected):
    assert words(text, default_tokenizer) == expected
    assert words(text, pr25_tokenizer) == expected


@pytest.mark.parametrize("text,tag", [("Call +44 20 7946 0018 today.", "en-GB"), ("The colour is #FF0000.", "en"),
                                      ("It is 25°C.", "en"), ("Pay $5.50, ok?", "en"), ("मेरे पास ५ किताबें", "hi"),
                                      ("اشتريتُ ٣ سَيّاراتٍ", "ar"), ("我有3本书", "zh"), ("3本あります", "ja")])
def test_spans_are_equal_on_both_tokenizers(text, tag):
    assert analyze(text, tag).spans == analyze(text, tag, tokenizer=pr25_tokenizer).spans


def test_the_arabic_decimal_mark_join_needs_a_declared_mark():
    text = "١٢٫٥"
    split = check_tokens(default_tokenizer(text, "ar"), text)
    assert len(join_split_words(split, text, frozenset({"٫"}))) == 1
    assert len(join_split_words(split, text, frozenset())) == len(split)


def test_a_trailing_combining_mark_stays_on_its_word():
    text = "سَيّاراتٍ"
    cut = (Token(0, len(text) - 1, text[:-1]),)
    assert join_split_words(cut, text, frozenset())[0].text == text


@pytest.mark.parametrize("tokens", [
    (Token(0, 2, "xy"),),                                  # text mismatch
    (Token(3, 5, "de"), Token(0, 2, "ab")),                # out of order
    (Token(0, 3, "abc"), Token(2, 4, "cd")),               # overlap
    (Token(0, 0, ""),),                                    # empty
    ((0, 3, "abc"),),                                      # not a Token
])
def test_a_tokenizer_that_breaks_a_rule_raises(tokens):
    with pytest.raises(TokenizerError):
        normalize("abc de", "en", tokenizer=lambda text, lang: tokens)


def test_a_downstream_tokenizer_feeds_the_context_words():
    seen = []

    def tokenizer(text, lang):
        seen.append(lang)
        return (Token(0, 2, "at"), Token(3, 8, "14:30"))

    assert normalize("at 14:30", "en-US", tokenizer=tokenizer) == "at two thirty PM"
    assert seen == ["en-US"]
    assert normalize("at 14:30", "en-US", tokenizer=lambda text, lang: ()) == "at 14:30"


def test_a_clause_end_token_stops_the_window():
    text = "at 14:30"
    tokens = (Token(0, 2, "at", clause_end=True), Token(3, 8, "14:30"))
    assert normalize(text, "en-US", tokenizer=lambda t, l: tokens) == "at 14:30"


@pytest.mark.parametrize("text,before", [("a b; at 14:30", ("at",)), ("Go. At 14:30", ("At",)),
                                         ("one two three four 14:30", ("two", "three", "four")),
                                         ("x! y 14:30", ("y",)), ("e.g. b 14:30", ("e.g", "b"))])
def test_the_window_stops_at_a_clause_mark_and_holds_three_words(text, before):
    found = context_words(default_tokenizer(text, "en"))
    start = text.index("14:30")
    assert clause_window(text, found, start, start + 5, -1) == before


CLAUSE_TEXTS = [
    "Use #fff now colour", "the #fff colour; #000 here", "Go. At #abc! then #123 is? x y. Z #eee colour",
    "background-color: #fff; color: #000", "e.g. b #fff c. D e", "a-b-c #FFF x-colour", "#fff", "", "; ; #fff ;",
]


@pytest.mark.parametrize("every", [0, 2, 3])
def test_the_clauses_give_the_clause_window_with_no_limit(every):
    """`Clauses.around` against `clause_window` with no limit, at each start and three span lengths, in the texts
    above and the rows of en.tsv, where every n-th token ends its clause."""
    with open(Path(__file__).parent / "data" / "en.tsv", encoding="utf-8") as rows:
        texts = CLAUSE_TEXTS + [row["text"] for row in csv.DictReader(rows, delimiter="\t")]
    compared = 0
    for text in texts:
        tokens = default_tokenizer(text, "en")
        if every:
            tokens = tuple(replace(t, clause_end=t.clause_end or i % every == 0) for i, t in enumerate(tokens))
        found = context_words(tokens)
        breaks = clause_breaks(text)
        clauses = Clauses(found, breaks)
        for start in range(len(text) + 1):
            for end in {start, min(start + 1, len(text)), min(start + 4, len(text))}:
                back, ahead = clauses.around(start, end)
                assert tuple(found[i].text for i in back) == clause_window(text, found, start, end, -1,
                                                                           limit=len(found), breaks=breaks)
                assert tuple(found[i].text for i in ahead) == clause_window(text, found, start, end, 1,
                                                                            limit=len(found), breaks=breaks)
                compared += 1
    assert compared > 10000


def test_a_clause_window_from_clauses_takes_the_same_steps_for_a_short_and_a_long_clause():
    """`Clauses.around` looks the clause up, and does not walk it: the lines that run inside it, counted by a trace,
    stay the same when the clause grows from 100 to 4000 words, apart from the two binary searches."""
    import sys

    from text2spoken.core.spans import Clauses

    def lines_run(size):
        text = " ".join(["word"] * size) + " #fff"
        found = context_words(default_tokenizer(text, "en"))
        clauses = Clauses(found, clause_breaks(text))
        count = 0

        def trace(frame, event, arg):
            nonlocal count
            if frame.f_code.co_filename.endswith("spans.py"):
                count += event == "line"
                return trace
            return None

        sys.settrace(trace)
        try:
            back, ahead = clauses.around(len(text) - 4, len(text))
        finally:
            sys.settrace(None)
        assert len(back) == size and len(ahead) == 0
        return count

    # Each of the two binary searches runs its key once per halving step.
    assert lines_run(4000) - lines_run(100) <= 2 * ((4000).bit_length() - (100).bit_length() + 1)


def test_the_clause_breaks_are_the_marks_and_the_periods_before_a_capital():
    text = "Go. At e.g. b; x! y? Z.  Q"
    assert clause_breaks(text) == (2, 13, 16, 19, 22)


def test_inline_blocks():
    assert protect_blocks("a [[x]] b [[y") == ((2, 7),)
    assert normalize("I have [[3]] and 3.", "en") == "I have [[3]] and three."


def test_digit_folding_keeps_the_length_and_names_the_script():
    assert fold_digits("٤٥ and ۵ and ५") == "45 and 5 and 5"
    assert digit_script("٤٥") == "Arab" and digit_script("45") == "Latn" and digit_script("५") == "Deva"
    assert digit_script("4٥") is None
