"""`script_languages` reads each run of a mapped script in its own language."""
import pytest

from text2spoken import normalize
from text2spoken.core.pipeline import script_runs
from text2spoken.params import FrozenMap, NormalizationParams

LATIN_AS_EN = NormalizationParams(script_languages=FrozenMap({"Latn": "en"}))


def test_a_latin_run_in_levantine_text_reads_in_english():
    text = "عندي 25 كتاب. I paid $1.05 and 1999 people came."
    assert normalize(text, "apc", LATIN_AS_EN) == (
        "عندي خمسة وعشرين كتاب. I paid one dollar and five cents and one thousand nine hundred and ninety-nine "
        "people came.")


def test_without_the_map_the_whole_text_reads_in_one_language():
    assert "ألف وتسعمية وتسعة وتسعين people" in normalize("1999 people came.", "apc")


def test_a_number_joins_the_run_of_the_noun_after_it():
    assert script_runs("عندي 25 كتاب and 3 books") == [("Arab", "عندي 25 كتاب"), ("Latn", " and 3 books")]


def test_trailing_marks_join_the_last_run():
    assert script_runs("hello 42!") == [("Latn", "hello 42!")]
    assert script_runs("42") == [(None, "42")]


def test_a_letter_outside_the_table_joins_the_runs_around_it():
    assert script_runs("مرحبا o 1º lugar") == [("Arab", "مرحبا"), ("Latn", " o 1º lugar")]
    assert script_runs("مرحبا 5 µm") == [("Arab", "مرحبا"), ("Latn", " 5 µm")]
    assert script_runs("コーヒー") == [("Kana", "コーヒー")]


def test_a_combining_mark_stays_with_its_letter():
    assert script_runs("e\u0301 مرحبا") == [("Latn", "e\u0301"), ("Arab", " مرحبا")]


def test_an_ordinal_and_a_unit_read_in_the_language_of_their_run():
    assert normalize("مرحبا o 1º lugar", "ar", NormalizationParams(
        script_languages=FrozenMap({"Latn": "pt-PT"}))) == "مرحبا o primeiro lugar"
    assert normalize("مرحبا 5 µm", "ar", LATIN_AS_EN) == "مرحبا five micrometres"


def test_an_empty_map_reads_as_before():
    text = "عندي 25 كتاب"
    assert normalize(text, "apc", NormalizationParams()) == normalize(text, "apc")


@pytest.mark.parametrize("value", [FrozenMap({"Latin": "en"}), FrozenMap({"Latn": ""}), {"Latn": "en"}])
def test_a_bad_map_is_refused(value):
    with pytest.raises(TypeError):
        NormalizationParams(script_languages=value)
