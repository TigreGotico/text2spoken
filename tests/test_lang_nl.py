"""Dutch readings outside the sentence rows: text with a line break or a tab, which a row of tests/data/nl.tsv
cannot hold."""
import pytest

from text2spoken import normalize


@pytest.mark.parametrize("gap", ["\n", "\r\n", "\t"])
def test_a_line_break_or_a_tab_after_the_year_words_gives_a_count(gap):
    """A year needs one space, one no-break space or one narrow no-break space after `in het jaar`, so the number
    reads as the count of row nl-161."""
    text = f"In het jaar{gap}1450 kwamen er mensen."
    assert normalize(text, "nl-NL") == f"In het jaar{gap}duizend vierhonderdvijftig kwamen er mensen."
