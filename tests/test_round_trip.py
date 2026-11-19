"""Round trip of section 13: ovos-number-parser parses each English cardinal back to its value.

This proves self-consistency only. It never replaces a cited row.
"""
import pytest
from ovos_number_parser import extract_number

from text2spoken import normalize

VALUES = [0, 1, 7, 13, 21, 99, 101, 115, 999, 1000, 1001, 1234, 2024, 10_000, 65_536, 999_999, 1_000_000, 1_234_567]


@pytest.mark.parametrize("tag", ["en-GB", "en-US"])
@pytest.mark.parametrize("value", VALUES)
def test_cardinal_round_trip(tag, value):
    spoken = normalize(f"{value:,}" if value >= 10_000 else str(value), tag)
    assert extract_number(spoken.replace("-", " "), lang="en") == value
