"""Portuguese readings outside the sentence rows: the refusal of ovos-date-parser and the hour symbol at 0 and 12."""
import pytest
from ovos_date_parser import spoken
from ovos_date_parser.spoken import UnsupportedForm

from text2spoken import normalize


def _refuse(error):
    def refuse(lang, *args, **kwargs):
        raise error
    return refuse


@pytest.mark.parametrize("error", [UnsupportedForm("pt-PT", "date", "this language"), ValueError("no such day")])
def test_a_date_the_parser_refuses_stays_as_written(monkeypatch, error):
    monkeypatch.setattr(spoken, "spoken_date", _refuse(error))
    assert normalize("Nasceu em 1/5/2024 às 9h.", "pt-PT") == "Nasceu em 1/5/2024 às nove horas."


@pytest.mark.parametrize("error", [UnsupportedForm("pt-BR", "time", "the digits style"), ValueError("no such hour")])
@pytest.mark.parametrize("text", ["Chego às 14:30 amanhã.", "Chego às 0:00 amanhã."])
def test_a_time_the_parser_refuses_stays_as_written(monkeypatch, error, text):
    monkeypatch.setattr(spoken, "spoken_time", _refuse(error))
    assert normalize(f"{text} 1/5/2024", "pt-BR") == f"{text} primeiro de maio de dois mil e vinte e quatro"


@pytest.mark.parametrize(("tag", "text", "expected"), [
    ("pt-PT", "às 0h", "às zero horas"),
    ("pt-BR", "às 0h", "às zero hora"),
    ("pt-PT", "às 12h", "às doze horas"),
    ("pt-BR", "das 12h às 13h", "das doze horas às treze horas"),
    ("pt-PT", "às 0:30", "às zero e trinta"),
])
def test_a_time_with_the_hour_symbol_or_minutes_keeps_its_article(tag, text, expected):
    """The ruling keeps the 24-hour reading of a written `0h` and `12h` ("zero hora" in pt-BR, after Dicio, "Zero
    grau ou zero graus"), so the article before it stays."""
    assert normalize(text, tag) == expected


def test_a_character_between_the_article_and_the_time_stays_read():
    """The `§` reads by its name (Priberam, "parágrafo": "Sinal desta divisão (§)."), so the article before it
    stays as written."""
    assert normalize("Abre às § 0:00.", "pt-PT") == "Abre às parágrafo meia-noite."
