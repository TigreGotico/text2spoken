"""Core parts with values worked out by hand: numbers, dates, times, Roman numerals, token splits, regexes."""
import importlib
import pkgutil
import re

import pytest

import text2spoken
from tests.contract import check_pattern
from text2spoken.core import dates, numbers, roman, times
from text2spoken.core.spans import Span, splits_token
from text2spoken.core.tokens import Token
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


def test_a_span_may_split_a_token_only_where_a_digit_meets_a_non_digit():
    text = "MIXER 2024ko"
    tokens = (Token(0, 5, "MIXER"), Token(6, 12, "2024ko"))
    assert splits_token(Span(0, 3, Form.ROMAN, FrozenMap()), tokens, text)
    assert not splits_token(Span(6, 10, Form.YEAR, FrozenMap()), tokens, text)
    lexicon = "l'ACME"
    assert not splits_token(Span(2, 6, Form.LEXICON, FrozenMap()), (Token(0, 6, lexicon),), lexicon)
    assert splits_token(Span(2, 6, Form.CARDINAL, FrozenMap()), (Token(0, 6, lexicon),), lexicon)


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
