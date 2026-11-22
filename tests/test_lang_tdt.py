"""Tetun Dili readings outside the sentence rows: text with a tab, a line break or a space character other than
U+0020, which a row of tests/data/tdt.tsv cannot hold or a reader cannot see."""
import pytest

from text2spoken import normalize

GAPS = ["\t", "\n", "\u00a0", "\u2009", "\u202f"]


@pytest.mark.parametrize("gap", GAPS)
def test_an_amount_before_a_scale_word_after_a_gap_stays_as_written(gap):
    """The amount of row tdt-030 stays as written with a tab, a line feed, a no-break space, a thin space or a narrow
    no-break space before the scale word."""
    text = f"Orsamentu US$ 1{gap}bilhaun."
    assert normalize(text, "tdt-TL") == text


@pytest.mark.parametrize("gap", GAPS)
def test_an_amount_after_a_scale_word_and_a_gap_stays_as_written(gap):
    """The amount of row tdt-056 stays as written with a tab, a line feed, a no-break space, a thin space or a narrow
    no-break space after the scale word."""
    text = f"Orsamentu tokon{gap}$20."
    assert normalize(text, "tdt-TL") == text


@pytest.mark.parametrize("gap", GAPS)
def test_an_amount_before_another_word_after_a_gap_reads(gap):
    """A gap before a word that is no scale word keeps the reading of the amount."""
    assert normalize(f"Folin $5{gap}ba saúde.", "tdt-TL") == f"Folin cinco dólares{gap}ba saúde."
