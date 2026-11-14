"""Portuguese readings outside the sentence rows: the refusal of ovos-date-parser and the hour symbol at 0 and 12."""
import pytest
from ovos_date_parser import spoken
from ovos_date_parser.spoken import UnsupportedForm

from text2spoken import (Features, FrozenMap, GrammaticalGender, HintWarning, NormalizationParams, analyze, normalize,
                         render)


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
    stays as written and the time reads the 24-hour form that it agrees with."""
    assert normalize("Abre às § 0:00.", "pt-PT") == "Abre às parágrafo zero horas."


@pytest.mark.parametrize(("text", "expected"), [("às\t0:00", "à\tmeia-noite"), ("às\u00a012:00", "ao\u00a0meio-dia"),
                                              ("das\n0:00", "da\nmeia-noite")])
def test_the_white_space_after_the_contracted_word_stays_as_written(text, expected):
    assert normalize(text, "pt-PT") == expected


def test_a_written_zero_second_is_not_read():
    """Ciberdúvidas 14586 reads the units that the clock writes; a zero second adds no time."""
    assert normalize("às 17 h 34 min 00 s", "pt-PT") == "às dezassete horas e trinta e quatro minutos"


@pytest.mark.parametrize("strict", [False, True])
def test_a_lexicon_entry_on_the_word_keeps_the_time_reading(strict):
    """An identity entry keeps "às" from every other recognizer (design section 11), so the word stays as written and
    the time reads the 24-hour form that the plural article agrees with."""
    params = NormalizationParams(lexicon=FrozenMap({"pt-PT": FrozenMap({"às": "às"})}), strict=strict)
    assert normalize("Abre às 0:00.", "pt-PT", params) == "Abre às zero horas."


@pytest.mark.parametrize(("text", "expected"), [("5(às 0:00)", "cinco(às zero horas)"),
                                              ("Turno 3/das 12:00.", "Turno três/das doze horas.")])
def test_a_word_that_touches_a_number_stays_and_the_time_agrees_with_it(text, expected):
    """A span from the word would wait on the digit that it touches (design section 4.2), so the word stays as written
    and the time reads the 24-hour form."""
    assert normalize(text, "pt-PT") == expected


@pytest.mark.parametrize(("text", "expected"), [("Abre (às 0:00).", "Abre (à meia-noite)."),
                                              ("Chega x às 12:00.", "Chega x ao meio-dia."),
                                              ("À 12:00 almoça.", "Ao meio-dia almoça.")])
def test_the_word_takes_the_article_after_white_space_or_at_the_start(text, expected):
    assert normalize(text, "pt-PT") == expected


def test_a_hint_at_the_digits_of_a_contracted_time_warns_and_the_time_reads():
    """The span of `às 0:00` starts at the word, so a hint keyed at the digits names no span."""
    feminine = Features(gender=GrammaticalGender.FEMININE)
    analysis = analyze("Abre às 0:00.", "pt-PT")
    assert [span.start for span in analysis.spans] == [5]
    assert render(analysis, {5: feminine}) == "Abre à meia-noite."
    with pytest.warns(HintWarning, match="offset 8"):
        assert render(analysis, {8: feminine}) == "Abre à meia-noite."
