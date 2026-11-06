"""Time field parsing, with no speller (design section 5.3)."""
from __future__ import annotations


def clock_fields(hour: str, minute: str, second: str | None) -> tuple[int, int, int | None] | None:
    """(hour, minute, second) of a written `H:MM` or `H:MM:SS`, or None outside 0-23, 00-59 and 00-59.

    A minute or a second needs two digits, so `16:9` and `2:1` give None.
    """
    if not (1 <= len(hour) <= 2 and len(minute) == 2 and (second is None or len(second) == 2)):
        return None
    h, m, s = int(hour), int(minute), None if second is None else int(second)
    if h > 23 or m > 59 or (s is not None and s > 59):
        return None
    return h, m, s


def twelve_hour(hour: int) -> int:
    """The hour on a 12-hour clock face: 0 and 12 are 12."""
    return hour % 12 or 12


def day_period(hour: int) -> str:
    return "am" if hour < 12 else "pm"
