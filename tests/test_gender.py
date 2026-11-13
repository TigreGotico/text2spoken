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
}
"""The Portuguese rows that need tugalex, read by the `gender_suffixes` of pt.py alone: a noun that no ending
matches takes the masculine default, and `-as` reads feminine."""


@pytest.mark.parametrize("row", rows("pt"), ids=lambda row: row["id"])
def test_portuguese_without_tugalex_reads_by_the_suffix_rules(monkeypatch, row):
    monkeypatch.setitem(sys.modules, "tugalex", None)
    assert normalize(row["text"], row["tag"], row_params(row)) == SUFFIX_READINGS.get(row["id"], row["expected"])
