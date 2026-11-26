"""Portuguese readings outside the sentence rows: the refusal of ovos-date-parser and the hour symbol at 0 and 12."""
import sys

import pytest
from ovos_date_parser import spoken
from ovos_date_parser.spoken import UnsupportedForm

from text2spoken import (Features, Form, FrozenMap, GrammaticalGender, HintWarning, NormalizationParams, analyze,
                         normalize, render)


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


@pytest.mark.parametrize(("tag", "text", "expected"), [
    ("pt-BR", "Te vejo as 12:00!", "Te vejo as doze horas!"),
    ("pt-PT", "As 12:00 chega.", "As doze horas chega."),
    ("pt-PT", "Abre as 12:00 e fecha as 0:00.", "Abre as doze horas e fecha as zero horas."),
    ("pt-PT", "entre, as 12:00", "entre, as doze horas"),
    ("pt-PT", "sobre  as 0:00", "sobre  a meia-noite"),
    ("pt-BR", "Sem as 12:00 não há almoço.", "Sem o meio-dia não há almoço."),
])
def test_the_article_as_contracts_only_right_after_a_preposition(tag, text, expected):
    """Ciberdúvidas 27390: "A(preposição) + A(S) (artigo definido feminino singular ou plural): ÀS". An "as" with no
    preposition right before it stands for "às", so it stays as written and the time reads the hours it agrees with."""
    assert normalize(text, tag) == expected


@pytest.mark.parametrize(("text", "expected"), [("ÀS 12:00 FECHA.", "Ao meio-dia FECHA."),
                                              ("DAS 12:00 ÀS 14:00", "Do meio-dia ÀS catorze horas")])
def test_a_contracted_word_in_capitals_takes_only_a_first_capital(text, expected):
    """An all-caps "AO" or "DO" would be a two-letter word that the text did not write, and the LETTERS form spells a
    run of two capitals."""
    params = NormalizationParams(forms=NormalizationParams().forms | {Form.LETTERS})
    assert normalize(text, "pt-PT") == normalize(text, "pt-PT", params) == expected


@pytest.mark.parametrize(("tag", "text", "expected"), [
    ("pt-PT", "Mede 1" + "0" * 34 + " km.", "Mede dez mil quintiliões de quilómetros."),
    ("pt-BR", "Mede 1" + "0" * 34 + " km.", "Mede dez decilhões de quilômetros."),
    ("pt-PT", "Custa 1" + "0" * 28 + "1 €.", "Custa cem mil quatriliões e um euros."),
    ("pt-PT", "Mede 1" + "0" * 27 + "1 km.", "Mede dez mil quatriliões e um quilómetros."),
])
def test_a_number_past_28_digits_takes_de_only_on_a_multiple_of_a_million(tag, text, expected):
    """CLDR gives `many`, and so `de`, to a multiple of 1000000 only (`i % 1000000 = 0`): 10**34 takes it, and
    10**29 + 1 and 10**28 + 1 do not."""
    assert normalize(text, tag) == expected


@pytest.mark.parametrize(("tag", "text", "expected"), [
    ("pt-PT", "Falei com a sra.", "Falei com a senhora."),
    ("pt-PT", "Falei com a sra.  \n", "Falei com a senhora.  \n"),
    ("pt-PT", "O Sr.\nSilva chegou.", "O Senhor\nSilva chegou."),
    ("pt-PT", "o dr.\nCosta disse que sim.", "o doutor\nCosta disse que sim."),
    ("pt-PT", "Escrevi ao Prof.\nMarques ontem.", "Escrevi ao Professor\nMarques ontem."),
    ("pt-PT", "Eng.\nSousa", "Engenheiro\nSousa"),
    ("pt-BR", "Conversei com o sr.\nJoão ontem.", "Conversei com o senhor\nJoão ontem."),
    ("pt-PT", "Falei com a sra. Depois saí.", "Falei com a senhora Depois saí."),
])
def test_a_title_keeps_the_full_stop_only_at_the_end_of_the_text(tag, text, expected):
    """When a text ends with an abbreviation, its full stop also ends the sentence (Dicio, "Quando usar ponto
    final"). A title at the end of a line keeps no full stop, because its name can follow on the next line, and a
    title before a capital word comes before a name."""
    assert normalize(text, tag) == expected


@pytest.mark.parametrize(("text", "expected"), [
    ("Horário: abre às 9:00\nHoras extra pagas a dobro.", "Horário: abre às nove horas\nHoras extra pagas a dobro."),
    ("Chega às 16h\n\nHora local: Lisboa.", "Chega às dezasseis horas\n\nHora local: Lisboa."),
    ("Abre às 9:00\thoras.", "Abre às nove horas."),
])
def test_a_time_claims_an_hour_word_after_spaces_or_tabs_only(text, expected):
    """A line break between the time and the word keeps the word, which starts the next line."""
    assert normalize(text, "pt-PT") == expected


@pytest.mark.parametrize(("text", "expected"), [
    ("Comprei 2 casas.", "Comprei duas casas."),
    ("Vi 2 coisas.", "Vi duas coisas."),
    ("Ouvi 2 canções.", "Ouvi duas canções."),
])
def test_a_tugalex_that_fails_to_import_is_no_tugalex(monkeypatch, tmp_path, text, expected):
    """The endings of `gender_suffixes` read the noun when the package is on the path and does not import."""
    (tmp_path / "tugalex").mkdir()
    (tmp_path / "tugalex" / "__init__.py").write_text('raise ImportError("broken install")\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.delitem(sys.modules, "tugalex", raising=False)
    assert normalize(text, "pt-PT") == expected


@pytest.mark.parametrize(("text", "expected"), [
    ("Vi 2 Às 10h.", "Vi dois Às dez horas."),
    ("Comprei 2 Numa loja.", "Comprei dois Numa loja."),
])
def test_a_capital_function_word_gives_no_gender_without_tugalex(monkeypatch, text, expected):
    """The endings of `gender_suffixes` read `Às` as a feminine noun unless the table of function words holds it."""
    monkeypatch.setitem(sys.modules, "tugalex", None)
    assert normalize(text, "pt-PT") == expected


@pytest.mark.parametrize("text, expected", [
    ("Bebi 1,8 L.", "Bebi um vírgula oito litros."),
    ("Bebi 0,5L e 2,25 L", "Bebi zero vírgula cinco litros e dois vírgula vinte e cinco litros"),
])
def test_a_capital_l_after_a_decimal_reads_as_the_litre(text, expected):
    """DL 128/2010, note (a): «Os dois símbolos «l» e «L» podem ser usados para a unidade litro»."""
    assert normalize(text, "pt-PT") == expected


@pytest.mark.parametrize("text", ["O modelo 402 L.", "Lote Q.30 L.6", "A lente f/4L.", "Tamanho L", "tamanho XL",
                                  "Bebi 1,8 Lx"])
def test_a_capital_l_after_a_whole_number_or_in_a_word_reads_no_litre(text):
    assert "litro" not in normalize(text, "pt-PT")
