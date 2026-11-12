"""Russian hints and the default gender. The expected words come from the cited grammar, not from a run."""
import pytest

from text2spoken import Features, FrozenMap, GrammaticalGender, NormalizationParams, analyze, normalize, render


def test_a_case_hint_reads_a_date_in_the_genitive():
    # Розенталь 1985 § 94: "выедет первого декабря".
    analysis = analyze("Он выедет 1 декабря.", "ru-RU")
    assert render(analysis, {10: Features(case="genitive")}) == "Он выедет первого декабря."


def test_a_gender_hint_wins_over_the_noun_after_the_number():
    # Грамматика-80 § 1368: "одна", "одно" are the forms of the feminine and the neuter.
    analysis = analyze("Это 1 мнение.", "ru-RU")
    assert render(analysis, {4: Features(gender=GrammaticalGender.FEMININE)}) == "Это одна мнение."


def test_the_default_gender_reads_a_number_with_no_noun():
    params = NormalizationParams(default_gender=FrozenMap({"ru": GrammaticalGender.FEMININE}))
    assert normalize("Итого: 2.", "ru-RU", params) == "Итого: две."
    assert normalize("Итого: 2.", "ru-RU") == "Итого: два."


@pytest.mark.parametrize("text", ["1 мая 2024,2 мая", "Было 1 мая 2024,2 мая", "Было 1 мая,2 мая",
                                  "«Сегодня 1 мая»,2 мая"])
def test_a_second_pass_reads_a_date_before_a_glued_mark_the_same_way(text):
    once = normalize(text, "ru-RU")
    assert normalize(once, "ru-RU") == once
