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


def test_a_letter_of_an_unlisted_script_is_its_own_run():
    assert [script for script, _ in script_runs("ሰላም hello")] == ["Zzzz", "Latn"]


def test_an_empty_map_reads_as_before():
    text = "عندي 25 كتاب"
    assert normalize(text, "apc", NormalizationParams()) == normalize(text, "apc")


@pytest.mark.parametrize("value", [FrozenMap({"Latin": "en"}), FrozenMap({"Latn": ""}), {"Latn": "en"}])
def test_a_bad_map_is_refused(value):
    with pytest.raises(TypeError):
        NormalizationParams(script_languages=value)
