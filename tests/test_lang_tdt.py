"""Tetun Dili readings outside the sentence rows: text with a tab or a line break, which a row of tests/data/tdt.tsv
cannot hold, text with a space character that a reader cannot see, and a second pass."""
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


def test_two_amounts_with_a_scale_word_between_them_read_the_same_on_a_second_pass():
    """`milhaun` counts the amount before it, so the second amount reads on the first pass (design section 11)."""
    once = normalize("Folin $ 5 milhaun $ 6 milhoens.", "tdt-TL")
    assert "$" not in once
    assert normalize(once, "tdt-TL") == once
