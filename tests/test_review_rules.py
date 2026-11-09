"""Rules of design sections 2.1, 4.2, 6 and 11 with values worked out by hand, one test for each rule."""
import random
import time
from dataclasses import replace

import pytest

from text2spoken import (Animacy, Features, FrozenMap, InvalidLexiconError, NormalizationParams,
                         ParameterNotHonouredWarning, Token, TokenizerError, UndefinedGrammaticalGender, analyze,
                         effective_params, normalize, supports)
from text2spoken.core import language as loader
from text2spoken.core.language import cldr_locale
from text2spoken.core.numbers import find_numbers
from text2spoken.core.recognizers import SHARED
from text2spoken.core.spans import Span, _inside, _joined, check_features, splits_token
from text2spoken.core.tokens import check_tokens, context_word, fold_digits, join_split_words
from text2spoken.lang.en import LANGUAGE as EN
from text2spoken.params import Form, freeze


def words_of(text: str, clause_end_after: frozenset[str] = frozenset()) -> list[Token]:
    """A tokenizer that splits at spaces and ends the clause after each word in `clause_end_after`."""
    tokens, position = [], 0
    for word in text.split(" "):
        tokens.append(Token(position, position + len(word), word, word in clause_end_after))
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


def test_tokens_that_overlap_by_one_character_raise():
    with pytest.raises(TokenizerError):
        check_tokens((Token(0, 3, "abc"), Token(2, 5, "cde")), "abcde")


def test_a_joined_token_keeps_the_clause_end_of_its_last_part():
    text = "cafe\u0301s"
    joined = join_split_words((Token(0, 4, "cafe"), Token(5, 6, "s", True)), text, frozenset())
    assert joined == (Token(0, 6, text, True),)


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
    assert set(Form) - supports("en").forms == {Form.ROMAN, Form.LETTERS, Form.IDENTIFIER}


def test_cldr_locale_tries_the_script_before_the_region(gendered):
    assert cldr_locale("zh-Hant-TW", {"zh_Hant", "zh_TW", "zh"}, gendered.LANGUAGE) == "zh_Hant"


def test_a_lexicon_entry_that_keeps_its_key_is_allowed_and_protects_the_text():
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"MIX": "MIX", "X5": "X5"})}))
    assert normalize("MIX 5 and X5 now", "en", params) == "MIX five and X5 now"
    assert normalize("MIX 5 and X5 now", "en") == "MIX five and X5 now"
    protected = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"#fff": "#fff"})}))
    assert normalize("the #fff colour", "en", protected) == "the #fff colour"


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
    assert normalize("It is -5 now.", "fr") == "It is -5 now."
    assert "unread written form '-5'" in caplog.text and "sign_words" not in caplog.text


ATOMS = (list("abcxyzABCXYZéñ") + list("0123456789") + list("٠١٢٣٤٥٦٧٨٩") + list("０１２")
         + list("#-+$£€¥%°/:.,;!?()'’×") + ["́", "̈", "‍", "‌", "​", " ", "\r\n", "\t",
                                              " "]
         + ["Dr.", "vs.", "etc.", "No.", "March", "May", "[[", "]]", "am", "pm", "at", "in", "kg", "km/h", "°C",
            "call", "colour", "#fff", "#FF0000", "1/2", "24/7", "14:30", "12/03/2024", "+351", "00", "x", "−", "sub",
            "3rd", "11th", "1984", "2005", "million", "m", "k", "-", "1,000"])


@pytest.mark.parametrize("seed", range(4))
def test_normalize_is_idempotent_and_never_crashes_on_random_text(seed):
    """Section 11: a second pass changes nothing. Random text built from the atoms of each form."""
    rng = random.Random(seed)
    for _ in range(500):
        lang = rng.choice(["en", "en-US", "fr", "xx"])
        text = "".join(rng.choice(ATOMS) for _ in range(rng.randint(1, 30)))
        once = normalize(text, lang)
        assert normalize(once, lang) == once, (text, once)


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
        (Form.MONEY, {"amount": amount, "currency": "USD", "written_symbol": "$", "scale": "million"}),
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


def test_the_numbers_of_a_text_are_kept_for_one_call_only():
    first, second = analyze("It costs $5 at 14:30.", "en").request, analyze("It costs $5 at 14:30.", "en").request
    assert ("numbers", "It costs $5 at 14:30.") in first.memo
    assert second.memo is not first.memo
    assert not hasattr(find_numbers, "cache_info") and not hasattr(fold_digits, "cache_info")


def test_a_digit_next_to_a_span_is_no_joiner():
    """Section 2.1: the joining character is not a space and not a digit."""
    span = Span(0, 2, Form.CARDINAL, FrozenMap())
    text = "ab12"
    assert not _joined(text, span, bytearray(len(text)), [None] * len(text))
    assert _joined("ab/2", span, bytearray(4), [None] * 4)


def test_digits_from_two_digit_sets_stay_as_written_in_a_language_with_no_file():
    assert normalize("Il a １2 chambres.", "fr") == "Il a １2 chambres."


@pytest.mark.parametrize("space", [" ", "\t", "\n"])
def test_a_year_at_the_end_of_the_text_before_a_space_reads(space):
    assert normalize(f"In 1999{space}", "en-GB") == f"In nineteen ninety-nine{space}"


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
    assert normalize("Call the office staff later at 555 1234.", "en-GB") == \
        "Call the office staff later at five hundred and fifty-five one thousand two hundred and thirty-four."


@pytest.mark.parametrize("text", ["Dial 25 and 999.", "Call 25 or 999.", "Call 999 or 112 or 2 friends.",
                                  "Call 0099 1234 5678 now.", "Ring Dial \u0663--0700", "Tel 2, +999.",
                                  "Phone: cell 0099 now020 7946 0018", "Call 911 or 1234567890123456.",
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


def test_a_run_with_a_letter_attached_stays_as_written_only_right_after_a_phone_word():
    assert normalize("Text 020 7946 0018pages now.", "en-GB") == "Text 020 7946 0018pages now."
    assert normalize("Use 020 7946 0018pages now.", "en-GB") == \
        "Use 020 seven thousand nine hundred and forty-six 0018pages now."


def test_the_window_counts_three_content_words_within_eight_words():
    assert normalize("Call the team at the office on 555 1234.", "en-GB") == \
        "Call the team at the office on five five five one two three four."


def test_the_window_names_a_run_that_starts_with_a_zero():
    assert normalize("Call us on 02079460018.", "en-US") == \
        "Call us on zero two zero seven nine four six zero zero one eight."


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
