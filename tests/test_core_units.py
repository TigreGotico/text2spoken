"""Core parts with values worked out by hand: numbers, dates, times, Roman numerals, token splits, regexes."""
import ast
import importlib
import pkgutil
import re
import types
from dataclasses import fields
from pathlib import Path

import pytest

import text2spoken
from tests.contract import check_pattern
from text2spoken.core import color, dates, numbers, roman, times
from text2spoken import Features, GrammaticalGender, NormalizationParams, analyze, supports
from text2spoken.core.spans import Span, splits_token
from text2spoken.core.tokens import Token
from text2spoken.lang.en import LANGUAGE as EN
from text2spoken.params import Form, FrozenMap

EN_MARKS = (("Latn", ".", ","),)


@pytest.mark.parametrize("text,expected", [
    ("1,234.5", [("", "1234", "5")]), ("-5", [("-", "5", None)]), ("−5", [("-", "5", None)]), (".5", [("", "", "5")]),
    ("3-2", [("", "3", None), ("", "2", None)]), ("1,23", []), ("1.2.3", []), ("16:9", []), ("12,345,678", [("", "12345678", None)]),
    ("x5", [("", "5", None)]), ("٤٥", [("", "45", None)]),
])
def test_numbers_parse_by_the_declared_marks(text, expected):
    found = numbers.find_numbers(text, EN_MARKS)
    assert [(n.sign, n.integer, n.fraction) for n in found] == expected


FR_MARKS = (("Latn", ",.", " \u00a0\u202f'\u2019"),)


@pytest.mark.parametrize("text,expected", [
    ("1 234,5", [("", "1234", "5")]), ("3,5", [("", "3", "5")]), ("3.5", [("", "3", "5")]),
    ("12\u00a0345", [("", "12345", None)]), ("12\u202f345", [("", "12345", None)]),
    ("1'000", [("", "1000", None)]), ("1\u2019000", [("", "1000", None)]), ("1 000 000", [("", "1000000", None)]),
    ("1.000.000", [("", "1000000", None)]), ("1.234,5", [("", "1234", "5")]), ("1 234.5", [("", "1234", "5")]),
    ("-3,5", [("-", "3", "5")]), (",5", [("", "", "5")]), (".5", [("", "", "5")]),
    ("1.500", []), ("10.000", []), ("1.5.2", []), ("1,5,2", []), ("16:9", []),
    ("12 34", [("", "12", None), ("", "34", None)]), ("70 90 80", [("", "70", None), ("", "90", None), ("", "80", None)]),
    ("1 000 5", [("", "1000", None), ("", "5", None)]), ("1234 567", [("", "1234", None), ("", "567", None)]),
    ("5 123 6", [("", "5123", None), ("", "6", None)]),
])
def test_several_decimal_and_group_marks_read_one_number_or_none(text, expected):
    found = numbers.find_numbers(text, FR_MARKS)
    assert [(n.sign, n.integer, n.fraction) for n in found] == expected


def test_a_lone_other_decimal_mark_with_three_digits_is_neither_decimal_nor_group():
    assert numbers.find_numbers("3.141", FR_MARKS) == ()
    assert [n.fraction for n in numbers.find_numbers("3.14", FR_MARKS)] == ["14"]
    assert numbers.find_numbers("3.1415", FR_MARKS)[0].fraction == "1415"


def test_a_space_group_leaves_a_quote_before_a_number_alone():
    assert [(n.integer, n.start) for n in numbers.find_numbers("dit '5' fois", FR_MARKS)] == [("5", 5)]


def test_the_entry_of_the_decimal_mark_starts_with_it_and_a_space_is_no_token_mark():
    data = FrozenMap({"number_marks": FrozenMap({"Latn": ({"decimal": ".,", "group": " '"}, {"decimal": ",.", "group": " '"})})})
    assert numbers.number_marks(data, ",") == (("Latn", ",.", " '"),)
    assert numbers.number_marks(data, None) == (("Latn", ".,", " '"),)
    assert numbers.declared_marks(data) == {".", ",", "'"}


def test_an_undeclared_script_reads_integers_only():
    assert [(n.integer, n.fraction) for n in numbers.find_numbers("١٢٫٥", EN_MARKS)] == [("12", None), ("5", None)]
    assert [(n.integer, n.fraction) for n in numbers.find_numbers("١٢٫٥", (("Arab", "٫", "٬"),))] == [("12", "5")]


@pytest.mark.parametrize("fields,order,expected", [
    (("12", "03", "2024"), "DMY", (2024, 3, 12, "DMY")), (("12", "03", "2024"), "MDY", (2024, 12, 3, "MDY")),
    (("25", "12", "1999"), "MDY", (1999, 12, 25, "DMY")), (("12", "25", "1999"), "DMY", (1999, 12, 25, "MDY")),
    (("2024", "02", "29"), "DMY", (2024, 2, 29, "YMD")), (("2023", "02", "29"), "DMY", None),
    (("13", "13", "2024"), "DMY", None), (("12", "03", "24"), "DMY", None),
])
def test_date_resolution(fields, order, expected):
    assert dates.resolve(fields, order) == expected


@pytest.mark.parametrize("parts,expected", [(("14", "30", None), (14, 30, None)), (("9", "05", "07"), (9, 5, 7)),
                                            (("24", "00", None), None), (("16", "9", None), None),
                                            (("12", "60", None), None), (("1", "00", "60"), None)])
def test_clock_fields(parts, expected):
    assert times.clock_fields(*parts) == expected


def test_twelve_hour_face():
    assert [times.twelve_hour(h) for h in (0, 1, 12, 13, 23)] == [12, 1, 12, 1, 11]


@pytest.mark.parametrize("numeral,value", [("XIV", 14), ("MCMXCIX", 1999), ("MMMCMXCIX", 3999), ("IIII", None),
                                           ("IC", None), ("xiv", None), ("", None)])
def test_roman_value(numeral, value):
    assert roman.value(numeral) == value


def test_a_span_may_split_a_token_only_where_a_digit_meets_a_non_digit_or_next_to_punctuation():
    text = "MIXER 2024ko"
    tokens = (Token(0, 5, "MIXER"), Token(6, 12, "2024ko"))
    assert splits_token(Span(0, 3, Form.ROMAN, FrozenMap()), tokens, text)
    assert not splits_token(Span(6, 10, Form.YEAR, FrozenMap()), tokens, text)
    assert splits_token(Span(6, 8, Form.CARDINAL, FrozenMap()), tokens, text)
    assert splits_token(Span(8, 12, Form.CARDINAL, FrozenMap()), tokens, text)
    lexicon = "l'ACME"
    assert not splits_token(Span(2, 6, Form.LEXICON, FrozenMap()), (Token(0, 6, lexicon),), lexicon)
    assert not splits_token(Span(2, 6, Form.CARDINAL, FrozenMap()), (Token(0, 6, lexicon),), lexicon)
    dashed = "ACME-based"
    assert not splits_token(Span(0, 4, Form.LEXICON, FrozenMap()), (Token(0, 10, dashed),), dashed)
    assert splits_token(Span(0, 3, Form.LEXICON, FrozenMap()), (Token(0, 10, dashed),), dashed)


def _patterns():
    package = text2spoken.__path__
    for module in pkgutil.walk_packages(package, "text2spoken."):
        if module.name.endswith("__main__"):
            continue
        loaded = importlib.import_module(module.name)
        for name, value in vars(loaded).items():
            if isinstance(value, re.Pattern):
                yield f"{module.name}.{name}", value


@pytest.mark.parametrize("name,pattern", list(_patterns()))
def test_every_compiled_regex_of_the_package_is_portable(name, pattern):
    check_pattern(pattern.pattern)
    assert pattern.flags == re.UNICODE, f"{name} compiles with flags"


def _literal_patterns(node):
    """The whole string constants of a `re.compile` argument, through `x if c else y` and `x or y`."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.value
    elif isinstance(node, ast.IfExp):
        yield from _literal_patterns(node.body)
        yield from _literal_patterns(node.orelse)
    elif isinstance(node, ast.BoolOp):
        for value in node.values:
            yield from _literal_patterns(value)


def test_every_literal_regex_that_the_package_compiles_is_portable():
    """Each string literal passed to `re.compile` anywhere in the package, also one compiled inside a function."""
    found = []
    for path in sorted(Path(text2spoken.__file__).parent.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "compile"
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and node.args):
                found += [(f"{path.name}:{node.lineno}", pattern) for pattern in _literal_patterns(node.args[0])]
    patterns = {pattern for _, pattern in found}
    assert color._HEX.pattern in patterns and ", " in patterns
    for where, pattern in found:
        try:
            check_pattern(pattern)
        except AssertionError as error:
            raise AssertionError(f"{where}: {error}") from None


def test_the_package_namespace_is_exactly_all():
    public = {name for name in dir(text2spoken)
              if not name.startswith("__") and not isinstance(getattr(text2spoken, name), types.ModuleType)}
    assert public == set(text2spoken.__all__) and len(text2spoken.__all__) == len(public)


@pytest.mark.parametrize("value,positional", [
    (NormalizationParams(clock="24h", strict=True), 0), (Features(gender=GrammaticalGender.FEMININE, case="dative"), 0),
    (Token(0, 1, "a", clause_end=True), 3), (Span(0, 1, Form.CARDINAL, FrozenMap({"digits": "1"}), trail="."), 4),
    (analyze("Gate 7 opens.", "en"), 0), (supports("en-GB"), 0), (EN, 0),
], ids=lambda value: type(value).__name__ if not isinstance(value, int) else str(value))
def test_a_public_dataclass_takes_its_later_fields_by_keyword(value, positional):
    """A new field never shifts a positional caller: past the first `positional` fields, each field is a keyword."""
    names = [field.name for field in fields(value)]
    values = [getattr(value, name) for name in names]
    kind = type(value)
    with pytest.raises(TypeError):
        kind(*values)
    rebuilt = kind(*values[:positional], **dict(zip(names[positional:], values[positional:])))
    assert all(getattr(rebuilt, name) == getattr(value, name) for name in names)


def test_a_lead_missing_from_the_table_stays_written(monkeypatch):
    from dataclasses import replace

    from text2spoken import normalize
    from text2spoken.core import language
    from text2spoken.lang import en

    data = FrozenMap({**en.LANGUAGE.data, "leads": FrozenMap({"-": ""})})
    monkeypatch.setattr(language, "_registry", lambda: {"en": replace(en.LANGUAGE, data=data)})
    assert normalize("Room #20 is shut.", "en-GB") == "Room #20 is shut."
    assert normalize("The sub-23 team won.", "en-GB") == "The sub twenty-three team won."


def test_a_lead_after_a_digit_is_no_lead():
    from text2spoken import NormalizationParams, normalize

    assert normalize("It was 3-2.", "en", NormalizationParams().only(Form.CARDINAL)) == "It was 3-2."


def test_a_lead_with_words_after_a_letter_is_no_lead():
    from text2spoken import normalize

    assert normalize("Play C#5 now.", "en-GB") == "Play C#5 now."
    assert normalize("Play #5 now.", "en-GB") == "Play number five now."


@pytest.mark.parametrize("text,spans", [("Use 00442079460018 now.", 1), ("Use 00992079460018 now.", 0),
                                        ("Dial 0099 20 7946 0018 now.", 1)])
def test_a_number_written_with_00_needs_a_country_code_or_a_phone_word(text, spans):
    from text2spoken import analyze

    assert sum(span.form is Form.TELEPHONE for span in analyze(text, "en-GB").spans) == spans


def test_a_proclitic_wins_over_a_lead(monkeypatch):
    from dataclasses import replace

    from text2spoken import normalize
    from text2spoken.core import language
    from text2spoken.lang import en

    data = FrozenMap({**en.LANGUAGE.data, "proclitics": ("ab-",)})
    monkeypatch.setattr(language, "_registry", lambda: {"en": replace(en.LANGUAGE, data=data)})
    assert normalize("Go ab-5 now.", "en-GB") == "Go ab-five now."
    assert normalize("Go cd-5 now.", "en-GB") == "Go cd five now."


@pytest.mark.parametrize("gap", ["", " ", " ", " "])
def test_a_narrow_no_break_space_gap_joins_a_number_to_its_symbol_and_unit(gap):
    from text2spoken import normalize

    assert normalize(f"Take 50{gap}% of 5{gap}kg.", "en-US") == "Take fifty percent of five kilograms."


@pytest.mark.parametrize("text,spoken", [("Pay -5 $ now.", "Pay minus five dollars now."),
                                         ("Pay +5 $ now.", "Pay plus five dollars now."),
                                         ("Pay -$5 now.", "Pay minus five dollars now.")])
def test_a_sign_before_a_number_with_its_symbol_after_stays_in_the_amount(text, spoken):
    from text2spoken import normalize

    assert normalize(text, "en-US") == spoken


@pytest.mark.parametrize("text,spoken", [
    ("Your next alarm is set for 7:30 tomorrow morning.", "Your next alarm is set for seven thirty tomorrow morning."),
    ("Set an alarm for 6:05 tonight.", "Set an alarm for six oh five tonight."),
    ("The meeting is for 3:15 this afternoon.", "The meeting is for three fifteen this afternoon."),
    ("Be there by 17:45.", "Be there by five forty-five PM."),
    ("Be there by 5:30 sharp.", "Be there by five thirty sharp."),
    ("Bake for 1:30.", "Bake for 1:30."),
    ("Practice for 0:45.", "Practice for 0:45."),
    ("Wait for 2:00.", "Wait for 2:00."),
    ("He ran for 1:23:45.", "He ran for 1:23:45."),
    ("Be there by 5:45:10.", "Be there by 5:45:10."),
    ("The score was 7:30.", "The score was 7:30."),
    ("It is set for 16:9.", "It is set for 16:9."),
])
def test_a_weak_time_word_is_evidence_for_hours_and_minutes_only_and_for_needs_a_day_part_cue(text, spoken):
    from text2spoken import normalize

    assert normalize(text, "en-GB") == spoken


@pytest.mark.parametrize("before", ["", " ", " ", " ", "(", "\n", "à "])
@pytest.mark.parametrize("mark", [",", "."])
def test_a_leading_decimal_mark_reads_after_a_space_a_bracket_or_at_the_start(before, mark):
    found = numbers.find_numbers(f"{before}{mark}5", FR_MARKS)
    assert [(n.integer, n.fraction, n.start) for n in found] == [("", "5", len(before))]


@pytest.mark.parametrize("text", ["1.,5", "1,.5", "x,5", "a.5", "1.5.,5"])
def test_a_mark_that_continues_a_cluster_or_a_word_is_no_leading_mark(text):
    assert all(n.integer for n in numbers.find_numbers(text, FR_MARKS))


@pytest.mark.parametrize("tag,text,spoken", [
    ("fr", "Il a ,5 de moyenne.", "Il a zéro virgule cinq de moyenne."),
    ("fr", "Il a .5 de moyenne.", "Il a zéro virgule cinq de moyenne."),
    ("fr", f"Il a{chr(0xa0)},5 de moyenne.", f"Il a{chr(0xa0)}zéro virgule cinq de moyenne."),
    ("fr", f"Il a{chr(0x202f)},5 de moyenne.", f"Il a{chr(0x202f)}zéro virgule cinq de moyenne."),
    ("fr", "(,5)", "(zéro virgule cinq)"), ("fr", ",5", "zéro virgule cinq"),
    ("en-US", "It is .5 now.", "It is zero point five now."),
])
def test_a_leading_decimal_mark_reads_in_a_sentence(tag, text, spoken):
    from text2spoken import normalize

    assert normalize(text, tag) == spoken
