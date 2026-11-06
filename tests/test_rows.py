"""The sentence rows of tests/data: expected values from a cited source, never from a run of the code."""
from importlib.resources import files

import pytest

from tests.conftest import DATA, rows
from text2spoken import Form, normalize, supports

CODES = sorted(p.stem for p in DATA.glob("*.tsv"))
LANG_FILES = sorted(e.name[:-3] for e in files("text2spoken.lang").iterdir()
                    if e.name.endswith(".py") and not e.name.startswith("_"))
ROWS = [row for code in CODES for row in rows(code)]


def test_every_language_file_has_rows():
    assert LANG_FILES == CODES


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_row(row):
    assert normalize(row["text"], row["tag"]) == row["expected"]


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_row_is_idempotent(row):
    once = normalize(row["text"], row["tag"])
    assert normalize(once, row["tag"]) == once


@pytest.mark.parametrize("code", CODES)
def test_rows_cover_every_form_and_variety(code):
    from text2spoken.core.language import language_file

    table = rows(code)
    language = language_file(code)
    # A lexicon row needs params, so test_lexicon.py holds the LEXICON rows.
    assert {r["form"] for r in table} >= {str(f) for f in supports(code).forms - {Form.LEXICON}}
    assert {r["tag"] for r in table} >= {v.tag for v in language.varieties}
    unread = {r["text"] for r in table if r["text"] == r["expected"]}
    for written in ("16:9", "3:16", "#decade", "13/13/2024"):
        assert any(written in text for text in unread), written


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_row_cites_a_source(row):
    assert row["source"].strip() and row["checked_by"].strip()
