"""The ELECTRONIC form: the Portuguese rows of tests/data/electronic, and the rules that no shipped table uses.

The Portuguese rows run on `tests/fixtures/pt_electronic.py`, a language with the address tables of
`text2spoken/lang/_pt_electronic.py` and no other form. The English rows are in tests/data/en.tsv."""
import csv
from dataclasses import replace

import pytest

from tests.conftest import DATA
from tests.fixtures import pt_electronic
from text2spoken import Form, NormalizationParams, UnreadFormError, analyze, normalize
from text2spoken.core import language
from text2spoken.params import FrozenMap, freeze

EN = language.language_file("en")


def electronic_rows(code: str) -> list[dict]:
    with open(DATA / "electronic" / f"{code}.tsv", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


PT_ROWS = electronic_rows("pt")


@pytest.fixture
def pt(monkeypatch):
    monkeypatch.setattr(language, "_registry", lambda: {"pt": pt_electronic.LANGUAGE})


@pytest.fixture
def en_with(monkeypatch):
    """English with its data changed by `changes`, which replace the tables of the same name."""
    def patch(**changes):
        monkeypatch.setattr(language, "_registry", lambda: {"en": replace(EN, data=freeze({**EN.data, **changes}))})
    return patch


@pytest.mark.parametrize("row", PT_ROWS, ids=[r["id"] for r in PT_ROWS])
def test_pt_row(pt, row):
    assert normalize(row["text"], row["tag"]) == row["expected"]


@pytest.mark.parametrize("row", PT_ROWS, ids=[r["id"] for r in PT_ROWS])
def test_pt_row_is_idempotent(pt, row):
    once = normalize(row["text"], row["tag"])
    assert normalize(once, row["tag"]) == once


def test_pt_rows_cover_both_varieties_and_cite_a_source():
    assert {r["tag"] for r in PT_ROWS} == {"pt-PT", "pt-BR"}
    assert all(r["form"] == "electronic" and r["source"].strip() and r["checked_by"].strip() for r in PT_ROWS)


def test_the_fields_of_each_kind():
    spans = analyze("Mail ann@example.com, see https://example.org/a and www.example.net or example.com.",
                    "en").spans
    assert [dict(s.fields) for s in spans] == [
        {"kind": "email", "scheme": "", "address": "ann@example.com"},
        {"kind": "url", "scheme": "https", "address": "example.org/a"},
        {"kind": "url", "scheme": "", "address": "www.example.net"},
        {"kind": "domain", "scheme": "", "address": "example.com"},
    ]


def test_a_known_label_reads_as_the_table_says(en_with):
    en_with(electronic_labels=FrozenMap({"me": "word", "info": "letters"}))
    assert normalize("Mail me@info.com.", "en") == "Mail me at i en ef o dot com."


def test_a_scheme_that_the_table_drops_reads_nothing(en_with):
    en_with(electronic_schemes=FrozenMap({"https": "drop"}))
    assert normalize("See https://example.com now.", "en") == "See example dot com now."


def test_a_scheme_outside_the_table_starts_no_url():
    assert normalize("See gopher://example.com now.", "en") == "See gopher://example.com now."


def test_a_bare_domain_needs_a_top_level_domain_of_the_table(en_with):
    en_with(electronic_tlds=("org",))
    assert normalize("See example.com and example.org.", "en") == "See example.com and example dot org."


def test_an_address_with_no_word_for_a_symbol_raises_in_strict_mode():
    with pytest.raises(UnreadFormError):
        normalize("Go to http://example.com/a%20b now.", "en", NormalizationParams(strict=True))


def test_without_the_form_an_address_stays_as_written():
    text = "Write to ann@example.com or www.example.org."
    assert normalize(text, "en", NormalizationParams().without(Form.ELECTRONIC)) == text


def test_an_address_glued_to_a_letter_stays_as_written():
    for text in ("Write to annè@example.com now.", "Write to ann@exampleé.com now.", "Go to www.câmara.pt now."):
        assert normalize(text, "en") == text
