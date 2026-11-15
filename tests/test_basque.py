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


def test_the_eu_extra_installs_the_basque_speller():
    """`eu.py` reads cardinals with ovos-number-parser, which design section 12 keeps out of the base install, so
    the `eu` extra installs it."""
    lines = [Requirement(line) for line in requires("text2spoken")]
    extra = {line.name for line in lines if line.marker is not None and line.marker.evaluate({"extra": "eu"})}
    assert "ovos-number-parser" in extra


IDEMPOTENT = [
    "II. 1995ean sortu zen.", "XX. 5", "III. 25 urte geroago", "1. 25 lagun etorri ziren.", "2. 3 aukera",
    "XIX. 1850ean", "V. 5 mendean", "MIV. 1907", "Luis XIV. 1715ean hil zen.", "27. 5 orrialdea", "II. 12:00etan",
    "II. % 5", "II. 5 €", "II. etab.", "II. 1 °C", "XX. 1 °C-an", "V. 1 °C", "XIX., XX. eta XXI. mendeetan",
    "XX. eta XXI. mendeetan", "XX. edo XXI. mendean", "II. eta III. 1995ean", "XX. eta 5", "XX. eta XXI. 5",
]


@pytest.mark.parametrize("params", [None, NormalizationParams(clock="24h")], ids=["12h", "24h"])
@pytest.mark.parametrize("text", IDEMPOTENT)
def test_a_roman_numeral_reads_the_same_on_a_second_pass(text, params):
    """Design section 11. A Roman numeral before a number stays as written, because the number reads as lowercase
    words, and a second pass must not read the numeral before them. `1 °C` reads "gradu bat", and `gradu` is a noun
    of the `roman_nouns` table, so a noun before `bat` is no evidence."""
    once = normalize(text, "eu", params)
    assert normalize(once, "eu", params) == once


@pytest.mark.parametrize(("text", "expected"), [
    ("XX. eta XXI. mendeetan", "hogeigarren eta hogeita batgarren mendeetan"),
    ("XX. edo XXI. mendean", "hogeigarren edo hogeita batgarren mendean"),
    ("VIII. gradura", "zortzigarren gradura"),
    ("II. 1995ean sortu zen.", "II. mila bederatziehun eta laurogeita hamabostean sortu zen."),
    ("XX. mende batean", "XX. mende batean"),
])
def test_a_roman_numeral_reads_only_on_evidence(text, expected):
    """Araua 203, section 5, page 27: each ordinal of a coordination may take `-garren`, as in "XIX., XX. eta XXI.
    mendeetan". Page 10 numbers a degree: "Mercalli eskalako VIII. gradura". A year after `II.` gives no evidence
    for the numeral, and a noun before `bat` is the order of a unit reading (page 21), so both stay as written."""
    assert normalize(text, "eu") == expected
