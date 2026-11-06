"""Date field resolution, with no speller (design section 5.3)."""
from __future__ import annotations

import calendar


def is_valid(year: int | None, month: int, day: int) -> bool:
    """Whether the day exists in the month; with no year, 29 February counts as valid."""
    if not 1 <= month <= 12 or day < 1:
        return False
    return day <= calendar.monthrange(2000 if year is None else year, month)[1]


def resolve(fields: tuple[str, str, str], date_order: str) -> tuple[int, int, int, str] | None:
    """(year, month, day, written order) from three digit fields, or None when they form no valid date.

    The four-digit field is the year. When the year is last, a field above 12 is the day, and only when
    both fields are 12 or below does `date_order` decide.
    """
    first, second, third = fields
    if len(first) == 4 and len(second) <= 2 and len(third) <= 2:
        year, month, day, order = int(first), int(second), int(third), "YMD"
    elif len(third) == 4 and len(first) <= 2 and len(second) <= 2:
        a, b = int(first), int(second)
        if a > 12 >= b:
            order = "DMY"
        elif b > 12 >= a:
            order = "MDY"
        else:
            order = "MDY" if date_order == "MDY" else "DMY"
        day, month = (a, b) if order == "DMY" else (b, a)
        year = int(third)
    else:
        return None
    return (year, month, day, order) if is_valid(year, month, day) else None
