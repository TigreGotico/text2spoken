"""The date and time writers that each tag reads through (`text2spoken.core.parsers`)."""
import sys

import pytest

from text2spoken import normalize


@pytest.mark.parametrize("text, expected", [
    ("Nasceu a 1/3/2026.", "Nasceu a primeiro de março de dois mil e vinte e seis."),
    ("A reunião é às 13:30.", "A reunião é às treze e trinta."),
])
def test_a_pt_pt_date_and_time_read_through_chronologia(text, expected):
    """Cunha & Cintra p. 374 and AO1990 Base XIX, the sources of `locale/pt/spoken.json` of chronologia."""
    assert normalize(text, "pt-PT") == expected
    assert "chronologia.spoken" in sys.modules


def test_a_pt_br_date_reads_through_ovos_date_parser():
    assert normalize("Nasceu em 1/3/2026.", "pt-BR") == "Nasceu em primeiro de março de dois mil e vinte e seis."
