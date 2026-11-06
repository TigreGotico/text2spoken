import csv
from pathlib import Path

import pytest

from text2spoken.core import language

DATA = Path(__file__).parent / "data"


def rows(code: str) -> list[dict]:
    with open(DATA / f"{code}.tsv", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


@pytest.fixture
def gendered(monkeypatch):
    """The registry with the test language `qaa` added beside the shipped files."""
    from tests.fixtures import qaa

    registry = {**language._registry(), "qaa": qaa.LANGUAGE, "qab": qaa.LANGUAGE}
    monkeypatch.setattr(language, "_registry", lambda: registry)
    return qaa
