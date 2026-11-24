"""Rules of design sections 2.1, 4.2, 6 and 11 with values worked out by hand, one test for each rule."""
import logging
import random
import re
import sys
import time
import warnings
from dataclasses import replace
from types import SimpleNamespace

import pytest

from tests.known_limits import known_limit
from text2spoken import (Animacy, Features, FrozenMap, InvalidLexiconError, NormalizationParams,
                         ParameterNotHonouredWarning, SayAs, Token, TokenizerError, UndefinedGrammaticalGender,
                         UnreadFormError, analyze, effective_params, normalize, render, supports)
from text2spoken.core import language as loader
from text2spoken.core import recognizers
from text2spoken.core.language import cldr_locale
from text2spoken.core.numbers import find_numbers
from text2spoken.core.recognizers import _DATE, _FRACTION, SHARED, SPACE_GROUPS, digit_run_matches
from text2spoken.core.spans import Span, _group_spaces, _inside, _joined, _sides, check_features, splits_token
from text2spoken.core.tokens import check_tokens, context_word, fold_digits, join_split_words, protect_blocks
from text2spoken.lang import nl
from text2spoken.lang.en import LANGUAGE as EN
from text2spoken.params import Form, freeze, thaw

BRACKET_LOSS = pytest.mark.xfail(strict=True, reason="a number in brackets before a run keeps the run as written")
GLUED_LOSS = pytest.mark.xfail(strict=True,
                               reason="under say-as telephone, the digits after a glued group read as a quantity")
WORD_BACK_LOSS = pytest.mark.xfail(strict=True, reason="a phone word more than one word back names no run")


def words_of(text: str, clause_end_after: frozenset[str] = frozenset()) -> list[Token]:
    """A tokenizer that splits at spaces and ends the clause after each word in `clause_end_after`."""
    tokens, position = [], 0
    for word in text.split(" "):
        tokens.append(Token(position, position + len(word), word, clause_end=word in clause_end_after))
        position += len(word) + 1
    return tokens


def test_a_lead_frees_only_the_start_edge():
    text = "#5abc"
    lead = Span(0, 3, Form.CARDINAL, FrozenMap({"lead": "#"}))
    assert splits_token(lead, (Token(0, 5, text),), text)


def test_a_lead_that_is_no_punctuation_may_start_a_span_inside_a_token():
    text = "sub~23"
    tokens = (Token(0, 6, text),)
    assert not splits_token(Span(3, 6, Form.CARDINAL, FrozenMap({"lead": "~"})), tokens, text)
    assert splits_token(Span(3, 6, Form.CARDINAL, FrozenMap({"lead": ""})), tokens, text)


def test_the_longest_lead_wins(monkeypatch):
    leads = FrozenMap({"#": "", "N#": "number"})
    spec = replace(EN, data=FrozenMap({**EN.data, "leads": leads}))
    monkeypatch.setattr(loader, "_registry", lambda: {"en": spec})
    assert normalize("Room N#5 is shut.", "en") == "Room number five is shut."


@pytest.mark.parametrize("seed", range(20))
def test_a_span_is_inside_the_blocks_that_it_overlaps(seed):
    rng = random.Random(seed)
    for _ in range(200):
        text = "".join(rng.choice(["[[", "]]", "a", " ", "5"]) for _ in range(rng.randint(1, 30)))
        blocks = protect_blocks(text)
        for start in range(len(text)):
            for end in range(start + 1, len(text) + 1):
                span = Span(start, end, Form.CARDINAL, FrozenMap())
                expected = any(start < block_end and block_start < end for block_start, block_end in blocks)
                assert _inside(span, blocks) == expected, (text, start, end)


def test_the_block_check_takes_linear_time():
    def seconds(count: int) -> float:
        blocks = tuple((8 * i, 8 * i + 5) for i in range(count))
        spans = [Span(8 * i + 6, 8 * i + 7, Form.CARDINAL, FrozenMap()) for i in range(count)]
        start = time.perf_counter()
        for span in spans:
            _inside(span, blocks)
        return time.perf_counter() - start

    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_the_unread_check_takes_linear_time_in_the_blocks():
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"ACME": "acme"})}))

    def seconds(count: int) -> float:
        analysis = analyze("[[x]] ACME " * count, "en", params)
        start = time.perf_counter()
        render(analysis)
        return time.perf_counter() - start

    render(analyze("[[x]] ACME", "en", params))
    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_unread_digits_between_blocks_are_reported_once_each():
    with pytest.raises(UnreadFormError) as raised:
        normalize("05 [[01]] 06 [[02]][[03]] 07 [[04]]", "en", NormalizationParams(strict=True))
    assert raised.value.unread == ("05", "06", "07")


@pytest.mark.parametrize("text, expected", [
    ("[[5]] apples", "[[5]] apples"),
    ("[[5]][[6]] apples", "[[5]][[6]] apples"),
    ("[[5]] 6 apples", "[[5]] six apples"),
    ("5[[6]] apples", "five[[6]] apples"),
    ("Pay $5[[6]] now.", "Pay five dollars[[6]] now."),
])
def test_a_block_at_the_start_of_a_passthrough_segment_is_not_unread(text, expected):
    assert normalize(text, "en-GB", NormalizationParams(strict=True)) == expected


def test_two_digit_tokens_join_over_one_declared_mark_only():
    text = "1, 5"
    tokens = (Token(0, 1, "1"), Token(3, 4, "5"))
    assert join_split_words(tokens, text, frozenset({", "})) == tokens
    assert join_split_words((Token(0, 1, "1"), Token(2, 3, "5")), "1,5", frozenset({","})) == (Token(0, 3, "1,5"),)


def test_a_span_that_overlaps_a_block_edge_is_inside_it():
    assert _inside(Span(2, 6, Form.CARDINAL, FrozenMap()), [(4, 10)])
    assert _inside(Span(6, 12, Form.CARDINAL, FrozenMap()), [(4, 10)])
    assert not _inside(Span(10, 12, Form.CARDINAL, FrozenMap()), [(4, 10)])


@pytest.mark.parametrize("features", [Features(animacy=Animacy.PERSONAL), Features(noun_class="7"),
                                      Features(numeral_system="counting")])
def test_a_hint_value_that_the_language_lacks_raises_in_every_dimension(gendered, features):
    language = replace(gendered.LANGUAGE, animacies=frozenset({Animacy.ANIMATE}), noun_classes=frozenset({"1"}),
                       numeral_systems=frozenset({"standard"}))
    with pytest.raises(UndefinedGrammaticalGender):
        check_features(features, language, "qaa")


def test_clause_end_on_a_word_after_the_span_stops_the_after_window():
    text = "Use #fff now colour"
    assert normalize(text, "en", tokenizer=lambda t, lang: words_of(t)) == "Use white now colour"
    assert normalize(text, "en", tokenizer=lambda t, lang: words_of(t, frozenset({"now"}))) == text


def test_clause_end_on_the_word_that_holds_the_span_stops_the_after_window():
    text = "the #fff colour"
    assert normalize(text, "en", tokenizer=lambda t, lang: words_of(t)) == "the white colour"
    assert normalize(text, "en", tokenizer=lambda t, lang: words_of(t, frozenset({"#fff"}))) == text


def test_the_colour_search_grows_linearly_with_the_hex_codes(monkeypatch):
    """Each hex code that holds only letters or only digits looks for a colour word in its whole clause. The clause
    steps must grow with the text, not with its square: twice the codes take about twice the steps."""
    from text2spoken.core import spans

    steps, clause_break = 0, spans._clause_break

    def counted(*args):
        nonlocal steps
        steps += 1
        return clause_break(*args)

    monkeypatch.setattr(spans, "_clause_break", counted)

    def search(count):
        nonlocal steps
        steps = 0
        text = " ".join(["#abc and"] * count) + " in this colour."
        assert sum(span.form is Form.COLOR for span in analyze(text, "en").spans) == count
        return steps

    assert search(2000) <= 2.2 * search(1000)


def test_the_colour_search_reads_each_word_once(monkeypatch):
    """Each context word is tested as a colour word once per call, however many hex codes the text holds."""
    from text2spoken.core import color
    from text2spoken.core.spans import context_words

    tested, is_color_word = 0, color._is_color_word

    def counted(*args):
        nonlocal tested
        tested += 1
        return is_color_word(*args)

    monkeypatch.setattr(color, "_is_color_word", counted)
    text = " ".join(["#abc and"] * 500) + " in this colour."
    analysis = analyze(text, "en")
    assert sum(span.form is Form.COLOR for span in analysis.spans) == 500
    assert tested == len(context_words(analysis.tokens))


def test_tokens_that_overlap_by_one_character_raise():
    with pytest.raises(TokenizerError):
        check_tokens((Token(0, 3, "abc"), Token(2, 5, "cde")), "abcde")


def test_a_joined_token_keeps_the_clause_end_of_its_last_part():
    text = "cafe\u0301s"
    joined = join_split_words((Token(0, 4, "cafe"), Token(5, 6, "s", clause_end=True)), text, frozenset())
    assert joined == (Token(0, 6, text, clause_end=True),)


def test_a_zero_width_space_separates_words():
    text = "สวัสดี​ครับ"
    tokens = (Token(0, 6, "สวัสดี"), Token(7, 11, "ครับ"))
    assert join_split_words(tokens, text, frozenset()) == tokens
    joiner = "ab‍cd"
    assert join_split_words((Token(0, 2, "ab"), Token(3, 5, "cd")), joiner, frozenset()) == (Token(0, 5, joiner),)


def test_a_context_word_drops_punctuation_at_both_ends():
    assert context_word("(phone):") == "phone"


def test_a_phone_region_set_with_one_region_lacking_a_plan_warns():
    with pytest.warns(ParameterNotHonouredWarning):
        effective_params("en", NormalizationParams(phone_regions=frozenset({"GB", "ZZ"})))


def test_supports_lists_every_form_that_en_reads():
    assert set(Form) - supports("en").forms == {Form.IDENTIFIER}


def test_cldr_locale_tries_the_script_before_the_region(gendered):
    assert cldr_locale("zh-Hant-TW", {"zh_Hant", "zh_TW", "zh"}, gendered.LANGUAGE) == "zh_Hant"


def test_a_lexicon_entry_that_keeps_its_key_is_allowed_and_protects_the_text():
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"MIX": "MIX", "X5": "X5"})}))
    assert normalize("MIX 5 and X5 now", "en", params) == "MIX five and X5 now"
    assert normalize("MIX 5 and X5 now", "en") == "MIX five and X5 now"
    protected = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"#fff": "#fff"})}))
    assert normalize("the #fff colour", "en", protected) == "the #fff colour"


# en.py marks a date that "the" stands right before, and the span keeps the bounds it has with no article.


def test_a_lexicon_entry_for_the_article_before_an_english_date_leaves_the_date_read():
    params = NormalizationParams(lexicon=FrozenMap({"en-GB": FrozenMap({"the": "thee"})}))
    assert normalize("Due the 12/03/2024.", "en-GB", params) == "Due thee twelfth of March twenty twenty-four."
    assert normalize("On the 14 March 2024.", "en-GB", params) == "On thee fourteenth of March twenty twenty-four."


def test_a_hint_at_an_english_date_after_the_article_finds_the_date():
    text = "Book it for the 3rd of May."
    strict = analyze(text, "en-GB", NormalizationParams(strict=True))
    assert render(strict, {text.index("3rd"): Features()}) == "Book it for the third of May."
    assert [text[span.start:span.end] for span in strict.spans] == ["3rd of May"]


def test_a_lexicon_value_that_a_recognizer_reads_with_its_tokens_raises():
    with pytest.raises(InvalidLexiconError):
        normalize("ETA", "en", NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"ETA": "at 14:30"})})))


def test_a_lexicon_key_inside_a_word_is_not_read():
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"MIX": "mix"})}))
    assert normalize("MIXER and MIX", "en", params, tokenizer=lambda t, lang: ()) == "MIXER and mix"


def test_a_phone_number_has_at_most_fifteen_digits():
    assert normalize("Call 012345678901234 now.", "en-GB") == \
        "Call zero one two three four five six seven eight nine zero one two three four now."
    assert normalize("Call 0123456789012345 now.", "en-GB") == "Call 0123456789012345 now."
    assert normalize("Call 1234567890123456 now.", "en-GB") == "Call 1234567890123456 now."
    assert not any(span.form is Form.TELEPHONE for span in analyze("See +44 1234 5678 9012 3456 78.", "en-GB").spans)
    assert not any(span.form is Form.TELEPHONE for span in analyze("Call 25 or 1234567890123456.", "en-GB").spans)


def test_a_unit_after_a_currency_symbol_is_no_measure():
    assert normalize("It is €10kg.", "en") == "It is €10kg."


def test_a_named_date_after_a_symbol_reads_the_same_on_a_second_pass():
    once = normalize("Up %2 12/03/2024 now", "en-US")
    assert normalize(once, "en-US") == once


def test_a_negative_number_stays_as_written_in_a_language_with_no_sign_words(caplog):
    # CLDR zu.xml: the rule set spellout-cardinal has no -x rule.
    assert normalize("It is -5 now.", "zu") == "It is -5 now."
    assert "unread written form '-5'" in caplog.text and "sign_words" not in caplog.text


ATOMS = (list("abcxyzABCXYZéñ") + list("0123456789") + list("٠١٢٣٤٥٦٧٨٩") + list("０１２")
         + list("#-+$£€¥%°/:.,;!?()'’×") + ["́", "̈", "‍", "‌", "​", " ", "\r\n", "\t",
                                              " "]
         + ["Dr.", "vs.", "etc.", "No.", "March", "May", "[[", "]]", "am", "pm", "at", "in", "kg", "km/h", "°C",
            "call", "colour", "#fff", "#FF0000", "1/2", "24/7", "14:30", "12/03/2024", "+351", "00", "x", "−", "sub",
            "3rd", "11th", "1984", "2005", "million", "m", "k", "-", "1,000", "@", "www.", ".com", "http://", "-",
            "_", "ftp://", ".5", ".٣", "@x.", "a@b.com."])


@pytest.mark.parametrize("seed", range(4))
def test_normalize_is_idempotent_and_never_crashes_on_random_text(seed):
    """Section 11: a second pass changes nothing, except in the known limits of the address claim that the
    README lists. Random text built from the atoms of each form."""
    rng = random.Random(seed)
    for _ in range(500):
        lang = rng.choice(["en", "en-US", "fr", "xx"])
        text = "".join(rng.choice(ATOMS) for _ in range(rng.randint(1, 30)))
        once = normalize(text, lang)
        assert normalize(once, lang) == once or known_limit(text, lang), (text, once)


GROUPED = ["1 000", "1\u202f000", "2\u00a0500 000", "–", "1 000-", "1 000–", "1 000/", "1 000+", "1 000 = ",
           "1 000 × ", "1\u202f000-", "-2 000", "–2 000", "/2 000", "+2 000", "= 2 000", "× 2 000"]
"""Numbers grouped with a space next to a range mark, a fraction slash or an operator. A language whose group marks
hold a space reads `1 000` as one number, and a recognizer that read `[0-9]+` on its own split it."""


@pytest.mark.parametrize("seed", range(4))
def test_a_number_grouped_with_a_space_reads_the_same_on_a_second_pass(seed):
    """Section 11 for French, which groups digits with a space, on random text with the atoms of `GROUPED`."""
    rng = random.Random(seed)
    atoms = ATOMS + GROUPED
    for _ in range(500):
        lang = rng.choice(["fr", "fr-FR", "fr-CA", "fr-CH", "fr-BE"])
        text = "".join(rng.choice(atoms) for _ in range(rng.randint(1, 30)))
        once = normalize(text, lang)
        assert normalize(once, lang) == once or known_limit(text, lang), (text, once)


@pytest.mark.parametrize(("text", "expected"), [
    ("Pay 2,51 €m.www.x.in", "symbol at claim start"),
    ("See x.com£€ 03° and pay 2,51 €m.www.x.in", None),
])
def test_the_symbol_at_claim_start_limit_holds_only_its_own_amounts(text, expected):
    """Both texts change on a second pass. In the second, the amount `€ 03` also reads on the second pass, and its
    sign stands after the reading of the address `x.com`, not at the start of a claim. So the limit does not name
    that text."""
    once = normalize(text, "en-GB")
    assert normalize(once, "en-GB") != once
    assert known_limit(text, "en-GB") == expected


def test_run_time_grows_linearly_with_the_input():
    unit = "Dr. Smith paid $5 at 14:30 on 12/03/2024. "
    normalize(unit, "en")

    def seconds(copies: int) -> float:
        start = time.perf_counter()
        normalize(unit * copies, "en")
        return time.perf_counter() - start

    small, large = min(seconds(100) for _ in range(3)), min(seconds(800) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_analyze_claims_a_year_and_a_money_scale():
    spans = analyze("In 1984 they raised $2 million.", "en-US").spans
    amount = {"integer": "2", "fraction": "", "sign": "", "prefix": "", "suffix": "", "script": "Latn"}
    assert [(s.form, s.fields) for s in spans] == [
        (Form.YEAR, {"digits": "1984", "suffix": ""}),
        (Form.MONEY, {"amount": amount, "currency": "USD", "written_symbol": "$", "scale": "million", "prefix": "",
                      "suffix": ""}),
    ]


def test_a_signed_number_after_a_dimension_mark_is_no_second_dimension():
    analysis = analyze("A 10 x -5 cm hole.", "en-GB")
    spans = SHARED["measure"].find(analysis.text, analysis.tokens, analysis.request)
    assert [s for s in spans if isinstance(s.fields["amount"], tuple)] == []


def test_digits_from_two_digit_sets_read_the_same_on_a_second_pass():
    once = normalize("[[０3 12/03/2024", "en-US")
    assert once == "[[０3 December third twenty twenty-four"
    assert normalize(once, "en-US") == once


def test_measures_that_slashes_chain_take_linear_time():
    def seconds(count: int) -> float:
        text = "x " + "/".join(f"{i}°C" for i in range(count))
        start = time.perf_counter()
        normalize(text, "en")
        return time.perf_counter() - start

    normalize("x 1°C/2°C", "en")
    small, large = min(seconds(250) for _ in range(3)), min(seconds(2000) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_short_groups_after_a_letter_take_linear_time():
    def seconds(count: int) -> float:
        text = "x" + "1 " * count + "1"
        start = time.perf_counter()
        normalize(text, "en")
        return time.perf_counter() - start

    normalize("x1 1", "en")
    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_a_long_digit_run_takes_linear_time():
    def seconds(count: int) -> float:
        start = time.perf_counter()
        normalize("1" * count, "en")
        return time.perf_counter() - start

    normalize("1/2 1-2 1+2 12/03/2024", "en")
    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


@pytest.mark.parametrize("name", ["fraction", "range", "date_numeric", "expression"])
def test_a_long_digit_run_takes_linear_time_in_each_recognizer(name):
    recognizer = next(r for r in EN.recognizers if r.name == name)
    request = analyze("1", "en").request

    def seconds(count: int) -> float:
        start = time.perf_counter()
        list(recognizer.find("1" * count, (), request))
        return time.perf_counter() - start

    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


ADDRESS_SHAPES = {"www": lambda count: "1www." * (count // 5),
                  "brackets": lambda count: "see example.com/" + ")" * count,
                  "labels": lambda count: "a." * (count // 2) + "1",
                  "at": lambda count: "a@" * (count // 2),
                  "blocks": lambda count: "[[x]]a@b" * (count // 8)}


@pytest.mark.parametrize("shape", sorted(ADDRESS_SHAPES))
def test_a_long_address_shape_takes_linear_time_in_the_address_recognizer(shape):
    recognizer = next(r for r in EN.recognizers if r.name == "electronic")
    request = analyze("1", "en").request

    def seconds(count: int) -> float:
        text = ADDRESS_SHAPES[shape](count)
        start = time.perf_counter()
        list(recognizer.find(text, (), request))
        return time.perf_counter() - start

    small, large = min(seconds(1000) for _ in range(3)), min(seconds(8000) for _ in range(3))
    assert large < 20 * small, (small, large)


class CountedPattern:
    """A pattern that counts the starts at which it tries a match. `finditer` tries each start in turn, as the
    engine of `re` does."""
    starts = 0

    def __init__(self, pattern):
        self.compiled = pattern.compiled if isinstance(pattern, CountedPattern) else re.compile(pattern)

    def match(self, string, pos=0):
        CountedPattern.starts += 1
        return self.compiled.match(string, pos)

    def finditer(self, string):
        pos = 0
        while pos <= len(string):
            match = self.match(string, pos)
            if match:
                yield match
            pos = max(match.end(), pos + 1) if match else pos + 1


@pytest.mark.parametrize(("tag", "name"), [("pt-PT", "ordinal"), ("ru-RU", "hyphen_ordinal"),
                                           ("ru-RU", "other_decimal_mark"), ("ru-RU", "expression_guard"),
                                           ("eu", "law_number"), ("nl-NL", "kept_groups"), ("nl-NL", "money")])
def test_a_long_digit_run_is_tried_at_a_few_starts(monkeypatch, tag, name):
    """A try at a start inside a digit run can read to the end of the run. So the starts that a recognizer tries in
    one run must not grow with the run, or a long run takes quadratic time."""
    request = analyze("1", tag).request
    recognizer = next(r for r in request.language.recognizers if r.name == name)
    counted_re = SimpleNamespace(**{**vars(re), "compile": CountedPattern,
                                    "finditer": lambda pattern, string: CountedPattern(pattern).finditer(string)})
    for module in (recognizers, sys.modules[type(recognizer).__module__]):
        monkeypatch.setattr(module, "re", counted_re)
    monkeypatch.setattr(nl, "SPACE_GROUPS", CountedPattern(SPACE_GROUPS))

    def starts(count: int) -> int:
        CountedPattern.starts = 0
        list(recognizer.find("1" * count, (), request))
        return CountedPattern.starts

    assert 0 < starts(8000) == starts(1000)


@pytest.mark.parametrize("pattern", [_FRACTION, _DATE, EN.data["patterns"]["expression"],
                                     "[0-9]+(?:" + "|".join(map(re.escape, EN.data["range_marks"])) + ")[0-9]+",
                                     "[-+]?[0-9]+/[0-9]", "[-+]?[0-9]+[-+]", SPACE_GROUPS,
                                     "([0-9]{1,3}(?:[ \u00a0][0-9]{3})+|[0-9]+)-"])
@pytest.mark.parametrize("seed", range(20))
def test_matches_from_digit_runs_are_the_matches_of_finditer(pattern, seed):
    rng = random.Random(seed)
    pieces = ["1", "12", "007", "1234", " 000", "1" * 30, "/", "-", "–", "+", "−", "=", " ", "\u00a0", ".", ",", "x",
              ":"]
    for _ in range(200):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 12)))
        expected = [m.span() for m in re.finditer(pattern, text)]
        assert [m.span() for m in digit_run_matches(pattern, text)] == expected, text


def test_the_numbers_of_a_text_are_kept_for_one_call_only():
    first, second = analyze("It costs $5 at 14:30.", "en").request, analyze("It costs $5 at 14:30.", "en").request
    assert ("numbers", "It costs $5 at 14:30.") in first.memo
    assert second.memo is not first.memo
    assert not hasattr(find_numbers, "cache_info") and not hasattr(fold_digits, "cache_info")


def test_a_digit_next_to_a_span_is_no_joiner():
    """Section 2.1: the joining character is not a space and not a digit."""
    span = Span(0, 2, Form.CARDINAL, FrozenMap())
    text = "ab12"
    sides = _sides(span, {}, {})
    assert not _joined(text, span, bytearray(len(text)), [None] * len(text), sides, bytearray(len(text)))
    assert _joined("ab/2", span, bytearray(4), [None] * 4, sides, bytearray(4))


def test_a_space_between_groups_of_three_digits_joins_them():
    """Section 2.1 and BIPM, SI Brochure, 9th edition, section 5.4.4: digits "may be divided into groups of three by
    a space", so the space joins the groups as a mark does. A mark and digits after the run belong to it, as in
    `1 250.5`. A space joins nothing when a digit is next to the run or one character away, as in `123 456 78`,
    `1.6 125`, `+34 481.312 50` and `470-2 487`, and nor does a space after a code, as in `K1 500`. A fraction after a
    decimal comma takes groups too, as in `0,264 7`, where each group but the last has three digits, so `1 250,50 2`
    is no such run. Where the comma groups thousands, `1,000 18` is two numbers."""
    span = Span(0, 2, Form.CARDINAL, FrozenMap())
    sides = _sides(span, {}, {})
    assert _joined("12 000", span, bytearray(6), [None] * 6, sides, _group_spaces("12 000", True))
    assert not _joined("12 00", span, bytearray(5), [None] * 5, sides, _group_spaces("12 00", True))
    assert list(_group_spaces("12 000 0001", True)) == [0] * 11
    assert list(_group_spaces("0800 123 456", True)) == [0] * 12
    assert list(_group_spaces("1 000 000-2", True)) == [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    assert list(_group_spaces("1.6 125", True)) == [0] * 7
    assert list(_group_spaces("K1 500", True)) == [0] * 6
    assert list(_group_spaces("3.537,03 176.851", True)) == [0] * 16
    assert list(_group_spaces("(00) 08 199", False)) == [0] * 7 + [1, 0, 0, 0]
    assert list(_group_spaces("1 250.5 kg", True)) == [0, 1] + [0] * 8
    assert list(_group_spaces("+34 481.312 50", True)) == [0] * 14
    assert list(_group_spaces("091 081-95 3", True)) == [0] * 12
    assert list(_group_spaces("470-2 487", True)) == [0] * 9
    assert list(_group_spaces("0,264 7", True)) == [0, 0, 0, 0, 0, 1, 0]
    assert list(_group_spaces("0,264 7 12", True)) == [0] * 10
    assert list(_group_spaces("1 250,50 2", True)) == [0] * 10
    assert list(_group_spaces("0,264 7", False)) == [0] * 7
    assert list(_group_spaces("1,000 18", False)) == [0] * 8
    assert list(_group_spaces("12 000", False)) == [0, 0, 1, 0, 0, 0]


def test_a_long_digit_run_before_a_comma_takes_linear_time():
    def seconds(count: int) -> float:
        start = time.perf_counter()
        _group_spaces("1" * count + ",x", True)
        return time.perf_counter() - start

    small, large = min(seconds(4000) for _ in range(3)), min(seconds(32000) for _ in range(3))
    assert large < 20 * small, (small, large)


def test_digits_from_two_digit_sets_stay_as_written_in_a_language_with_no_file():
    assert normalize("Et huet １2 Zëmmer.", "lb") == "Et huet １2 Zëmmer."


@pytest.mark.parametrize("space", [" ", "\t", "\n"])
def test_a_year_at_the_end_of_the_text_before_a_space_reads(space):
    assert normalize(f"In 1999{space}", "en-GB") == f"In nineteen ninety-nine{space}"


@pytest.mark.xfail(strict=True, reason="a number between the phone word and a short code: the code reads as a quantity")
def test_a_short_code_behind_another_number_reads_the_same_on_a_second_pass():
    once = normalize("Call 45./999 now.", "en-GB")
    assert once == "Call forty-five./nine nine nine now."
    assert normalize(once, "en-GB") == once


def test_render_gives_a_verbalizer_the_words_of_its_clause_only(monkeypatch):
    seen = []

    def spy(span, context):
        seen.append((context.before, context.after))
        return "N"

    spec = replace(EN, verbalizers={**EN.verbalizers, Form.CARDINAL: spy})
    monkeypatch.setattr(loader, "_registry", lambda: {"en": spec})
    assert normalize("We left. Then 5 came; all went.", "en") == "We left. Then N came; all went."
    assert seen == [(("Then",), ("came",))]


def test_a_named_run_with_no_known_country_code_stays_as_written():
    assert normalize("Call +999.", "en-GB") == "Call +999."
    assert normalize("Call +9 now.", "en-GB") == "Call +9 now."


def test_the_window_names_only_a_phone_shaped_run_or_a_short_code():
    assert normalize("Call me at 999.", "en-GB") == "Call me at nine nine nine."
    assert normalize("Call me at 100.", "en-GB") == "Call me at one hundred."
    assert normalize("Phone sales hit 2500000 units.", "en-GB") == \
        "Phone sales hit two million five hundred thousand units."
    # No phone word names `555 1234`, and its groups are no thousands grouping, so it stays as written.
    assert normalize("Call the office staff later at 555 1234.", "en-GB") == "Call the office staff later at 555 1234."


@pytest.mark.parametrize("text", ["Dial 25 and 999.", "Call 25 or 999.", "Call 999 or 112 or 2 friends.",
                                  "Call 0099 1234 5678 now.", "Ring Dial \u0663--0700", "Tel 2, +999.",
                                  "Call 911 or 1234567890123456.",
                                  "Call 999 or +999."])
def test_a_digit_reading_of_a_named_run_reads_the_same_on_a_second_pass(text):
    once = normalize(text, "en-GB")
    assert once != text
    assert normalize(once, "en-GB") == once


def test_a_letter_sign_blocks_a_year_only_as_the_whole_follower():
    assert normalize("In 1999 x 2 rose.", "en-GB") == "In one thousand nine hundred and ninety-nine x two rose."
    assert normalize("In 1999 xUnit spread.", "en-GB") == "In nineteen ninety-nine xUnit spread."


def test_a_lexicon_key_that_starts_with_a_full_stop_sees_the_words_before_it(monkeypatch):
    seen = []

    def spy(span, context):
        seen.append(context.before)
        return span.fields["spoken"]

    spec = replace(EN, verbalizers={**EN.verbalizers, Form.LEXICON: spy})
    monkeypatch.setattr(loader, "_registry", lambda: {"en": spec})
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({".NET": "dot net"})}))
    assert normalize("Use .NET now.", "en", params) == "Use dot net now."
    assert seen == [("Use",)]


def test_a_run_with_a_letter_attached_stays_as_written():
    for text in ("Text 020 7946 0018pages now.", "Use 020 7946 0018pages now.", "Phone: cell 0099 now020 7946 0018"):
        assert normalize(text, "en-GB") == text


@WORD_BACK_LOSS
def test_the_window_counts_three_content_words_within_eight_words():
    assert normalize("Call the team at the office on 555 1234.", "en-GB") == \
        "Call the team at the office on five five five one two three four."


def test_the_window_names_a_run_that_starts_with_a_zero():
    assert normalize("Call us on 02079460018.", "en-US") == \
        "Call us on zero two zero seven nine four six zero zero one eight."


@pytest.mark.xfail(strict=True, reason="a run that a list link joins to a kept run reads as a quantity")
def test_a_kept_run_that_a_joiner_continues_starts_a_phone_list():
    assert normalize("Call 0800 123 456/7 or 5551234.", "en-GB") == \
        "Call 0800 123 456/7 or five five five one two three four."


def test_the_core_telephone_holds_no_english_rule(gendered, monkeypatch):
    """A language whose group mark is a space and that uses the shared telephone recognizer reads `10 000` as
    one number. The thousands keep is a rule of `EnglishTelephone` in `en.py`, and the core holds none."""
    words = {"10000": "dez mil"}
    spec = replace(gendered.LANGUAGE, data=freeze({"defaults": {},
                                                   "number_marks": {"Latn": [{"decimal": ",", "group": " "}]}}),
                   recognizers=(SHARED["telephone"], SHARED["cardinal"]),
                   verbalizers={Form.CARDINAL: lambda span, context: words[span.fields["digits"]],
                                Form.TELEPHONE: lambda span, context: " ".join(span.fields["groups"])})
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    assert normalize("A vila tem 10 000 pessoas.", "qaa") == "A vila tem dez mil pessoas."


@pytest.mark.xfail(strict=True, reason="a run with a case ending gives no telephone span")
def test_a_case_ending_joins_every_form_that_holds_a_number(gendered, monkeypatch):
    """A language with case endings reads `20%ko`, `5€ko` and `943 123 456ra` as one span each, with the ending in
    the `suffix` field of the form (design section 4.4)."""
    data = freeze({"defaults": {}, "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
                   "case_suffixes": ["ko", "ra"], "percent": {"signs": ["%"], "position": "after"},
                   "currencies": {"EUR": {"symbols": ["€"]}}, "phone_words": ["deitu"]})
    spec = replace(gendered.LANGUAGE, data=data,
                   recognizers=(SHARED["telephone"], SHARED["money"], SHARED["percent"], SHARED["cardinal"]))
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    for text, form, written, suffix in (("Prezioaren 20%ko igoera.", Form.PERCENT, "20%ko", "ko"),
                                        ("5€ko sarrera.", Form.MONEY, "5€ko", "ko"),
                                        ("Deitu 943 123 456ra.", Form.TELEPHONE, "943 123 456ra", "ra")):
        spans = analyze(text, "qaa").spans
        assert [(text[s.start:s.end], s.form, s.fields["suffix"], s.keep) for s in spans] == [(written, form, suffix,
                                                                                                False)]


def test_a_proclitic_before_a_numeric_date_stays_in_the_reading(gendered, monkeypatch):
    """A declared proclitic before a numeric date is the `prefix` of the `DATE` span, and the attachment step
    joins it to the spoken date (design section 4.4)."""
    data = freeze({"defaults": {"date_order": "DMY"}, "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
                   "proclitics": ["بـ"]})
    spec = replace(gendered.LANGUAGE, data=data, recognizers=(SHARED["date_numeric"],),
                   verbalizers={Form.DATE: lambda span, context: "<date>"},
                   options={**gendered.LANGUAGE.options, "date_order": frozenset({"DMY", "MDY", "YMD"})},
                   not_applicable=gendered.LANGUAGE.not_applicable - {"date_order"})
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    assert [span.fields["prefix"] for span in analyze("x بـ10/6/2026 y", "qaa").spans] == ["بـ"]
    assert normalize("x بـ10/6/2026 y", "qaa") == "x بـ<date> y"


def test_a_clock_mark_of_the_language_reads_a_time(gendered, monkeypatch):
    """A language whose `clock_marks` table holds `h` with no evidence needed reads `14h30` as a time, as
    Portuguese writes it. The table, not the core, names the marks (design section 4.2)."""
    data = freeze({"defaults": {}, "time_words": [], "day_periods": {}, "range_word": "às",
                   "clock_marks": [{"mark": "h", "seconds": False, "needs": "none"}]})
    spec = replace(gendered.LANGUAGE, data=data, recognizers=(SHARED["time_clock"],),
                   verbalizers={Form.TIME: lambda span, context: f"{span.fields['hour']} e {span.fields['minute']}"})
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    assert normalize("A loja abre às 14h30.", "qaa") == "A loja abre às 14 e 30."


def test_a_clock_mark_that_closes_an_hour_reads_a_bare_hour(gendered, monkeypatch):
    """A mark with `closes_hour` closes an hour with no minutes, so `às 14h` and `das 9h às 18h` read as times, as
    Portuguese writes them. A mark without it leaves the bare hour as written (design section 4.2)."""
    def use(clock):
        data = freeze({"defaults": {}, "time_words": [], "day_periods": {}, "range_word": "às",
                       "clock_marks": [{"mark": "h", "seconds": False, "needs": "none", **clock}]})
        verbalizers = {Form.TIME: lambda span, context: f"<{span.fields['hour']}:{span.fields['minute']:02}>"}
        spec = replace(gendered.LANGUAGE, data=data, recognizers=(SHARED["time_clock"],), verbalizers=verbalizers)
        monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})

    use({"closes_hour": True})
    assert normalize("A loja abre às 14h.", "qaa") == "A loja abre às <14:00>."
    assert normalize("Aberto das 9h às 18h30.", "qaa") == "Aberto das <9:00> às <18:30>."
    assert normalize("Abre às 25h.", "qaa") == "Abre às 25h."
    use({})
    assert normalize("A loja abre às 14h.", "qaa") == "A loja abre às 14h."


def test_the_join_range_hook_of_the_language_joins_a_range(gendered, monkeypatch):
    """A mark of `range_marks` between two spans joins them through the `join_range` hook of the language, so a
    language can place its range words or endings by its own grammar."""
    data = freeze({"defaults": {}, "number_marks": {"Latn": [{"decimal": ",", "group": "."}]}, "range_word": "to",
                   "range_marks": ["–"], "percent": {"signs": ["%"], "position": "after"}})

    def between(span, following, range_word):
        return replace(span, end=following.start, trail=" eta "), following

    spec = replace(gendered.LANGUAGE, data=data, recognizers=(SHARED["percent"],), join_range=between,
                   verbalizers={Form.PERCENT: lambda span, context: f"{span.fields['amount']['integer']} ehuneko"})
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    assert normalize("10%–20%", "qaa") == "10 ehuneko eta 20 ehuneko"
    assert normalize("10%-20%", "qaa") == "10 ehuneko-20 ehuneko"


def test_the_join_range_hook_puts_an_ending_on_each_reading(gendered, monkeypatch):
    """A language that marks a range with case endings has no range word. Its `join_range` hook still runs, and
    gives each span of the pair its ending through the `suffix` field, which `attach` joins to the reading: the
    first takes the ablative and the second the allative, as Basque writes `10%-20%`."""
    data = freeze({"defaults": {}, "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
                   "range_marks": ["-"], "percent": {"signs": ["%"], "position": "after"}})

    def endings(span, following, range_word):
        return (replace(span, end=following.start, trail=" ", fields=FrozenMap({**span.fields, "suffix": "etik"})),
                replace(following, fields=FrozenMap({**following.fields, "suffix": "ra"})))

    spec = replace(gendered.LANGUAGE, data=data, recognizers=(SHARED["percent"],), join_range=endings,
                   verbalizers={Form.PERCENT: lambda span, context: f"{span.fields['amount']['integer']} ehuneko"})
    monkeypatch.setattr(loader, "_registry", lambda: {"qaa": spec})
    assert normalize("10%-20%", "qaa") == "10 ehunekoetik 20 ehunekora"


@pytest.mark.parametrize("text, operands, operators", [
    ("−3+3", ("−3", "3"), ("+",)),
    ("−3−3", ("−3", "3"), ("−",)),
    ("−3 − 3", ("−3", "3"), ("−",)),
    ("-3−3", ("-3", "3"), ("−",)),
    ("3−3", ("3", "3"), ("−",)),
    ("−12 × 3 ÷ 4 = 9", ("−12", "3", "4", "9"), ("×", "÷", "=")),
    ("+3+3", ("+3", "3"), ("+",)),
    ("3 − −3", ("3", "−3"), ("−",)),
    ("3++3", ("3", "+3"), ("+",)),
    ("2 − 5 = −3", ("2", "5", "−3"), ("−", "=")),
])
def test_a_leading_sign_binds_to_the_first_operand(text, operands, operators):
    span = next(s for s in analyze(text, "en").spans if s.form is Form.EXPRESSION)
    assert (span.fields["operands"], span.fields["operators"]) == (operands, operators)


@pytest.mark.parametrize("text, expected", [
    ("−3+3", "minus three plus three"),
    ("−3−3", "minus three minus three"),
    ("−3 − 3", "minus three minus three"),
    ("−12÷3", "minus twelve divided by three"),
    ("−3 ×3", "minus three times three"),
])
@pytest.mark.parametrize("strict", [False, True])
def test_a_leading_minus_sign_reads_in_both_modes(text, expected, strict):
    assert normalize(text, "en-GB", NormalizationParams(strict=strict)) == expected


@pytest.mark.parametrize("text, expected", [
    ("-2+3=1", "minus two plus three equals one"),
    ("2−5=−3", "two minus five equals minus three"),
    ("2 − 5 = −3", "two minus five equals minus three"),
    ("+3+3", "plus three plus three"),
    ("3 − −3", "three minus minus three"),
    ("3−−3", "three minus minus three"),
    ("3++3", "three plus plus three"),
    ("3+-3", "three plus minus three"),
    ("−3 × −3", "minus three times minus three"),
    ("Score: −3 − −3 = 0", "Score: minus three minus minus three equals zero"),
    ("Pages 12−15", "Pages twelve minus fifteen"),
])
@pytest.mark.parametrize("strict", [False, True])
def test_each_operand_reads_its_sign(text, expected, strict):
    """Section 4.2: each integer may carry one sign, `-`, `−` or `+`, right before its digits, and the sign reads as
    its sign word. A sign on a later integer follows an operator."""
    assert normalize(text, "en-GB", NormalizationParams(strict=strict)) == expected


def test_an_operators_table_without_an_operator_of_the_pattern_reads_no_expression():
    """The pattern and the `operators` table can disagree in a variety; the match then has no operator to read."""
    recognizer = next(r for r in EN.recognizers if r.name == "expression")
    request = analyze("1", "en").request
    operators = {k: v for k, v in EN.data["operators"].items() if k != "÷"}
    language = replace(EN, data=freeze({**thaw(EN.data), "operators": operators}))
    assert list(recognizer.find("3÷3", (), replace(request, language=language))) == []


@pytest.mark.parametrize("tag, text", [
    ("en-GB", "--3+3"),
    ("en-GB", "+-3+3"),
    ("en-GB", "−−3 × 3"),
    ("en-GB", "3+--3"),
    ("en-GB", "3−−−3"),
    ("en-GB", "So 3 − +−3 now."),
    ("en-US", "$−3+3"),
    ("en-US", "$-3+3"),
    ("en-GB", "£−3+3"),
    ("en-GB", "€−3 × 3"),
    ("en-GB", "×3+3"),
    ("en-GB", "3+3°"),
])
def test_an_expression_with_two_signs_on_one_operand_or_a_symbol_next_to_it_stays_as_written(tag, text, caplog):
    """Section 4.2: two signs before one integer keep the expression as written, and no other form claims a number
    next to a symbol of the `symbols` table. Section 10: the unread run gives a WARNING, and an error when strict."""
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(text, tag) == text
    assert any("unread written form" in r.message for r in caplog.records)
    with pytest.raises(UnreadFormError):
        normalize(text, tag, NormalizationParams(strict=True))


@pytest.mark.parametrize("lang, left, mark, right", [
    ("en-US", "$12", ".", "-1/2"), ("en-US", "$12", ".", "+1/2"), ("en-GB", "£5", ",", "−1/4"),
    ("en-US", "12/03/2024", ":", "+1/2"), ("en-GB", "12/03/2024", ":", "+1/2")])
def test_a_signed_fraction_after_a_mark_reads_once_the_number_before_the_mark_reads(lang, left, mark, right):
    once = normalize(left + mark + right, lang)
    assert once == normalize(left, lang) + mark + normalize(right, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize("text", ["12:-1/2", "1,-1/2", "(1,-1/2)", "5.−1/2"])
def test_a_signed_fraction_that_a_mark_joins_to_a_bare_number_stays_as_written(text, caplog):
    assert normalize(text, "en-GB") == text
    assert "unread written form" in caplog.text


@pytest.mark.parametrize("text", ["50% 1 000, 1️⃣", "Een groei van 5 % 1 000 keer."])
def test_groups_after_a_percentage_read_the_same_on_a_second_pass(text):
    """Section 11. The percentage reads its sign, so the groups after it read on the first pass."""
    once = normalize(text, "nl-BE")
    assert normalize(once, "nl-BE") == once


def test_groups_at_the_start_of_the_text_read_as_a_cardinal():
    """Taaladvies.net, 10.000.000 / 10 000 000: the space groups the digits, so `12 000` reads "twaalfduizend"."""
    assert normalize("12 000 mensen wonen hier.", "nl-NL") == "twaalfduizend mensen wonen hier."


@pytest.mark.parametrize("lang", ["es-CR", "es-ES"])
def test_a_phone_word_after_a_hyphen_keeps_its_run_on_a_second_pass(lang):
    """Section 11. A hyphen joins the reading of the amount to `Tel` on a second pass, and `Tel` still names the run."""
    once = normalize("Dr. 12,50 €-Tel.. 1.000,5-", lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize("lang", ["eu-x-nafarra-beherea", "eu-ES"])
def test_a_word_after_a_number_is_no_unit_and_case_ending_on_a_second_pass(lang):
    """Section 11. `sei` is a word, not the unit `s` and the ending `ei`, so a second pass reads no measure."""
    once = normalize("Appelez le 0033 6 12 34 56 78 ici.", lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("Il faut 1 000 000-2 000 000 personnes.", "de-DE"), ("Il faut 1 000 000-2 000 000 personnes.", "es-BO"),
    ("Il faut 1 000 000-2 000 000 personnes.", "es-ES"), ("Il faut 1 000 000-2 000 000 personnes.", "es-US"),
    ("Il faut 1 000 000-2 000 000 personnes.", "es-UY"), ("Het kost € 12 000 000,00.", "it-IT"),
    ("Het kost € 12 000", "it-IT"), ("Het kost € 12 000.", "it-IT"), ("Het kost € 12 000.", "it-SM"),
    ("+34 481.312 50 2x.", "de-DE"), ("+34 481.312 50 2x.", "es-ES"), ("+34 481.312 50 2x.", "pt-PT"),
    ("091 081-95 3/7", "de-DE"), ("+49 914-622 56 329:47", "en-GB"), ("+351 514 579.16 091 36", "en-GB"),
    ("+1 633-427 864 3D", "de-AT"), ("Fax: 83:044 5226 470-2 487", "de-DE"), ("174 01-426 534 589", "en-GB"),
    ("Fax: (491:62 7 6-8181-7 964)", "es-MX"), ("+43 (0)08 717 80 1st", "en-GB"),
    ("Tel. 665.037 (0)74 513 77 8 101 36 12 h", "es-MX"), ("Ligue 84-607 (0)0902 2 89 373 3204-4 und", "pt-PT"),
    ("+43 (1)08 717 80 1st", "en-GB"), ("Tel. 665.037 (1)74 513 77 8 101 36 12 h", "es-MX"),
    ("Ligue 84-607 (2)0902 2 89 373 3204-4 und", "pt-PT"),
])
def test_a_number_grouped_with_spaces_reads_the_same_on_a_second_pass(text, lang):
    """Section 11. No span reads one group of a number grouped with spaces, so no group is left for a second pass.
    A run that a digit continues or starts is no such number, so it reads on the first pass, as `+34 481.312 50 2x.`
    does: a second pass that finds the run kept as written before a number word reads it as a telephone number."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "expected"), [
    pytest.param("(1) 0 437 593", "en-GB", "(one) zero four three seven five nine three", marks=BRACKET_LOSS),
    ("(12) 0 437 593", "en-US", "one two zero four three seven five nine three"),
    pytest.param("Step (3) 0 800 123 456", "en-GB", "Step (three) zero eight zero zero one two three four five six",
                 marks=BRACKET_LOSS),
    pytest.param("(1) 0 437 593", "de-DE", "(eins) null vier drei sieben fünf neun drei", marks=BRACKET_LOSS),
    pytest.param("x(12) 0 437 593", "de-DE", "x(zwölf) null vier drei sieben fünf neun drei", marks=BRACKET_LOSS),
])
def test_a_run_after_a_number_in_brackets_reads_as_on_a_second_pass(text, lang, expected):
    """Section 11. A number in brackets that no telephone reading takes as an area code leaves the run after it, so
    the run reads digit by digit on the first pass, as it does after `[1]` and as a second pass reads it after
    `(one)`. An area code of two digits with no `0` in brackets is evidence, so `(12)` reads with the run."""
    once = normalize(text, lang)
    assert once == expected
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "say_as"), [
    ("(09) 0919321487 0", "fr-FR", None),
    ("(01) 0612345678 8 h", "fr-FR", None),
    ("(09) 0612345678 24 h/24", "fr-FR", None),
    ("(09) 0919321487 0", "fr-CA", None),
    ("(09) 0612345678 0", "pt-BR", SayAs(interpret_as="telephone")),
])
def test_a_run_after_a_number_in_brackets_with_a_leading_0_reads_as_on_a_second_pass(text, lang, say_as):
    """Section 11. A number in brackets such as `(09)` reads as no cardinal, so a second pass sees the same
    bracketed run, and the run after it is not tried alone on the first pass either."""
    once = normalize(text, lang, say_as=say_as)
    assert normalize(once, lang, say_as=say_as) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("(0) 0 437 593-9085", "en-GB"),
    ("Note (84/34-8 (0) 0 437 593-9085), Tel. 360/259-23 00 62-839-4799 956 895 12 h Call [0347 899 867 443 (81)] 1st",
     "en-GB"),
    ("Nota (112-388 2097 630)/2 telefone 08.43 (0) 320 294 211-917 413 und", "pt-BR"),
])
def test_a_run_after_a_lone_0_in_brackets_reads_as_on_a_second_pass(text, lang):
    """Section 11. A lone `(0)` reads as the cardinal zero, so a second pass sees the run after it alone, and the
    first pass tries that run alone too."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("Call 1-800-555-0199 8 a.m. to 5 p.m.", "es-US"), ("Llame al 1-800-555-0199 8 a.m. a 5 p.m.", "es-US"),
    ("23.59 +1 800 555 1234 2.5 2ª", "fr-CH"),
])
def test_an_hour_after_a_phone_number_reads_the_same_on_a_second_pass(text, lang):
    """Section 11. A last group of one or two digits that a day period follows, or that a word continues, is no
    phone group, so the run is the one that a second pass finds."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("0 437 593 (0) 0 437 593", "it-IT"), ("0 437 593 (0) 0 437 593", "pt-PT"), ("0 437 593 (0) 0 437 593", "ar"),
    ("(0) 0 437 593 (0) 0 437 593", "nl-NL"), ("(09) 0 437 593 (09) 0 437 593", "it-IT"),
    ("0 437 593 (020) 437 593", "ja-JP"), ("12 000 (1) 437 593", "en-GB"), ("12 000 (1) 437 593", "en-US"),
    ("12 000 (1) 437 593", "de-DE"), ("12 000 (1) 437 593", "es-ES"),
])
def test_a_second_telephone_number_reads_on_the_first_pass(text, lang):
    """Section 11. With say-as `telephone`, the number in brackets of the second run is the word after the first
    run, so it counts as the evidence that keeps the first run as written. The say-as reads the first run, so that
    run keeps nothing, and the say-as reads the second run on the first pass, as a second pass does."""
    say_as = SayAs(interpret_as="telephone")
    once = normalize(text, lang, say_as=say_as)
    assert normalize(once, lang, say_as=say_as) == once


@pytest.mark.parametrize(("text", "lang", "value", "expected"), [
    ("(0)-12 000,5", "fr-FR", "telephone", "(0)-12 000,5"),
    ("+44 (0)20 7946 0958", "en-US", "digits", "plus four four zero two zero seven nine four six zero nine five eight"),
])
def test_a_kept_run_that_no_telephone_number_holds_keeps_its_evidence_word(text, lang, value, expected):
    """A kept run keeps the word after it as its evidence unless a telephone number of the say-as holds the run, so
    `(0)-12 000,5` keeps that word as written: no telephone number holds `12 000,5`. Under say-as `digits`, the run
    with `+` and a country code reads digit by digit."""
    assert normalize(text, lang, say_as=SayAs(interpret_as=value)) == expected


@pytest.mark.parametrize(("text", "lang"), [
    ("(503 104) 8 000 000 2nd.", "en-GB"), ("482 985.41 +49\xa0200\xa0420\xa0471 7 000 000", "ru-RU"),
    ("( 00)217 670\xa00\xa0107", "sv-SE"), ("0601979583/+44 (0)62 3427 9129 €.", "nl-NL"),
    ("(6 000 000) 0925054722/(1)123 264,68", "pt-BR"), ("(09)7\u202f000\u202f000 0993133993 €.", "ca-ES"),
    ("2,2 0145900045/+39 100 438 905\u202f0753995967", "eu-ES"),
])
def test_a_telephone_number_relies_only_on_a_kept_telephone_number_that_the_say_as_reads(text, lang):
    """Sections 11 and 17.7. With say-as `telephone`, a telephone number that holds the evidence word of a run kept
    as written reads only when the plain analysis keeps that run as a telephone number and a telephone number of the
    say-as that reads holds it. Else the run and its evidence word stay as written on the first pass, and on a
    second pass with the same say-as or with none."""
    say_as = SayAs(interpret_as="telephone")
    once = normalize(text, lang, say_as=say_as)
    assert normalize(once, lang, say_as=say_as) == once
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "value", "same"), [
    ("[09]284 884\xa0230 154.98/(00) 201 193 / 23:58 €.", "de-DE", "telephone", False),
    ("(00)17/10/2018; (1) 152 397 / (1) 934 029.53", "de-DE", "telephone", True),
    ("3 km 830\xa0333,66 4 000 000", "nl-NL", "telephone", True),
    ("383 470.21 people 437 007,33 7 000 000", "nl-NL", "telephone", True),
    ("0498124205, 513 588,48 322\xa0394", "nl-NL", "characters", True),
    ("Call 370 227 Tel. 17 - 9.8  [1]-292 262.79", "pt-PT", "characters", False),
])
def test_a_second_pass_reads_no_digit_that_the_say_as_left(text, lang, value, same):
    """Sections 11 and 17.7. A telephone number that a mark joins to the number it supports reads only with it. A run
    that the plain analysis keeps as a telephone number is a say-as candidate, as a second pass sees it once the
    number in brackets before it reads. nl keeps a run with short groups after its decimal comma whole. Say-as
    `characters` asks for every digit, as `telephone` does. So no digit that the first pass leaves reads on a second
    pass with no say-as, nor with the same say-as where `same` is true. A second pass with say-as `characters` spells
    the words of the first."""
    say_as = SayAs(interpret_as=value)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        once = normalize(text, lang, say_as=say_as)
        assert normalize(once, lang) == once
        if same:
            assert normalize(once, lang, say_as=say_as) == once


@pytest.mark.parametrize(("text", "lang", "expected"), [
    ("5@+351 000.7-4171 508 524", "en-GB",
     "five at plus three five one 000.7-4171 five hundred and eight five hundred and twenty-four"),
    ("Tel. 5@+351 000.7-4171 508 524", "en-US",
     "Tel. five at plus three five one 000.7-4171 five hundred eight five hundred twenty-four"),
])
def test_a_digit_in_the_word_before_a_run_refuses_its_group_spaces(text, lang, expected):
    """Section 11. A digit in the characters before a run up to a space joins the first group to the word
    that holds it, so the run is no number in groups, and the groups read alone, as dev reads them. If the run were
    one number, `351` would read with `5@+` and leave `508 524` waiting, and a second pass would read it.
    `000.7-4171` stays as written in both texts, as a run that marks join to other digits."""
    once = normalize(text, lang)
    assert once == expected
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "expected"), [
    ("x@12 000 000 €", "en-GB", "ex at one two 000 zero euros"),
    ("x €#@205 530 332 €", "pt-PT",
     "x € cardinal arroba dois zero cinco quinhentos e trinta trezentos e trinta e dois euros"),
    ("mail me@205 530 332 people", "en-GB",
     "mail em e at two zero five five hundred and thirty three hundred and thirty-two people"),
])
def test_a_character_glued_to_a_run_refuses_its_group_spaces(text, lang, expected):
    """Section 11. A character before a run that is not a space, a currency sign or an opening bracket holds its
    first group, so the run is no number in groups, and its groups read alone, as dev reads them. If the run were one
    number, the address would read `12` and leave `000 000` waiting, and a second pass would read it."""
    once = normalize(text, lang)
    assert once == expected
    assert normalize(once, lang) == once


_DROP_WORDS = {"en-US": "Dial", "en-GB": "Tel.", "de-DE": "Fax:", "es-ES": "Tel.", "fr-CH": "téléphone",
               "pt-PT": "telefone"}
_DROP_RUNS = ("130\xa0509,30 118", "281 039,0 % 84", "020 18:30", "916 047 319,233", "0990 3617 18:30 436",
              "164\xa0752,806")
_DROP_TEXTS = [(lang, word + join + run + tail) for lang, word in _DROP_WORDS.items() for join in ("", " ", "+44 ")
               for run in _DROP_RUNS for tail in ("", " (020)")] + [
    ("en-US", "Dial+44 164\xa0752,806\xa0- (3)"), ("en-GB", "Tel. 281 039,0 % 84\u202f585\u202f976"),
    ("de-DE", "Fax:\u202f916 047 319,233\u202f7.7509 €"), ("es-ES", "Tel.\xa020 18:30 (020)"),
    ("fr-CH", "téléphone 130\xa0509,30 118\u202f005\u202f905 1st"),
    ("fr-CA", "Tél.0990 3617 18:30 436\u202f292,88\xa0+ 78 , (12)")]
_SPOKEN_FIELDS = {Form.TELEPHONE: ("country_code", "groups", "prefix", "suffix"), Form.IDENTIFIER: ("head", "digits"),
                  Form.LETTERS: ("letters",)}


@pytest.mark.parametrize("value", ["telephone", "digits", "characters", "cardinal", None])
def test_a_reading_speaks_every_digit_of_its_text(value):
    """Sections 17.2 and 17.5. A span that reads digit by digit speaks each digit of its text, in the order the text
    writes them: the digits of its fields equal the digits of its text. A kept telephone run can hold more text than
    its groups, as the `+44` of `Dial+44 164` and the `,30 118` of `130 509,30 118`, so it reads under `telephone`
    only when its groups hold every digit and no `+`. A second pass cannot find the text a reading drops, because the
    output is stable. The texts put a phone word, glued or not, before runs that end in a decimal, a time or a sign."""
    say_as = None if value is None else SayAs(interpret_as=value)
    dropped = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        for lang, text in _DROP_TEXTS:
            for span in analyze(text, lang, say_as=say_as).spans:
                if span.form in _SPOKEN_FIELDS and not span.keep:
                    spoken = "".join("".join(span.fields[field]) for field in _SPOKEN_FIELDS[span.form])
                    written = text[span.start:span.end]
                    if "".join(filter(str.isdigit, fold_digits(spoken))) \
                            != "".join(filter(str.isdigit, fold_digits(written))):
                        dropped.append((lang, text, written))
    assert dropped == []


@pytest.mark.parametrize(("text", "lang", "expected", "same"), [
    ("Tél.\xa076 50h 087 5778 53 6370 % 36", "fr-CH",
     "Tél.\xa0septante-six cinquante heures zéro huit sept cinquante-sept septante-huit cinquante-trois soixante-trois "
     "septante % trente-six", True),
    ("Tel. 0171 23x 4567", "de-DE", "Telefon 0171 23x vier fünf sechs sieben", True),
    pytest.param("telefone 912 34a 678", "pt-PT", "telefone novecentas e doze 34a seis sete oito", True,
                 marks=GLUED_LOSS),
])
def test_say_as_telephone_reads_no_kept_run_glued_to_a_word(text, lang, expected, same):
    """Section 17.4 step 3. A run that a letter or a digit touches is kept as written for the word it is glued to,
    not for want of evidence, so say-as `telephone` does not read it, and a second pass changes nothing. Read as a
    telephone number, `23x` would give "dreix". The run
    `087 5778 53 6370` of fr-CH touches no word: the plain analysis keeps it because no number reading groups it, so
    the say-as reads it."""
    say_as = SayAs(interpret_as="telephone")
    once = normalize(text, lang, say_as=say_as)
    assert once == expected
    assert normalize(once, lang) == once
    if same:
        assert normalize(once, lang, say_as=say_as) == once


@pytest.mark.parametrize(("text", "lang", "say_as", "expected"), [
    pytest.param("Call the police on 999.", "en-GB", None, "Call the police on nine nine nine.",
                 marks=WORD_BACK_LOSS),
    pytest.param("Call the police on 999 now.", "en-GB", None, "Call the police on nine nine nine now.",
                 marks=WORD_BACK_LOSS),
    pytest.param("Call the office on 555-1234.", "en-GB", None, "Call the office on five five five one two three four.",
                 marks=WORD_BACK_LOSS),
    pytest.param("Text 0800 123 456–00 44", "en-GB", None, "Text 0800 123 456–00 44",
                 marks=pytest.mark.xfail(strict=True, reason="a group after a kept run reads as a quantity")),
    pytest.param("teléfono 2 062 6 9.30 aquí.", "es-ES", None, "teléfono dos cero seis dos seis 9.30 aquí.",
                 marks=pytest.mark.xfail(strict=True, reason="a time after a short code reads digit by digit")),
    pytest.param("telefone le (12) 872 523 454,71.", "pt-PT", None,
                 "telefone le (doze) oitocentos e setenta e dois milhões quinhentos e vinte e três mil quatrocentos "
                 "e cinquenta e quatro vírgula setenta e um.",
                 marks=pytest.mark.xfail(strict=True, reason="a bracketed area code keeps an amount as written")),
])
def test_a_phone_reading_that_the_simple_rule_loses(text, lang, say_as, expected):
    """Readings that the evidence of section 4.3 does not reach. Each reason names the class of the loss."""
    assert normalize(text, lang, say_as=say_as) == expected


@pytest.mark.parametrize(("text", "lang", "value", "expected"), [
    ("28\xa0944 856", "ko-KR", "characters", "이 팔\xa0구 사 사 팔 오 육"),
    ("(1) 685 666; 94, 64", "de-DE", "telephone", "eins sechs acht fünf sechs sechs sechs; neun vier, sechs vier"),
    ("351 912", "de-DE", "digits", "351 912"),
    pytest.param("11/2/2010 (12) 81 559\u202f599", "es-ES", "telephone",
                 "once de febrero de dos mil diez uno dos ocho uno cinco cinco nueve\u202fcinco nueve nueve",
                 marks=pytest.mark.xfail(
                     strict=True, reason="a date before a bracketed area code keeps the date and the run as written")),
    ("3.5 (1) 12 000 (1) 437 593", "en-GB", "telephone",
     "three five one one two zero zero zero one four three seven five nine three"),
])
def test_a_say_as_reads_as_dev_where_the_round_ten_rules_decide(text, lang, value, expected):
    """Sections 11 and 17.7. Say-as `characters` joins no groups, a kept run is a candidate only under `telephone`,
    and a span is `alone` only when no mark joins it to a digit. Each text reads as dev reads it, on the first pass
    and on both second passes."""
    say_as = SayAs(interpret_as=value)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        once = normalize(text, lang, say_as=say_as)
        assert once == expected
        assert normalize(once, lang, say_as=say_as) == once
        assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "value", "expected"), [
    ("Appelez le 35 910 08416252798 2nd", "fr-FR", "characters", "Appelez le 35 910 08416252798 2nd"),
    ("Tel. [1] ]\xa0+49\xa0074-63", "en-GB", "characters", "Tel. [one] ]\xa0+49\xa0074-63"),
    ("Telefon 1 52 010 - 614 857", "de-AT", "digits", "Telefon eins fünf zwei null eins null - 614 857"),
    ("mail me€665\xa0555\xa0465,73 2x", "fr-FR", "telephone", "mail me€665\xa0555\xa0465,73 2x"),
])
def test_a_say_as_leaves_the_words_that_keep_a_phone_run_as_a_second_pass_sees_them(text, lang, value, expected):
    """Design sections 11 and 4.3. A say-as does not read the phone word and the function words before a kept run, so
    the phone word still names the run on a second pass. It reads a digit group next to the run, because a second
    pass reads that group too. Under `telephone`, the groups that a no-break space joins to a run read with the run
    or not at all."""
    say_as = SayAs(interpret_as=value)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        once = normalize(text, lang, say_as=say_as)
        assert once == expected
        assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "value", "expected"), [
    ("912\xa0345\xa0678", "pt-PT", "telephone", "nove um dois\xa0três quatro cinco\xa0seis sete oito"),
    ("912\u202f345\u202f678", "pt-PT", "telephone", "nove um dois\u202ftrês quatro cinco\u202fseis sete oito"),
    ("0\xa0437\xa0593", "en-GB", "telephone", "zero\xa0four three seven\xa0five nine three"),
    ("0\u202f437\u202f593", "en-GB", "telephone", "zero\u202ffour three seven\u202ffive nine three"),
    ("12\xa0000", "en-GB", "telephone", "one two\xa0zero zero zero"),
    ("12\xa0000", "en-GB", "digits", "one two\xa0zero zero zero"),
    ("12\u202f000", "en-GB", "digits", "one two\u202fzero zero zero"),
])
def test_say_as_telephone_and_digits_read_a_run_that_group_spaces_join(text, lang, value, expected):
    """Design section 17.4 step 3: the markup reads `912 345 678`. Say-as `telephone` and `digits` ask for every
    digit, so no space joins the groups of a run under them, and the run reads group by group as it does when no
    space joins groups."""
    say_as = SayAs(interpret_as=value)
    once = normalize(text, lang, say_as=say_as)
    assert once == expected
    assert normalize(once, lang, say_as=say_as) == once
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang", "expected"), [
    ("Il a payé 12,500 3 fois.", "fr-FR", "Il a payé 12,500 3 fois."),
    ("Der Wert 0,125 3 mal.", "de-DE", "Der Wert 0,125 3 mal."),
    ("Custou 2,500 3 vezes.", "pt-BR", "Custou 2,500 3 vezes."),
    ("Il pèse 1 250,50 2 fois plus.", "fr-FR", "Il pèse mille deux cent cinquante virgule cinquante deux fois plus."),
])
def test_a_fraction_after_a_decimal_comma_may_hold_groups(text, lang, expected):
    """BIPM, SI Brochure, 9th edition, section 5.4.4: digits after the decimal mark may be grouped by three with a
    space, as in `43 279.168 29`. Where the decimal mark of the request is the comma, `12,500 3` is one number,
    which no span reads whole, so it stays as written. `1 250,50 2` is two numbers: a fraction group that another
    group follows has three digits."""
    assert normalize(text, lang) == expected


@pytest.mark.parametrize(("text", "lang"), [
    ("Between 10 000–20 000 people.", "en-GB"), ("Het kost 10 000/20 000 euro.", "nl-NL"),
    ("Es kostet 10 000:20 000 Euro.", "de-DE"), ("Mide 10 000x20 metros.", "es-ES"),
    ("Il faut 1 000 000–2 000 000 personnes.", "de-DE"),
])
def test_any_mark_after_a_group_run_keeps_the_run_as_written(text, lang):
    """Section 4.2: a wrong reading is worse than none. Any character that is no digit and no space joins the digits
    after it to a number grouped with spaces, as the dash of a range does, so no group reads alone."""
    once = normalize(text, lang)
    assert once == text
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("Composez le 1\u00a0800\u00a0555\u00a01234\u00a08 a.m.", "fr-CA"),
    ("Appelez le 01\u00a023\u00a045\u00a067\u00a089\u00a08h", "fr-FR"),
])
def test_a_last_hour_group_after_a_no_break_space_reads_as_after_a_space(text, lang):
    """A no-break space parts two groups of a phone run as a space does, so a last hour group after it leaves the
    run as it does after a space."""
    assert normalize(text, lang).replace("\u00a0", " ") == normalize(text.replace("\u00a0", " "), lang)


@pytest.mark.parametrize(("text", "lang"), [
    ("Uso Potencial, Agricultura, 1:1 000 000.", "es-ES"), ("ÖNORM ISO 10007:2005 06 01", "de-DE"),
])
def test_a_phone_run_after_a_joined_number_that_stays_stays_too(text, lang):
    """A run after a group that a mark joins to the digits before it waits until a span reads that mark. Here no
    span reads `1:1` or `10007:2005`, so a second pass sees the same digits, and the run stays as written."""
    assert normalize(text, lang) == text


@pytest.mark.parametrize(("text", "lang"), [
    ("45 08 08 2x.", "de-AT"),
    ("[52 734 569 (695)]/2 Seite (586:424 07.6 88 038) 2. 1468/094-6321 266 55 6 08 00 3D", "de-AT"),
    ("Nr. 19–66 +34 289 7248 219 014 733-488 3D Tel. 3,8 025/0.93 et", "de-DE"),
    ("n.º 88/82–376 5632-974/7766-9462 155 5 % n.º 251 9594-03 10 066 099 8am unos 331 015-3721 465.5", "es-MX"),
    ("567/1 06 2 1 036 03 1st", "es-US"),
    ("Note [: 3.14 324-367 804 694 (252)] 1st Tél. : 3288.824.728 777 67.18 2e", "fr-CA"),
    ("Appelez le 1.38 260 325 1266.093 192 6 2e 21.29 711 054 0687 811 0191 808 und (0) 79 31 0012.594"
     " 0489 1st", "fr-FR"),
    ("Fax : 3867.306:03\u202f2667.0908\u202f019\u202f529-6523 2x. Tél. 42,018\u202f40\u202f40 und", "fr-FR"),
    ("ISO 0 09 0 151-4-776 2x.", "fr-FR"),
    ("873:155 204 022.9 304.58-264 9.30 telefone 08 25 48 7149.272 417 1st telefone 169.730 aqui.", "pt-BR"),
    ("Fax: 2-330 12.05 +34 035 01 857 220/986 et", "pt-BR"),
    ("ISO . 12.05 0 88 4791 20 2ª Tel. 443.80 12.05 +351 784-749 740 772.5", "pt-BR"),
    ("Tel. 316–146 12.05 026 987-3197 97 78-566/2 Hinweis 9/290 4-30 31 504 037 82 und etwa 746:136 480 7 0.", "de-AT"),
    ("Telefon 702–77 3.14 521-93 928.31 08 70 2ª", "de-DE"),
    ("etwa 60-15/91 33 791 e 405–01 03 02 463 162 5 %", "de-DE"),
    ("86–85 035 097 927 06 722/51 %", "es-MX"),
    ("Note [621–82 0033 018.804 74 54/59/59 (67)] 2e 663/321,96 0576 415.96 79 9939-99 ici.", "fr-CH"),
    ("environ 087:772 1.6.0 082 116.14/1 3D page 257-567.16 2713.5 Tél. : 179–02 0602 078 931 13-309 e", "fr-CH"),
    ("page 6543–593\u202f06.438-66\u202f637\u202f61 8am", "fr-CH"),
    ("cerca de 431–034 0033 072 083 000 5 %", "pt-BR"),
])
def test_a_phone_run_after_an_en_dash_or_an_hour_reads_the_same_on_a_second_pass(text, lang):
    """Section 11. A shorter run after a group that an en dash joins, or after an hour that leaves the run, reads
    on the first pass only when a second pass reads it too."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [("47:892 06 3 74 12 h", "en-GB"), ("884/6 032 320 6 7 aquí.", "en-GB")])
def test_a_waiting_phone_span_holds_no_character(text, lang):
    """A phone span that waits until a span reads the group before it holds no character while it waits, so the
    digits of the run read as a second pass reads them."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("53,(0161) 07 22.34 646", "en-GB"), ("53/(0161) 07 22.34 646", "en-US"), ("53,(0161) 07 22.34 646", "de-DE"),
    ("53:(0161) 07 22.34 646", "es-ES"),
])
def test_a_phone_run_that_a_mark_joins_to_a_number_stays_as_written(text, lang):
    """A phone run that a mark joins to the digits before it stays as written, with the digits and marks glued to it,
    so `53` reads, `(0161) 07` stays, and a second pass sees the same text."""
    spans = {(span.start, span.end): span for span in analyze(text, lang).spans}
    assert spans[0, 2].form is Form.CARDINAL
    once = normalize(text, lang)
    assert "(0161) 07" in once
    assert normalize(once, lang) == once


@pytest.mark.parametrize(("text", "expected"), [
    ("Tel. USD20 444-2428.22.31 2x.", "Tel. zwanzig Dollar 444-2428.22.31 2x."),
    ("Telefon z. B. 260-9726.98.61 8am", "Telefon z. B. 260-9726.98.61 8am"),
])
def test_a_glued_run_stays_as_written_with_the_abbreviation_form_off(text, expected):
    """With `ABBREVIATION` off, `Tel.` and `z. B.` stay as written on both passes. The run, which full stops join to
    other digits and a letter continues, stays as written, and a second pass sees the same text."""
    params = NormalizationParams().without(Form.ABBREVIATION)
    once = normalize(text, "de-AT", params)
    assert once == expected
    assert normalize(once, "de-AT", params) == once


@pytest.mark.parametrize(("text", "lang"), [
    ("n.º 5-n.º 5", "es-US"), ("GPT-4/n.º 5+351 912 345 678/n.º 5", "es-CR"),
    ("GPT-4/n.º 5+351 912 345 678/n.º 5", "es-MX"), ("GPT-4/n.º 5+351 912 345 678/n.º 5", "es-PY"),
    ("3.º 2024. §1-n.º 5", "pt-PT"), ("0.000001/§1.", "fr-DZ"), ("Seite 5-Nr. 3", "de-DE"), ("No. 5-No. 5", "en-US"),
])
def test_a_number_that_a_mark_joins_to_a_number_abbreviation_reads_the_same_on_a_second_pass(text, lang):
    """Section 11. A number abbreviation is a key only before a digit, and a second pass sees the reading of that
    digit, so the abbreviation does not wait on the number before it."""
    once = normalize(text, lang)
    assert normalize(once, lang) == once
