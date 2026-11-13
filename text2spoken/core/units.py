"""Unit symbols and unit words from the CLDR data of a variety (design section 4.7).

`scripts/extract_cldr.py` writes one file per variety tag under `text2spoken/data/cldr/`, with the parent chain
already resolved. A language file that gives `unit_symbols` reads its units from that file: each written symbol
reads with the CLDR `long` pattern of its unit, in the plural category of the number. A language file with no
`unit_symbols` reads its own `units` table.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.language import Request
from text2spoken.params import FrozenMap, freeze

MICRO = "µμ"
POWERS = {"²": "power2", "³": "power3"}
_NO_WORD = "0123456789/²³‰" + MICRO


@lru_cache(maxsize=None)
def cldr_data(tag: str) -> FrozenMap:
    """The CLDR data file of a variety tag, read on first use."""
    path = files("text2spoken") / "data" / "cldr" / f"{tag}.json"
    return freeze(json.loads(path.read_text(encoding="utf-8")))


def no_word(symbol: str) -> bool:
    """Whether a symbol cannot be a plain word of running text: it holds a digit, `/`, a micro sign, `²`, `³` or
    `‰`, a `°` before a letter, as in `°C`, or a capital letter after a lowercase letter, as in `kWh`."""
    return (any(char in _NO_WORD for char in symbol)
            or any(first == "°" and second.isalpha() for first, second in zip(symbol, symbol[1:]))
            or any(first.islower() and second.isupper() for first, second in zip(symbol, symbol[1:])))


def _words_only(pattern: str) -> bool:
    return all(char.isalpha() or char.isspace() or char in "-'" for char in pattern.replace("{0}", ""))


def _case_changes(symbol: str, other: str) -> int:
    return sum(first != second for first, second in zip(symbol, other))


@lru_cache(maxsize=64)
def _cldr_table(tag: str, listed: tuple[str, ...]) -> FrozenMap:
    """A unit whose CLDR name holds a digit or a symbol, as `{0} litres per 100 kilometres` does, reads no symbol,
    because a reading holds words only (design section 11).

    A listed symbol that is no CLDR symbol of the locale, but differs from one only in case, reads as that unit, so
    en-US `ml` reads as `mL`. When it differs in case from two symbols, as `ml` does from `mL` and `ML`, the symbol
    with the fewest case changes wins, and a tie reads no unit."""
    units = [unit for unit in cldr_data(tag)["units"].values() if all(map(_words_only, unit["names"].values()))]
    table = {symbol: unit for unit in units for symbol in unit["symbols"] if no_word(symbol) or symbol in listed}
    written = {symbol for unit in cldr_data(tag)["units"].values() for symbol in unit["symbols"]}
    for symbol in listed:
        if symbol in written:
            continue
        ranked = sorted((_case_changes(symbol, other), other, unit) for unit in units for other in unit["symbols"]
                        if len(other) == len(symbol) and other.lower() == symbol.lower())
        if ranked and (len(ranked) == 1 or ranked[0][0] < ranked[1][0]):
            table[symbol] = ranked[0][2]
    return FrozenMap(table)


def unit_table(request: Request) -> FrozenMap:
    """The units that the request reads, by written symbol. With `unit_symbols`, a CLDR symbol of the variety reads
    when it cannot be a plain word or when the list names it. Without it, the `units` table of the language."""
    data = request.data
    if "unit_symbols" not in data:
        return data.get("units", FrozenMap())
    return _cldr_table(request.variety.tag, tuple(data["unit_symbols"]))


@lru_cache(maxsize=64)
def _by_length(table: FrozenMap) -> tuple[str, ...]:
    return tuple(sorted(table, key=len, reverse=True))


def units_at(text: str, start: int, request: Request) -> Iterator[str]:
    """The written units that start at text[start], the longest first. With CLDR data, a symbol with no `/` may take
    `²` or `³` after it, and a symbol may take `/` and a second symbol, as in `kg/m²`."""
    table = unit_table(request)
    symbols = _by_length(table)
    compound = "unit_symbols" in request.data

    def bases(at: int) -> Iterator[str]:
        for symbol in symbols:
            if text.startswith(symbol, at):
                power = text[at + len(symbol):at + len(symbol) + 1]
                if compound and power in POWERS and symbol[-1] not in POWERS and "/" not in symbol:
                    yield symbol + power
                yield symbol

    for base in bases(start):
        end = start + len(base)
        if compound and text[end:end + 1] == "/":
            yield from (base + "/" + denominator for denominator in bases(end + 1))
        yield base


def _pattern(names: FrozenMap, category: str) -> str:
    return names.get(category, names["other"])


def _simple(request: Request, unit: str, category: str) -> tuple[str, str | None] | None:
    table = unit_table(request)
    if unit in table:
        return _pattern(table[unit]["names"], category), table[unit].get("gender")
    if unit[-1:] in POWERS and unit[:-1] in table:
        entry = table[unit[:-1]]
        compound = cldr_data(request.variety.tag)["compound"]
        power = POWERS[unit[-1]]
        if entry.get("gender") == "feminine" and power + "_feminine" in compound:
            power += "_feminine"
        pattern = _pattern(entry["names"], category)
        name = pattern.replace("{0}", "").strip()
        return pattern.replace(name, _pattern(compound[power], category).replace("{0}", name)), entry.get("gender")
    return None


def unit_reading(request: Request, unit: str, category: str) -> tuple[str, str | None]:
    """The CLDR pattern of a written unit in a plural category, with `{0}` for the number, and the gender of the
    unit, or None. `a/b` reads the per-unit pattern of `b` when it holds words only, else the `per` pattern with the
    singular name of `b`. A missing category reads as `other`."""
    simple = _simple(request, unit, category)
    if simple is not None:
        return simple
    for index, char in enumerate(unit):
        if char != "/":
            continue
        numerator = _simple(request, unit[:index], category)
        denominator = unit[index + 1:]
        singular = _simple(request, denominator, "one")
        if numerator is None or singular is None:
            continue
        pattern, gender = numerator
        per = unit_table(request).get(denominator, FrozenMap()).get("per")
        if per is not None and _words_only(per):
            return per.replace("{0}", pattern), gender
        per = cldr_data(request.variety.tag)["compound"]["per"]
        return per.replace("{1}", singular[0].replace("{0}", "").strip()).replace("{0}", pattern), gender
    raise KeyError(unit)
