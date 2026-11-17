"""Say-as (design section 17): the rows of tests/data/say_as, with expected values from a cited source, and the
properties of section 17.7."""
import csv
import logging
import warnings

import pytest

from tests.conftest import DATA, row_params, rows
from text2spoken import (ArgumentTypeError, Form, NormalizationParams, ParameterNotHonouredWarning, SayAs,
                         UnreadFormError, UnsupportedParameterError, analyze, normalize)
from text2spoken.core import say_as as module

with open(DATA / "say_as" / "rows.tsv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f, delimiter="\t"))
BY_ID = {row["id"]: row for row in ROWS}
CODES = sorted(path.stem for path in DATA.glob("*.tsv"))
LANGUAGE_ROWS = [row for code in CODES for row in rows(code)]


def say_as(row: dict) -> SayAs:
    return SayAs(interpret_as=row["interpret_as"], format=row["format"] or None, detail=row["detail"] or None)


def read(row: dict) -> str:
    return normalize(row["text"], row["tag"], say_as=say_as(row))


@pytest.mark.parametrize("row", ROWS, ids=[row["id"] for row in ROWS])
def test_row(row):
    assert read(row) == row["expected"]


@pytest.mark.parametrize("row", ROWS, ids=[row["id"] for row in ROWS])
def test_row_cites_a_source(row):
    assert row["source"].strip() and row["checked_by"].strip()


@pytest.mark.parametrize("row", ROWS, ids=[row["id"] for row in ROWS])
def test_a_second_pass_changes_nothing(row):
    """The frontend reads the whole text again with no say-as, and phoonnx splices the reading into its piece."""
    once = read(row)
    assert normalize(once, row["tag"]) == once
    sentence = f"Room {once} is free."
    assert normalize(sentence, row["tag"]) == sentence


SAY_AS_OF = {Form.CARDINAL: SayAs(interpret_as="cardinal"), Form.DECIMAL: SayAs(interpret_as="cardinal"),
             Form.ORDINAL: SayAs(interpret_as="ordinal"), Form.DATE: SayAs(interpret_as="date"),
             Form.YEAR: SayAs(interpret_as="date", format="y"), Form.TIME: SayAs(interpret_as="time"),
             Form.TELEPHONE: SayAs(interpret_as="telephone"), Form.MONEY: SayAs(interpret_as="currency"),
             Form.MEASURE: SayAs(interpret_as="unit"), Form.FRACTION: SayAs(interpret_as="fraction")}
"""The say-as that names each form with no other format."""


def _one_span_rows() -> list[tuple[dict, SayAs]]:
    """The rows whose plain analysis is one span over the whole text, then the written text of each span of every
    row, as a row of its own, when its plain analysis is one span over it."""
    found, seen = [], set()
    for row in LANGUAGE_ROWS:
        params = row_params(row)
        pieces = [row["text"], *(row["text"][s.start:s.end] for s in analyze(row["text"], row["tag"], params).spans)]
        for number, text in enumerate(pieces):
            if (text, row["tag"], params) in seen:
                continue
            seen.add((text, row["tag"], params))
            spans = analyze(text, row["tag"], params).spans
            if len(spans) == 1 and (spans[0].start, spans[0].end) == (0, len(text)) and spans[0].form in SAY_AS_OF:
                found.append(({**row, "id": f"{row['id']}.{number}", "text": text}, SAY_AS_OF[spans[0].form]))
    return found


ONE_SPAN_ROWS = _one_span_rows()


def test_the_consistency_check_covers_rows_of_every_language():
    assert {row["id"].split("-")[0] for row, _ in ONE_SPAN_ROWS} == set(CODES)


@pytest.mark.parametrize("row,named", ONE_SPAN_ROWS, ids=[row["id"] for row, _ in ONE_SPAN_ROWS])
def test_a_say_as_that_adds_nothing_changes_nothing(row, named):
    """Note, section 1: "if the interpret-as and format attributes do not specify additional or different
    information than what the processor would have inferred automatically, then there should be no change"."""
    params = row_params(row)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        assert normalize(row["text"], row["tag"], params, say_as=named) == normalize(row["text"], row["tag"], params)


DECLINES = [
    ("abc", "en-US", SayAs(interpret_as="cardinal")),
    ("13/13/2024", "en-US", SayAs(interpret_as="date", format="mdy")),
    ("13/12/2024", "en-US", SayAs(interpret_as="date", format="mdy")),
    ("01/02/02", "en-US", SayAs(interpret_as="date", format="dmy")),
    ("13:00", "en-US", SayAs(interpret_as="time", format="hms12")),
    ("3+1/2", "en-US", SayAs(interpret_as="fraction")),
    ("3,5", "pt-PT", SayAs(interpret_as="ordinal")),
    ("é", "en-US", SayAs(interpret_as="characters")),
]
"""Texts that hold no candidate of the form, or only candidates with invalid fields. `13/12/2024` is a valid date
only in day-month order, so it is no `mdy` date, and the two-digit year of `01/02/02` has no reading."""


@pytest.mark.parametrize("text,lang,named", DECLINES, ids=[text for text, _, _ in DECLINES])
def test_a_say_as_with_no_reading_gives_the_plain_reading_and_one_warning(caplog, text, lang, named):
    """SSML 1.1 section 3.1.9: "MUST render the content ... as if the interpret-as attribute were not present" and
    "SHOULD also notify the environment of the mismatch". The test reads the log at WARNING."""
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(text, lang, say_as=named) == normalize(text, lang)
    say_as_records = [r for r in caplog.records if "say-as" in r.getMessage()]
    assert len(say_as_records) == 1
    record = say_as_records[0]
    assert record.levelno == logging.WARNING and record.name == "text2spoken"
    assert repr(named.interpret_as) in record.getMessage() and repr(text) in record.getMessage()
    with pytest.raises(UnreadFormError, match="say-as"):
        normalize(text, lang, NormalizationParams(strict=True), say_as=named)


UNSUPPORTED = [
    ("10 Downing Street", "en-GB", "address"),
    ("Wow", "en-US", "interjection"),
    ("2024-01-02", "en-US", "vxml:date"),
    ("3", "el-GR", "ordinal"),
    ("3", "ar-SA", "digits"),
    ("W3C", "ar-SA", "characters"),
]
"""A value that the core does not read, a prefixed value, and a value whose form the language does not read."""


@pytest.mark.parametrize("text,lang,value", UNSUPPORTED, ids=[f"{lang}-{value}" for _, lang, value in UNSUPPORTED])
def test_an_unsupported_value_gives_the_plain_reading_and_a_warning(text, lang, value):
    with pytest.warns(ParameterNotHonouredWarning, match=value):
        assert normalize(text, lang, say_as=SayAs(interpret_as=value)) == normalize(text, lang)
    with pytest.raises(UnsupportedParameterError, match=value):
        normalize(text, lang, NormalizationParams(strict=True), say_as=SayAs(interpret_as=value))


NOT_HONOURED = [
    ("W3C", "en-US", SayAs(interpret_as="characters", detail="1 2"), "double-u three see"),
    ("W3C", "en-US", SayAs(interpret_as="characters", format="glyphs"), "double-u three see"),
    ("123", "en-US", SayAs(interpret_as="ordinal", format="x"), "one hundred twenty-third"),
    ("1,5", "en-US", SayAs(interpret_as="cardinal", format=";"), "1,5"),
    ("2024", "pt-PT", SayAs(interpret_as="date", format="y"), "dois mil e vinte e quatro"),
    ("00:01", "en-US", SayAs(interpret_as="time", format="hms"), "twelve oh one AM"),
]
"""A format or a detail that the language cannot honour: the say-as reads without it. SSML 1.1 section 3.1.9: "it
MUST render the contained text as if no format value were specified, and SHOULD render it using the interpret-as
value that is specified"."""


@pytest.mark.parametrize("text,lang,named,expected", NOT_HONOURED, ids=[f"{t}-{n}" for t, _, n, _ in NOT_HONOURED])
def test_a_format_or_detail_that_the_language_cannot_honour_is_dropped_with_a_warning(text, lang, named, expected):
    attribute = "format" if named.format is not None else "detail"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert normalize(text, lang, say_as=named) == expected
    honoured = [str(w.message) for w in caught if issubclass(w.category, ParameterNotHonouredWarning)]
    assert len(honoured) == 1 and attribute in honoured[0]
    with pytest.raises(UnsupportedParameterError, match=attribute):
        normalize(text, lang, NormalizationParams(strict=True), say_as=named)


def test_the_value_is_case_folded_and_the_aliases_read():
    assert normalize("123", "en-US", say_as=SayAs(interpret_as=" ORDINAL ")) == "one hundred twenty-third"
    assert normalize("21", "en-US", say_as=SayAs(interpret_as="number")) == "twenty-one"
    for alias in ("spell-out", "letters", "verbatim"):
        assert normalize("W3C", "en-US", say_as=SayAs(interpret_as=alias)) == "double-u three see"


@pytest.mark.parametrize("value", [3, "ordinal", {"interpret_as": "ordinal"}])
def test_a_say_as_of_the_wrong_type_raises(value):
    with pytest.raises(ArgumentTypeError):
        normalize("3", "en", say_as=value)


@pytest.mark.parametrize("fields", [{"interpret_as": None}, {"interpret_as": "date", "format": 1},
                                    {"interpret_as": "date", "detail": b"y"}])
def test_a_field_of_the_wrong_type_raises(fields):
    with pytest.raises(ArgumentTypeError):
        SayAs(**fields)


def test_a_say_as_reads_its_form_whatever_the_params_turn_off():
    """`LETTERS` is off in `DEFAULT_FORMS`, and a caller may turn `DATE` off: the markup names the form."""
    assert normalize("W3C", "en-US", NormalizationParams(), say_as=SayAs(interpret_as="characters")) \
        == "double-u three see"
    assert normalize("01/02/1960", "en-US", NormalizationParams().without(Form.DATE),
                     say_as=SayAs(interpret_as="date", format="dmy")) == "February first nineteen sixty"


def test_the_other_text_reads_as_plain_text():
    """SSML 1.1 section 3.1.9: "this additional text MUST be rendered"."""
    assert normalize("01/02/1960 at 5 PM", "en-US", say_as=SayAs(interpret_as="date", format="dmy")) \
        == "February first nineteen sixty at five PM"


def test_the_analysis_shows_the_say_as_that_the_call_read():
    assert analyze("123", "en-US", say_as=SayAs(interpret_as="Ordinal")).request.say_as.value == "ordinal"
    assert analyze("abc", "en-US", say_as=SayAs(interpret_as="cardinal")).request.say_as is None


def test_a_bare_ordinal_takes_the_default_gender_of_the_params():
    from text2spoken import FrozenMap, GrammaticalGender

    params = NormalizationParams(default_gender=FrozenMap({"pt": GrammaticalGender.FEMININE}))
    assert normalize("3", "pt-PT", params, say_as=SayAs(interpret_as="ordinal")) == "terceira"


@pytest.mark.parametrize("ids,mutate", [
    (("SA01", "SA17"), lambda monkeypatch: monkeypatch.setattr(
        module, "VALUES", {k: v for k, v in module.VALUES.items() if k != "ordinal"})),
    (("SA06", "SA10", "SA13"), lambda monkeypatch: monkeypatch.setattr(
        module.ResolvedSayAs, "recognizers",
        lambda self, language: tuple(r for r in language.recognizers if r.form in self.forms))),
])
def test_the_rows_fail_when_the_say_as_table_or_the_evidence_step_is_removed(monkeypatch, ids, mutate):
    """Mutation control: removing the `ordinal` entry fails SA01 and SA17, and removing the recognizers that take
    the markup as evidence fails SA06, SA10 and SA13."""
    mutate(monkeypatch)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ParameterNotHonouredWarning)
        for row_id in ids:
            assert read(BY_ID[row_id]) != BY_ID[row_id]["expected"], row_id
