"""Gender per language (design sections 2.3 and 5.6), on the gendered test language `qaa`, on English, and on
Portuguese without the noun lexicon of tugalex (design section 16)."""
import sys
import warnings

import pytest

from tests.conftest import row_params, rows

from text2spoken import (Features, FrozenMap, GrammaticalGender, NormalizationParams, UndefinedGrammaticalGender,
                         analyze, effective_params, normalize, render)

F, M, N, C = (GrammaticalGender.FEMININE, GrammaticalGender.MASCULINE, GrammaticalGender.NEUTER,
              GrammaticalGender.COMMON)


def params(**genders):
    return NormalizationParams(default_gender=FrozenMap(genders))


def test_no_entry_uses_the_language_default(gendered):
    assert normalize("Tenho 1 livro.", "qaa") == "Tenho um livro."


def test_an_entry_sets_the_gender_of_its_language(gendered):
    assert normalize("Tenho 1 livro e 2 livros.", "qaa", params(qaa=F)) == "Tenho uma livro e duas livros."


@pytest.mark.parametrize("strict", [False, True])
def test_an_entry_with_a_gender_the_language_lacks_raises_in_both_modes(gendered, strict):
    p = NormalizationParams(default_gender=FrozenMap({"qaa": N}), strict=strict)
    with pytest.raises(UndefinedGrammaticalGender) as raised:
        normalize("Tenho 1 livro.", "qaa", p)
    assert raised.value.value == "neuter" and raised.value.defined == {"masculine", "feminine"}


def test_an_entry_for_another_language_never_affects_the_call(gendered):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert normalize("Tenho 1 livro.", "qaa", params(da=C, pt=N)) == "Tenho um livro."


def test_an_entry_for_a_language_with_no_gender_has_no_effect():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert normalize("I have 1 house.", "en", params(en=F)) == "I have one house."
        assert effective_params("en", params(en=F)).default_gender == FrozenMap({"en": F})


def test_the_key_is_the_file_code_so_a_served_code_reads_the_file_entry(gendered):
    assert normalize("Tenho 1 livro.", "qab", params(qaa=F)) == "Tenho uma livro."
    assert normalize("Tenho 1 livro.", "qab", params(qab=F)) == "Tenho um livro."


def test_a_hint_gives_the_gender_of_one_span(gendered):
    analysis = analyze("Tenho 1 livro e 1 carro.", "qaa")
    first = analysis.spans[0].start
    assert render(analysis, {first: Features(gender=F)}) == "Tenho uma livro e um carro."


@pytest.mark.parametrize("strict", [False, True])
def test_a_hint_with_a_gender_the_language_lacks_raises_in_both_modes(gendered, strict):
    analysis = analyze("Tenho 1 livro.", "qaa", NormalizationParams(strict=strict))
    with pytest.raises(UndefinedGrammaticalGender):
        render(analysis, {analysis.spans[0].start: Features(gender=N)})


def test_a_gender_hint_for_a_language_with_no_gender_has_no_effect():
    analysis = analyze("I have 1 house.", "en")
    assert render(analysis, {analysis.spans[0].start: Features(gender=F)}) == "I have one house."


def test_supports_lists_the_genders(gendered):
    from text2spoken import supports

    assert supports("qaa").genders == {M, F} and supports("en").genders == frozenset()


@pytest.mark.parametrize("strict", [False, True])
def test_the_entry_check_reads_the_file_code_for_a_served_code(gendered, strict):
    with pytest.raises(UndefinedGrammaticalGender):
        normalize("Tenho 1 livro.", "qab", NormalizationParams(default_gender=FrozenMap({"qaa": N}), strict=strict))
    assert normalize("Tenho 1 livro.", "qab", params(qab=N)) == "Tenho um livro."


def test_the_noun_after_the_number_decides_before_the_params(gendered):
    assert normalize("Tenho 1 casa.", "qaa") == "Tenho uma casa."
    assert normalize("Tenho 1 casa.", "qaa", params(qaa=M)) == "Tenho uma casa."
    analysis = analyze("Tenho 1 casa.", "qaa")
    assert render(analysis, {analysis.spans[0].start: Features(gender=M)}) == "Tenho um casa."


def test_a_language_with_no_context_words_reads_none(monkeypatch, gendered):
    from dataclasses import replace

    from text2spoken.core import language

    blind = replace(gendered.LANGUAGE, context_words=False)
    monkeypatch.setattr(language, "_registry", lambda: {"qaa": blind})
    gendered.LANGUAGE, original = blind, gendered.LANGUAGE
    try:
        assert normalize("Tenho 1 casa.", "qaa") == "Tenho um casa."
    finally:
        gendered.LANGUAGE = original


SUFFIX_READINGS = {
    "pt-131": "Há dois pontes e um árvore.",
    "pt-132": "Tenho dois mãos e falo duas idiomas.",
    "pt-133": "Júpiter e Saturno são duas planetas.",
    "pt-134": "A região tem dois tribos indígenas.",
    "pt-135": "Os duas artistas e as duas artistas.",
    "pt-336": "A érre tê pê no á érre",
    "pt-339": "A u é no á érre",
    "pt-340": "de MIM ou de tê i",
    "pt-343": "VAMOS i érre",
    "pt-344": "á érre CONDICIONADO",
    "pt-368": "O á érre",
    "pt-371": "Combater a á i dê ésse.",
    "pt-394": "Ligações para a Região Terceiro.",
    "pt-396": "Elizabeth Segundo é a rainha da Inglaterra.",
    "pt-445": "Reda Segundo venceu.",
    "pt-532": "Nesta III Cimeira.",
    "pt-533": "Nesta Quinze edição.",
    "pt-534": "Nesta Vinte e um Bienal.",
    "pt-535": "Deste III Congresso.",
    "pt-760": "Na Sexta dez ponto zero dois abre a loja.",
    "pt-765": "A Indústria quatro ponto zero chegou.",
    "pt-789": "Paguei trezentas ainda ontem.",
    "pt-793": "Comprei duas pra você.",
}
"""The Portuguese rows that need tugalex, read without it. The `gender_suffixes` of pt.py alone give the gender: a
noun that no ending matches takes the masculine default, and `-as` reads feminine. Only `letter_words` makes a run of
capitals read as a word, so `AR`, `IR`, `TI` and `AIDS` read as they read with no word check, and a word of
`letter_words` next to them, as `NO` in pt-336, is written in lower case. A Roman numeral after a capitalised word
takes its gender from a list, never from an ending, and the `noun_gender` table names few nouns and names, so
`Região III`, `Elizabeth II` and `Reda II` read the masculine. A Roman numeral after a singular contraction such as
`nesta` reads as an ordinal only when the `noun_gender` table or tugalex gives the noun after it the gender of the
contraction. The table names none of the nouns of pt-532 to pt-535, so they keep the reading that they have with no
noun. Only tugalex shows that `Sexta` and `Indústria` are words and no names of a product, so the version after them
in pt-760 and pt-765 reads with "ponto". Only tugalex shows that `ainda` and `pra` have no gender, so without it the
ending `-a` makes the number before them feminine in pt-789 and pt-793."""


@pytest.mark.parametrize("row", rows("pt"), ids=lambda row: row["id"])
def test_portuguese_without_tugalex_reads_by_the_suffix_rules(monkeypatch, row):
    monkeypatch.setitem(sys.modules, "tugalex", None)
    assert normalize(row["text"], row["tag"], row_params(row)) == SUFFIX_READINGS.get(row["id"], row["expected"])


def test_portuguese_without_tugalex_takes_the_gender_from_the_endings(monkeypatch):
    """No table names `coisa`, so without tugalex only the ending `-as` of `gender_suffixes` makes the number
    feminine. With tugalex, tugalex runs its own ending rules and the endings of `gender_suffixes` do not run."""
    monkeypatch.setitem(sys.modules, "tugalex", None)
    assert normalize("Comprei 2 coisas.", "pt-PT") == "Comprei duas coisas."
    assert normalize("Comprei 2 coisas.", "pt-BR") == "Comprei duas coisas."
