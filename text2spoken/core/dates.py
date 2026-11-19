"""Date field resolution, and the CLDR date data of a language with no file, with no speller (design sections 5.3
and 17.5)."""
from __future__ import annotations

import calendar
import json
import re
from functools import lru_cache
from importlib.resources import files

DATE_FIELDS = {"d": "day", "M": "month", "MMMM": "month_name", "y": "year"}
"""The fields of a CLDR date pattern that a date with no file reads, by their UTS #35 symbols: the day of the month,
the month as a number, the wide month name in the format context, and the year. A pattern with any other field, such
as the era `G` of Thai, gives no reading."""

FIELD_WIDTHS = {"dd": "d", "MM": "M", "yyyy": "y"}
"""The fields that pad a number with zeros, by the field of the same number with no padding."""


def is_valid(year: int | None, month: int, day: int) -> bool:
    """Whether the day exists in the month; with no year, 29 February counts as valid. The calendar has no year 0,
    so `0000-01-01` is no date."""
    if not 1 <= month <= 12 or day < 1 or (year is not None and year < 1):
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


@lru_cache(maxsize=1)
def date_locales() -> frozenset[str]:
    """The locales with a dates file of `scripts/extract_cldr.py`."""
    folder = files("text2spoken") / "data" / "cldr"
    return frozenset(entry.name.removesuffix(".dates.json") for entry in folder.iterdir()
                     if entry.name.endswith(".dates.json"))


@lru_cache(maxsize=1)
def date_readings() -> dict[str, dict]:
    """The cited date readings of `data/date_readings.json`, by CLDR locale."""
    return json.loads((files("text2spoken") / "data" / "date_readings.json").read_text(encoding="utf-8"))["locales"]


@lru_cache(maxsize=128)
def long_date(locale: str) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...], dict[str, dict]] | None:
    """The parts of the CLDR `long` date pattern of the locale, its twelve month names and the forms of its day and
    year. A part is `("text", literal)`, or a field of `DATE_FIELDS` as `(name, "")`; a day followed by a full stop is
    `("ordinal_day", "")`. An entry of `date_readings` whose `written` pattern is the pattern of the file gives the
    pattern to read by and whether the day and the year read as ordinals (`ordinal_day`, `ordinal_year`).

    UTS #35, Part 4, "Date Format Patterns": text in apostrophes is literal, two apostrophes are one, and a run of
    one ASCII letter is a field. In Czech, Danish, Finnish, Icelandic, Norwegian and other languages, "a period or
    full stop is written after the numeral" of an ordinal (Wikipedia, "Ordinal indicator"), so `d.` is an ordinal
    day: `d. MMMM y` reads the ordinal of the day. A full stop anywhere else gives None, unless an entry of
    `date_readings` gives the words. So do a field outside
    `DATE_FIELDS` and the year of two digits `yy`."""
    stored = json.loads((files("text2spoken") / "data" / "cldr" / f"{locale}.dates.json").read_text(encoding="utf-8"))
    reading = date_readings().get(locale)
    if reading is None or reading["written"] != stored["long"]:
        reading = {}
    parts: list[tuple[str, str]] = []
    for match in re.finditer(r"'((?:[^']|'')*)'|([A-Za-z])\2*|([^A-Za-z']+)", reading.get("spoken", stored["long"])):
        quoted, field, text = match.group(1), match.group(0) if match.group(2) else None, match.group(3)
        if field is not None:
            name = DATE_FIELDS.get(FIELD_WIDTHS.get(field, field))
            if name is None:
                return None
            parts.append((name, ""))
            continue
        literal = (quoted.replace("''", "'") or "'") if quoted is not None else text
        if parts and parts[-1] == ("day", "") and quoted is None and literal.startswith("."):
            parts[-1], literal = ("ordinal_day", ""), literal[1:]
        if "." in literal:
            return None
        if literal:
            parts.append(("text", literal))
    forms = {field: reading[field] for field in ("day", "year") if field in reading}
    for index, (name, _) in enumerate(parts):
        field = name.removeprefix("ordinal_")
        if field in forms:
            parts[index] = ("ordinal_" + field if forms[field]["reading"] == "ordinal" else field, "")
    return tuple(parts), tuple(stored["months"]), forms
