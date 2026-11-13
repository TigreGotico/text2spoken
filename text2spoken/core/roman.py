"""Roman numeral parsing (design section 5.3)."""
from __future__ import annotations

_THOUSANDS = ("", "M", "MM", "MMM")
_HUNDREDS = ("", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM")
_TENS = ("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC")
_UNITS = ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")


def to_roman(number: int) -> str:
    return (_THOUSANDS[number // 1000] + _HUNDREDS[number // 100 % 10] + _TENS[number // 10 % 10]
            + _UNITS[number % 10])


_VALUES = {to_roman(n): n for n in range(1, 4000)}


def value(numeral: str) -> int | None:
    """The value of a canonical upper-case Roman numeral from 1 to 3999; `IIII` and `IC` give None."""
    return _VALUES.get(numeral)
