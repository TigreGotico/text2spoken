"""The 24-hour reading of Basque, which no row shows because rows use the default params.

Each expected value is the unusual reading of the tables of Euskaltzaindia Araua 203, section 14.3.2, pages 53 to 56
(https://www.euskaltzaindia.eus/dok/arauak/Araua_0203.pdf#page=53), without the word `minutu`, which note 39 lets
the reader leave out, and with the hour alone at minute zero, as note 43 reads `13:00etan` "hamahiruetan"."""
import pytest

from text2spoken import NormalizationParams, UnreadFormError, normalize

TWENTY_FOUR = NormalizationParams(clock="24h")


@pytest.mark.parametrize(("text", "expected"), [
    ("13:00etan", "hamahiruetan"),
    ("14:00ak", "hamalauak"),
    ("03:05ean", "hirurak eta bostean"),
    ("02:03an", "ordu biak eta hiruan"),
    ("01:01ean", "ordu bata eta batean"),
    ("00:08an", "zero ordua eta zortzian"),
    ("24:00etara", "hogeita lauetara"),
])
def test_twenty_four_hour_reading(text, expected):
    assert normalize(text, "eu", TWENTY_FOUR) == expected


def test_midnight_at_minute_zero_has_no_twenty_four_hour_reading():
    """The table gives `00:00etan` the usual reading "(gaueko/gauerdiko) hamabietan" and no unusual reading
    without `minutu`, so the 24-hour reading declines it."""
    assert normalize("00:00etan", "eu") == "gaueko hamabietan"
    with pytest.raises(UnreadFormError):
        normalize("00:00etan", "eu", NormalizationParams(clock="24h", strict=True))
