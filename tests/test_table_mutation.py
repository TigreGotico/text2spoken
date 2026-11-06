"""Mutation control of section 13: dropping one entry of each table of a language file fails a row."""
from dataclasses import replace
from importlib import import_module

import pytest

from tests.conftest import rows
from text2spoken import NormalizationParams, UnreadFormError, normalize
from text2spoken.core import language as loader
from text2spoken.params import FrozenMap

EN = import_module("text2spoken.lang.en").LANGUAGE
DELETE = object()

# One entry of each table of en.py; DELETE removes a table that holds one value.
EN_ENTRIES = {
    "number_marks": "Latn", "defaults": "clock", "sign_words": "-", "decimal_word": DELETE, "digit_words": "zero",
    "fraction_names": "2", "idioms": "24/7", "range_word": DELETE, "dimension_marks": "x", "dimension_word": DELETE,
    "operators": "+", "time_words": "at", "day_periods": "pm", "spoken_periods": "pm", "minute_phrases": "0",
    "months": "March", "numeric_date_reading": "full", "currencies": "USD", "percent": "word", "units": "kg",
    "phone_words": "phone", "color_words": "colour", "colors": "ff0000", "titles": "Dr.", "abbreviations": "etc.",
    "number_abbreviations": "No.", "patterns": "ordinal",
}


def drop(data: FrozenMap, table: str, entry) -> FrozenMap:
    if entry is DELETE:
        return FrozenMap({k: v for k, v in data.items() if k != table})
    value = data[table]
    assert entry in value, f"{entry!r} is not in {table}"
    kept = FrozenMap({k: v for k, v in value.items() if k != entry}) if isinstance(value, FrozenMap) \
        else tuple(v for v in value if v != entry)
    return FrozenMap({**data, table: kept})


def test_every_table_has_an_entry_to_drop():
    assert set(EN_ENTRIES) | {"symbols"} == set(EN.data)


def _fails(row) -> bool:
    try:
        return normalize(row["text"], row["tag"]) != row["expected"]
    except Exception:
        return True


def _failures(monkeypatch, spec) -> list[str]:
    monkeypatch.setattr(loader, "_registry", lambda: {"en": spec})
    return [r["id"] for r in rows("en") if _fails(r)]


@pytest.mark.parametrize("table", sorted(EN_ENTRIES))
def test_dropping_an_entry_fails_a_row(monkeypatch, table):
    assert _failures(monkeypatch, EN) == []
    assert _failures(monkeypatch, replace(EN, data=drop(EN.data, table, EN_ENTRIES[table])))


def test_dropping_a_symbol_hides_it_from_the_unread_check(monkeypatch):
    strict = NormalizationParams(strict=True)
    with pytest.raises(UnreadFormError):
        normalize("Pay in $ only.", "en", strict)
    monkeypatch.setattr(loader, "_registry", lambda: {"en": replace(EN, data=drop(EN.data, "symbols", "$"))})
    assert normalize("Pay in $ only.", "en", strict) == "Pay in $ only."
