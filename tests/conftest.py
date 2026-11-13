import csv
from importlib import import_module
from pathlib import Path

import pytest

from text2spoken import Form, NormalizationParams
from text2spoken.core import language

DATA = Path(__file__).parent / "data"
FIXTURES = Path(__file__).parent / "fixtures"
STUBS = {"qac": "tests.fixtures.qac"}
"""Stub language files, which the row tests of every language file run on beside the shipped files."""


def rows(code: str) -> list[dict]:
    """The rows of a language file from tests/data, or of a stub from tests/fixtures."""
    path = FIXTURES / f"{code}.tsv" if code in STUBS else DATA / f"{code}.tsv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


LETTERS_ON = NormalizationParams().plus(Form.LETTERS)


def row_params(row: dict) -> NormalizationParams | None:
    """The params of a row. A `LETTERS` row runs with the form on, which is off by default (design section 4.6)."""
    return LETTERS_ON if row["form"] == "letters" else None


def language_names() -> list[str]:
    """The code of each language file that the loader finds, then the code of each stub."""
    return sorted({spec.code for spec in language._registry().values()}) + sorted(STUBS)


def registry_with_stubs() -> dict:
    """The registry of the loader with the stubs added, so that the loader reads a stub as a language file."""
    registry = dict(language._registry())
    for module in STUBS.values():
        spec = import_module(module).LANGUAGE
        registry.update(dict.fromkeys((spec.code, *spec.serves), spec))
    return registry


@pytest.fixture
def stubs(monkeypatch):
    """The registry with the stubs added beside the shipped files."""
    registry = registry_with_stubs()
    monkeypatch.setattr(language, "_registry", lambda: registry)
    return registry


@pytest.fixture
def gendered(monkeypatch):
    """The registry with the test language `qaa` added beside the shipped files."""
    from tests.fixtures import qaa

    registry = {**language._registry(), "qaa": qaa.LANGUAGE, "qab": qaa.LANGUAGE}
    monkeypatch.setattr(language, "_registry", lambda: registry)
    return qaa
