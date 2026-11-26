"""Mutation control of section 13: dropping one entry of each table of a language file fails a row.

The tests run on every language file that the loader finds, and on the stubs of tests/fixtures. A new language
file adds its entries to ENTRIES."""
from dataclasses import replace
from importlib import import_module

import pytest

from tests.conftest import language_names, registry_with_stubs, row_params, rows
from text2spoken import NormalizationParams, UnreadFormError, analyze, normalize
from text2spoken.core import language as loader
from text2spoken.params import FrozenMap, freeze

EN = import_module("text2spoken.lang.en").LANGUAGE
DELETE = object()
ROW_SILENT = {"symbols"}
"""Tables that only the unread check of strict mode reads, so no row shows a dropped entry."""
NO_ROW = {"ca": {"leads", "operators"}, "el": {"leads"}, "ja": {"leads"}, "ko": {"leads"}, "tdt": {"defaults"},
          "fr": {"day_part_words", "minute_phrases", "phone_shapes", "phone_unit_shapes", "phone_kept_shapes",
                 "no_phone_shapes"},
          "pt": {"phone_shapes"},
          "it": {"phone_kept_shapes"},
          "nl": {"clock_marks", "phone_shapes", "phone_unit_shapes", "phone_kept_shapes"},
          "zh": {"leads", "scales", "dimension_marks"}}
"""Tables that no row of the language shows: the shared readers need the key and the language leaves it empty
(the phone shape tables, and the Catalan leads and operators), or a row reads it only with a param other than the default (the 12-hour clock and the
phrase style of French, which tests/test_french.py checks), or a default that equals the order which
`dates.resolve` takes with no order (the `DMY` date order of Tetun Dili)."""

# One entry of each table of a language file; DELETE removes a table that holds one value.
EN_ENTRIES = {
    "number_marks": "Latn", "defaults": "clock", "sign_words": "-", "decimal_word": DELETE, "digit_words": "zero", "leads": "#",
    "fraction_names": "2", "idioms": "24/7", "range_word": DELETE, "dimension_marks": "x", "dimension_word": DELETE,
    "operators": "+", "time_words": "at", "day_periods": "pm", "spoken_periods": "pm", "minute_phrases": "0",
    "months": "March", "numeric_date_reading": "full", "currencies": "USD", "currency_symbols": "CHF",
    "percent": "word", "unit_symbols": "kg",
    "phone_words": "phone", "color_words": "colour", "colors": "ff0000", "titles": "Dr.", "abbreviations": "etc.",
    "number_abbreviations": "No.", "patterns": "expression", "range_marks": "-", "year_words": "in",
    "scales": "million", "sentence_final": "etc.", "ordinal_marks": "th", "year_links": "and",
    "function_words": "the", "list_links": "or", "short_codes": "911", "phone_shapes": "[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}",
    "phone_unit_shapes": "(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+", "phone_kept_shapes": "[1-9][0-9]{0,2}(?: [0-9]{3})+",
    "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})",
    "clock_marks": freeze({"mark": ".", "seconds": False, "needs": "day_period"}),
    "electronic_symbols": "@", "letter_names": "w", "electronic_vowels": "i", "electronic_schemes": "https",
    "electronic_tlds": "uk", "letter_vowels": "a", "letter_onsets": "n", "letter_codas": "ng", "letter_runs": "IRS",
    "regnal_titles": "King", "regnal_names": "Henry", "apposition_marks": "[", "roman_nouns": "chapter", "roman_words": "MX",
    "roman_letter_nouns": "chapter", "letter_words": "TO", "unjoined_symbols": "CD", "mixed_word": DELETE,
}
DE_ENTRIES = {
    "number_marks": "Latn", "defaults": "decimal_mark", "sign_words": "-", "decimal_word": DELETE,
    "digit_words": "null", "leads": "#", "half": DELETE, "mixed_suffix": DELETE, "idioms": "24/7",
    "range_word": DELETE, "range_marks": "-",
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
FR_ENTRIES = {
    "number_marks": "Latn", "defaults": "decimal_mark", "sign_words": "-", "decimal_word": DELETE, "digit_words": "zéro",
    "leads": "-", "idioms": "24h/24", "range_word": DELETE, "range_marks": "-", "dimension_marks": "x",
    "dimension_word": DELETE, "time_words": "à", "months": "novembre", "currencies": "EUR", "percent": "word",
    "units": "kg", "titles": "M.", "name_particles": "le", "abbreviations": "etc.", "sentence_final": "etc.",
    "number_abbreviations": "n°", "ordinal_marks": "masculine", "feminine_nouns": "pommes", "patterns": "date_day_month",
    "clock_marks": freeze({"mark": ":", "seconds": True, "needs": "evidence"}),
    "operators": "+", "colors": "ff0000", "color_words": "couleur", "year_words": "en", "year_links": "et",
    "function_words": "il", "phone_words": "composez", "short_codes": "3919", "list_links": "et",
    "phone_reading": DELETE, "roman_headings": "chapitre",
    "roman_names": "Louis", "scales": "M", "day_periods": "pm", "number_gaps": "\u202f", "elision_marks": "'",
    "ordinal_nouns": "page", "scale_nouns": "million", "no_de_words": "dans", "aspirated_h": "haricot",
    "no_de_adjectives": "supplémentaires", "invariable_plurals": "abat-jour", "mute_h": "hallucin", "eliding_y": "yeux",
    "no_elision": "ouistiti", "no_de_participles": "versés", "inverted_pronouns": "ils", "eliding_h": "haïti",
    "imperative_pronouns": "moi", "elided_pronouns": "m",
    "mixed_word": DELETE, "mixed_half": "other",
}
PT_ENTRIES = {
    "number_marks": "Latn", "sign_words": "-", "digit_words": "zero", "leads": "#", "range_word": DELETE,
    "decimal_word": DELETE, "point_word": DELETE, "point_version_words": "versão",
    "point_section_words": "rcl", "bible_books": "gênesis",
    "range_marks": "-", "clock_marks": freeze({"mark": "h", "seconds": False, "needs": "none", "closes_hour": True}),
    "time_words": "às", "time_suffixes": "h", "day_periods": "pm", "dimension_marks": "x", "dimension_word": DELETE,
    "operators": "+", "months": "março", "currencies": "EUR", "currency_symbols": "CHF", "symbol_names": DELETE,
    "scales": "milhões",
    "percent": "word",
    "unit_symbols": "kg", "line_power_symbols": "m", "phone_words": "ligue", "short_codes": "112", "list_links": "ou",
    "phone_unit_shapes": "[29][0-9]{2} [0-9]{3} [0-9]{3}", "phone_kept_shapes": "[1-9][0-9]{0,2}(?: [0-9]{3})+",
    "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})", "function_words": "agora",
    "color_words": "cor", "colors": "000000", "titles": "Dr.", "abbreviations_any_case": "dr.",
    "honorific_before_name": "D.", "abbreviations": "etc.", "sentence_final": "etc.", "number_abbreviations": "n.º",
    "ordinal_marks": "ª", "regnal_titles": "D", "century_words": "século", "determiners": "as", "noun_gender": "Isabel",
    "currency_noun_gender": "córdobas", "two_gender_feminine": "caixas",
    "gender_suffixes": freeze(["a", "feminine"]), "patterns": "date_named", "time_units": "h",
    "time_contractions": "às", "time_article_prepositions": "as",
    "plural_time_verbs": "são", "point_time_words": "pelas", "point_one_words": "à",
    "point_article_prepositions": "as", "amount_words": "vezes",
    "range_articles": "das", "symbols_before_only": "$", "fraction_denominators": "1000",
    "electronic_symbols": "@", "electronic_vowels": "a", "electronic_schemes": "https", "electronic_tlds": "pt",
    "letter_names": "p", "letter_vowels": "o", "letter_onsets": "n", "letter_codas": "l", "letter_runs": "APPO",
    "letter_free_consonants": "b", "roman_nouns": "capítulo", "roman_words": "MC", "letter_words": "DA",
    "roman_letter_nouns": "capítulo", "unjoined_symbols": "ML", "label_nouns": "sala", "plural_labels": "a páginas",
    "hour_periods": "tarde", "number_links": "vírgula", "letter_label_nouns": "vitamina", "year_words": "desde",
    "roman_ordinal_limit": DELETE,
    "mixed_word": DELETE, "mixed_half": "other",
}
AR_ENTRIES = {
    "number_marks": "Arab", "defaults": "decimal_mark", "proclitics": "بـ", "prepositions": "في",
    "semi_prepositions": "بعد", "year_nouns": "سنة", "feminine_plurals": "سيارات", "afila_plurals": "أجهزة", "rank_nouns": "الطابق", "label_nouns": "رقم", "list_marks": "-", "measure_nouns": "بوصة", "percent_words": "في المئة", "uncounted_words": "أو", "sign_words": "-", "leads": "#",
    "decimal_word": DELETE, "fraction_names": "2", "construct_duals": "مئتان", "range_word": DELETE,
    "range_marks": "-", "percent": "word",
    "currencies": "USD", "symbols_after_only": "ريال", "scales": "مليون", "units": "كم", "dimension_marks": "×",
    "clock_marks": freeze({"mark": ":", "seconds": False, "needs": "evidence"}), "time_words": "الساعة",
    "day_periods": "pm", "spoken_periods": "afternoon2", "minute_phrases": "30", "months": "مارس",
    "date_reading": "full", "era_marks": "م", "bce_mark": "ق", "shared_era_marks": "م", "hijri_months": "رمضان", "hijri_marks": "هـ", "short_periods": "م",
}
ES_ENTRIES = {
    "number_marks": "Latn", "defaults": "decimal_mark", "sign_words": "-", "decimal_words": ",", "digit_words": "cero",
    "leads": "-", "fraction_names": "2", "range_word": DELETE, "range_marks": "-", "time_words": "las",
    "clock_marks": freeze({"mark": ":", "seconds": False, "needs": "evidence"}), "time_symbols": " h",
    "day_periods": "pm", "day_period_words": "tarde", "minute_phrases": "30", "months": "marzo", "month_variants": "setiembre",
    "first_of_month": DELETE, "currencies": "EUR", "scales": "millones", "percent": "word", "units": "kg",
    "dimension_marks": "x", "dimension_word": DELETE, "operators": "+", "phone_words": "teléfono",
    "short_codes": "112", "list_links": "o", "phone_shapes": "6[0-9]{2} [0-9]{3} [0-9]{3}",
    "phone_unit_shapes": "(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+", "phone_kept_shapes": "[1-9][0-9]{0,2}(?: [0-9]{3})+",
    "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})", "titles": "Dr.", "abbreviations": "etc.",
    "sentence_final": "etc.", "number_abbreviations": "n.º", "ordinal_marks": ".er", "function_words": "de",
    "year_words": "en", "noun_gender": "día", "gender_suffixes": "a", "tonic_a": "arma", "patterns": "expression",
    "abbreviation_plurals": "vol.", "degree_marks": "º", "ordinal_leads": "el", "ordinal_follows": "de",
    "ordinal_determiners": "el", "feminine_determiners": "la",
    "mixed_word": DELETE, "mixed_half": "other",
}
ENTRIES = {
    "ar": AR_ENTRIES,
    "de": DE_ENTRIES,
    "en": EN_ENTRIES,
    "es": ES_ENTRIES,
    "fr": FR_ENTRIES,
    "pt": PT_ENTRIES,
    "qac": {"number_marks": "Latn", "digit_words": "wa", "sign_words": "-", "leads": "#"},
    "el": {
        "number_marks": "Latn", "sign_words": "-", "decimal_word": DELETE, "case_words": "genitive", "articles": "στις",
        "number_links": "ή", "month_names": "μαΐου", "currencies": "Sc", "percent": "signs", "units": "km",
        "walk_adverbs": "ακόμη", "pronoun_adjectives": "άλλες", "hour_phrases": ("η", "ώρα"), "weekdays": "παρασκευή",
        "months": "Μαρτίου", "half": "feminine", "fraction_names": "4",
        "halves": "2",
    },
    "ja": {"number_marks": "Latn", "sign_words": "-", "currencies": "Sc", "percent": "signs", "units": "kg"},
    "ko": {"number_marks": "Latn", "sign_words": "-", "currencies": "Sc", "percent": "signs", "units": "kg",
           "counters": "개", "counter_followers": "이", "months": "유월"},
    "eu": {
        "number_marks": "Latn", "defaults": "clock", "sign_words": "-", "decimal_word": DELETE, "digit_words": "zero",
        "leads": "-", "case_suffixes": "ko", "time_suffixes": "etan", "time_words": "arratsaldeko",
        "day_periods": "pm", "day_period_words": "15", "hour_words": "1", "months": "martxoaren", "roman_nouns": "urte",
        "code_nouns": "Lege", "ordinal_words": "1",
        "ordinal_suffix": DELETE, "fraction_names": "2", "fraction_word": DELETE, "percent": "word",
        "currencies": "EUR", "units": "kg", "operators": "+", "patterns": "expression", "abbreviations": "etab.",
        "sentence_final": "etab.", "range_marks": "-", "range_followers": "bitartean",
    },
    "it": {
        "number_marks": "Latn", "sign_words": "-", "digit_words": "zero", "decimal_word": DELETE, "leads": "pag. ",
        "percent": "word", "currency_symbols": "CHF", "currencies": "EUR",
        "scales": "milioni", "unit_symbols": "kg", "dimension_marks": "×", "dimension_word": DELETE, "operators": "+",
        "ordinal_marks": "ª", "noun_ordinal_marks": "°", "ordinal_nouns": "piano", "lo_onsets": "z",
        "half_links": "di", "mixed_word": DELETE, "mixed_half": "other", "label_abbreviations": "art.",
        "label_nouns": "pagina", "label_determiners": "il",
        "score_words": "a", "label_counted_nouns": "punto", "title_adjectives": "egregia",
        "adverb_verbs": "fa parte", "preposition_units": "secondo", "masculine_determiners": "lo",
        "kept_day_months": "24/7", "kept_links": "e", "partitive_words": "di", "time_words": "alle",
        "clock_marks": freeze({"mark": ":", "seconds": False, "needs": "evidence"}),
        "time_articles": "alle", "date_words": "il", "of_words": "del", "titles": "Dr.", "feminine_titles": "prof.",
        "feminine_determiners": "la", "possessives": "loro", "abbreviations": "ecc.", "sentence_final": "ecc.",
        "number_abbreviations": "art.", "patterns": "expression", "phone_words": "fax", "short_codes": "112",
        "list_links": "e", "function_words": "il", "phone_shapes": "0[1-9][0-9]{0,2}[ .-][0-9]{3,4} [0-9]{3,4}",
        "phone_unit_shapes": "[(]0[0-9]*[)](?: [0-9]+)+",
        "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})",
    },
    "ca": {
        "number_marks": "Latn", "sign_words": "-", "digit_words": "u", "decimal_word": DELETE, "ordinal_marks": "è",
        "fraction_names": "3", "of_words": "dels", "date_words": "el", "percent": "word", "currency_symbols": "EUR",
        "currencies": "USD", "currency_genders": "EUR", "scales": "milions", "unit_symbols": "kg",
        "dimension_marks": "×", "titles": "Dr.", "abbreviations": "p. ex.", "sentence_final": "etc.",
        "number_abbreviations": "núm.", "symbol_names": "§",
    },
    "nl": {
        "number_marks": "Latn", "sign_words": "-", "digit_words": "nul", "decimal_word": DELETE, "leads": "nr. ",
        "ordinal_marks": "ste", "percent": "word", "currency_symbols": "EUR", "currencies": "JPY", "subunits": "EUR",
        "scales": "miljoen", "unit_symbols": "km", "dimension_marks": "×", "operators": "=", "patterns": "expression",
        "titles": "ing.", "abbreviations": "dr.", "sentence_final": "enz.", "number_abbreviations": "blz.",
        "currency_words": "euro", "year_words": "in het jaar", "mixed_word": DELETE, "mixed_half": "other",
        "phone_words": "fax", "short_codes": "112", "list_links": "of", "function_words": "naar",
        "no_phone_shapes": "(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})",
    },
    "ru": {
        "number_marks": "Latn", "defaults": "decimal_mark", "sign_words": "-", "digit_words": "ноль", "leads": "№ ",
        "range_word": DELETE, "range_marks": "-", "dimension_marks": "×", "dimension_word": DELETE, "time_words": "в",
        "zero_minutes": DELETE, "copulas": "будет", "onset_verbs": "наступило", "date_adverbs": "сегодня",
        "date_particles": "да", "owner_prepositions": "у", "collective_numerals": "2", "pluralia_tantum": "суток",
        "collective_persons": "детей", "months": "марта", "year_noun": "года",
        "whole": DELETE, "fraction_endings": "one", "decimal_denominators": "десят", "governed_cases": "до",
        "case_choices": "в", "plural_endings": "ах",
        "ordinal_endings": "м", "percent": "noun", "currencies": "USD", "scales": "млн", "scale_nouns": "миллион",
        "units": "кг", "titles": "проф.", "abbreviations": "р-н",
    },
    "zh": {
        "number_marks": "Latn", "sign_words": "-", "percent": "word", "fraction_word": DELETE,
        "ordinal_marker": DELETE, "currency_symbols": DELETE, "currencies": "CNY", "unit_symbols": "kg",
        "number_words": "个", "year_words": "公元前", "round_thousand_years": DELETE,
    },
}
FIELD_ONLY = {"electronic_schemes"}
"""Tables that no reading of a row shows. A scheme with `read` reads as its label would, so the entry gives only the
`kind` and `scheme` fields of an address span (section 4.5), which `test_dropping_a_scheme_changes_the_fields` checks."""
TABLES = [(code, table) for code in language_names() for table in sorted(ENTRIES.get(code, ())) if table not in FIELD_ONLY]


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
    assert set(ENTRIES.get(code, ())) | (ROW_SILENT & set(data)) | NO_ROW.get(code, set()) == set(data)


def _fails(row) -> bool:
    try:
        return normalize(row["text"], row["tag"], row_params(row)) != row["expected"]
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


PT = import_module("text2spoken.lang.pt").LANGUAGE
PT_VARIETY_ENTRIES = {("pt-PT", "electronic_symbols"): "_", ("pt-BR", "electronic_symbols"): "#",
                      ("pt-PT", "letter_names"): "w", ("pt-BR", "letter_names"): "w"}
"""One entry of each address table that a Portuguese variety holds."""


@pytest.mark.parametrize(("tag", "table"), sorted(PT_VARIETY_ENTRIES))
def test_dropping_a_pt_variety_entry_fails_a_row(monkeypatch, tag, table):
    entry = PT_VARIETY_ENTRIES[tag, table]
    varieties = tuple(replace(v, data=drop(v.data, table, entry)) if v.tag == tag else v for v in PT.varieties)
    assert _failures(monkeypatch, PT) == []
    assert _failures(monkeypatch, replace(PT, varieties=varieties))


@pytest.mark.parametrize(("spec", "tag"), [(EN, "en"), (PT, "pt-PT")])
def test_dropping_a_scheme_changes_the_fields(monkeypatch, spec, tag):
    text = "See https://example.com now."
    monkeypatch.setattr(loader, "_registry", lambda: dict.fromkeys((spec.code, *spec.serves), spec))
    assert [dict(s.fields) for s in analyze(text, tag).spans] == [
        {"kind": "url", "scheme": "https", "address": "example.com"}]
    dropped = replace(spec, data=drop(spec.data, "electronic_schemes", "https"))
    monkeypatch.setattr(loader, "_registry", lambda: dict.fromkeys((dropped.code, *dropped.serves), dropped))
    assert [dict(s.fields) for s in analyze(text, tag).spans] == [
        {"kind": "run", "scheme": "", "address": "https://example.com"}]
