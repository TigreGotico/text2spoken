"""The 24-hour reading of Basque, which no row shows because rows use the default params, and the install that
reads it.

Each expected value is the unusual reading of the tables of Euskaltzaindia Araua 203, section 14.3.2, pages 53 to 56
(https://www.euskaltzaindia.eus/dok/arauak/Araua_0203.pdf#page=53), without the word `minutu`, which note 39 lets
the reader leave out, and with the hour alone at minute zero, as note 43 reads `13:00etan` "hamahiruetan". Zero
hours take the singular, "zero ordua" (page 52), and Araua 35, page 184, reads `00:00` as "Zero orduan / orenean"
(https://www.euskaltzaindia.eus/dok/arauak/Araua_0035.pdf#page=4)."""
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement

from text2spoken import NormalizationParams, normalize

TWENTY_FOUR = NormalizationParams(clock="24h", strict=True)


@pytest.mark.parametrize(("text", "expected"), [
    ("13:00etan", "hamahiruetan"),
    ("14:00ak", "hamalauak"),
    ("03:05ean", "hirurak eta bostean"),
    ("02:03an", "ordu biak eta hiruan"),
    ("01:01ean", "ordu bata eta batean"),
    ("00:08an", "zero ordua eta zortzian"),
    ("24:00etara", "hogeita lauetara"),
    ("00:00etan", "zero orduan"),
    ("00:00ak", "zero ordua"),
    ("7:10 p.m.", "hemeretziak eta hamar."),
])
def test_twenty_four_hour_reading(text, expected):
    assert normalize(text, "eu", TWENTY_FOUR) == expected
    assert normalize(expected, "eu", TWENTY_FOUR) == expected


def test_the_usual_reading_of_midnight_names_the_night():
    """Araua 203, page 55: `00:00etan` reads "(gaueko/gauerdiko) hamabietan"."""
    assert normalize("00:00etan", "eu") == "gaueko hamabietan"


def test_a_base_install_holds_the_basque_speller():
    """Design section 12: the first language file that calls ovos-number-parser adds it back as a dependency, so a
    Basque voice reads a digit with no extra."""
    base = {Requirement(line).name for line in requires("text2spoken") if Requirement(line).marker is None}
    assert "ovos-number-parser" in base
