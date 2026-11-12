"""Mutation control of section 13: dropping one entry of each table of a language file fails a row.

The tests run on every language file that the loader finds, and on the stubs of tests/fixtures. A new language
file adds its entries to ENTRIES."""
from dataclasses import replace
from importlib import import_module

import pytest

from tests.conftest import language_names, registry_with_stubs, rows
from text2spoken import NormalizationParams, UnreadFormError, normalize
from text2spoken.core import language as loader
from text2spoken.params import FrozenMap, freeze

EN = import_module("text2spoken.lang.en").LANGUAGE
DELETE = object()
ROW_SILENT = {"symbols"}
"""Tables that only the unread check of strict mode reads, so no row shows a dropped entry."""

# One entry of each table of a language file; DELETE removes a table that holds one value.
EN_ENTRIES = {
    "number_marks": "Latn", "defaults": "clock", "sign_words": "-", "decimal_word": DELETE, "digit_words": "zero", "leads": "#",
    "fraction_names": "2", "idioms": "24/7", "range_word": DELETE, "dimension_marks": "x", "dimension_word": DELETE,
    "operators": "+", "time_words": "at", "day_periods": "pm", "spoken_periods": "pm", "minute_phrases": "0",
    "months": "March", "numeric_date_reading": "full", "currencies": "USD", "percent": "word", "units": "kg",
    "phone_words": "phone", "color_words": "colour", "colors": "ff0000", "titles": "Dr.", "abbreviations": "etc.",
    "number_abbreviations": "No.", "patterns": "expression", "range_marks": "-", "year_words": "in",
    "scales": "million", "sentence_final": "etc.", "ordinal_marks": "th", "year_links": "and",
    "function_words": "the", "list_links": "or", "short_codes": "911", "phone_shapes": "[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}",
    "phone_unit_shapes": "(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+", "phone_kept_shapes": "[1-9][0-9]{0,2}(?: [0-9]{3})+",
    "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})",
    "clock_marks": freeze({"mark": ".", "seconds": False, "needs": "day_period"}),
}
DE_ENTRIES = {
    "number_marks": "Latn", "defaults": "decimal_mark", "sign_words": "-", "decimal_word": DELETE,
    "digit_words": "null", "leads": "#", "half": DELETE, "idioms": "24/7", "range_word": DELETE, "range_marks": "-",
    "time_suffixes": " Uhr",
    "hour_word": DELETE, "time_words": "um", "dimension_marks": "x", "dimension_word": DELETE, "operators": "+",
    "months": "März", "month_numbers": "März", "year_words": "Jahr", "currencies": "EUR", "scales": "Mio.",
    "scale_plurals": "Million", "percent": "word", "units": "kg", "phone_words": "notruf", "short_codes": "112",
    "list_links": "oder", "phone_shapes": "0[1-9][0-9]{1,4} [0-9]+-[0-9]+",
    "phone_unit_shapes": "(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+", "phone_kept_shapes": "[1-9][0-9]{0,2}(?: [0-9]{3})+",
    "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})", "color_words": "Farbe", "titles": "Dr.",
    "abbreviations": "z. B.", "sentence_final": "usw.", "number_abbreviations": "Nr.", "dative_prepositions": "mit",
    "accusative_prepositions": "für", "two_way_prepositions": "in", "determiners": "am", "noun_genders": "auge",
    "noun_endings": ("e", "feminine"), "patterns": "date_day_month", "genitive_prepositions": "wegen",
    "temporal_prepositions": "vor", "time_nouns": "stunde", "accusative_verbs": "kostet",
    "noun_frames": ("ge[^aeiouäöüy]+[aeiouäöüy].*e", "neuter"),
    "clock_marks": freeze({"mark": ":", "seconds": True, "needs": "evidence"}),
}
ENTRIES = {
    "de": DE_ENTRIES,
    "en": EN_ENTRIES,
    "qac": {"number_marks": "Latn", "digit_words": "wa", "sign_words": "-", "leads": "#"},
}
TABLES = [(code, table) for code in language_names() for table in sorted(ENTRIES.get(code, ()))]


def drop(data: FrozenMap, table: str, entry) -> FrozenMap:
    if entry is DELETE:
        return FrozenMap({k: v for k, v in data.items() if k != table})
    value = data[table]
    assert entry in value, f"{entry!r} is not in {table}"
    kept = FrozenMap({k: v for k, v in value.items() if k != entry}) if isinstance(value, FrozenMap) \
        else tuple(v for v in value if v != entry)
    return FrozenMap({**data, table: kept})


@pytest.mark.parametrize("code", language_names())
def test_every_table_has_an_entry_to_drop(code):
    data = registry_with_stubs()[code].data
    assert set(ENTRIES.get(code, ())) | (ROW_SILENT & set(data)) == set(data)


def _fails(row) -> bool:
    try:
        return normalize(row["text"], row["tag"]) != row["expected"]
    except Exception:
        return True


def _failures(monkeypatch, spec) -> list[str]:
    monkeypatch.setattr(loader, "_registry", lambda: dict.fromkeys((spec.code, *spec.serves), spec))
    return [r["id"] for r in rows(spec.code) if _fails(r)]


@pytest.mark.parametrize(("code", "table"), TABLES, ids=[f"{code}-{table}" for code, table in TABLES])
def test_dropping_an_entry_fails_a_row(monkeypatch, code, table):
    spec = registry_with_stubs()[code]
    assert _failures(monkeypatch, spec) == []
    assert _failures(monkeypatch, replace(spec, data=drop(spec.data, table, ENTRIES[code][table])))


def test_dropping_a_symbol_hides_it_from_the_unread_check(monkeypatch):
    strict = NormalizationParams(strict=True)
    with pytest.raises(UnreadFormError):
        normalize("Pay in $ only.", "en", strict)
    monkeypatch.setattr(loader, "_registry", lambda: {"en": replace(EN, data=drop(EN.data, "symbols", "$"))})
    assert normalize("Pay in $ only.", "en", strict) == "Pay in $ only."
