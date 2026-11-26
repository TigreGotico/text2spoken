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
from text2spoken.core.tokens import is_letter
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
        ranked = sorted((sum(a != b for a, b in zip(symbol, other)), other, unit)
                        for unit in units for other in unit["symbols"]
                        if len(other) == len(symbol) and other.lower() == symbol.lower())
        if ranked and (len(ranked) == 1 or ranked[0][0] < ranked[1][0]):
            table[symbol] = ranked[0][2]
    return FrozenMap(table)


@lru_cache(maxsize=64)
def _joined_table(tag: str, excluded: tuple[str, ...], listed: tuple[str, ...]) -> FrozenMap:
    units = [unit for unit in cldr_data(tag)["units"].values() if all(map(_words_only, unit["names"].values()))]
    by_symbol = {symbol: unit for unit in units for symbol in unit["symbols"]}
    table = {symbol: unit for symbol, unit in by_symbol.items()
             if len(symbol) > 1 and symbol.isalpha() and symbol.isupper() and symbol not in excluded}
    cases: dict[str, set[str]] = {}
    for unit in cldr_data(tag)["units"].values():
        for symbol in unit["symbols"]:
            cases.setdefault(symbol.lower(), set()).add(symbol)
    for symbol in listed:
        if len(symbol) > 1 and symbol.isalpha() and cases.get(symbol) == {symbol} and symbol in by_symbol \
                and symbol.upper() not in excluded:
            table[symbol.upper()] = by_symbol[symbol]
    return FrozenMap(table)


def joined_table(request: Request) -> FrozenMap:
    """The CLDR symbols of two capital letters or more that read as units only when they touch the digits, as `GB`
    in `10GB`, apart from those of `unjoined_symbols`. A run of capitals joined to digits is no word of running
    text, so `10GB` reads "ten gigabytes", and `29 GB golds`, with a space, reads no unit. A symbol of
    `unit_symbols` in lowercase reads in capitals too when no other CLDR symbol differs from it only in case, so
    `5KM` reads as `5km`, and `ml` gives no `ML`, because CLDR also names `mL`. `unjoined_symbols` holds `ML`
    itself, the CLDR megalitre, so `2ML` stays as written. A language file with no `unit_symbols` reads no CLDR
    units, and none of these."""
    data = request.data
    if "unit_symbols" not in data:
        return FrozenMap()
    return _joined_table(request.variety.tag, tuple(data.get("unjoined_symbols", ())), tuple(data["unit_symbols"]))


def unit_table(request: Request) -> FrozenMap:
    """The units that the request reads, by written symbol. With `unit_symbols`, a CLDR symbol of the variety reads
    when it cannot be a plain word or when the list names it. Without it, the `units` table of the language."""
    data = request.data
    if "unit_symbols" not in data:
        return data.get("units", FrozenMap())
    return _cldr_table(request.variety.tag, tuple(data["unit_symbols"]))


def decimal_table(request: Request) -> FrozenMap:
    """The units of `decimal_unit_symbols`, which read only after a number with a decimal part, as `L` in `1,8 L`."""
    data = request.data
    decimal = tuple(data.get("decimal_unit_symbols", ()))
    if not decimal:
        return FrozenMap()
    table = _cldr_table(request.variety.tag, tuple(data["unit_symbols"]) + decimal)
    return FrozenMap({symbol: table[symbol] for symbol in decimal if symbol in table})


def _takes_power(symbol: str) -> bool:
    """Whether `²` or `³` may follow the symbol: not after a power, and not after `/`, so `kWh/100km²` is no square
    of `kWh/100km`."""
    return symbol[-1] not in POWERS and "/" not in symbol


@lru_cache(maxsize=64)
def _by_length(table: FrozenMap) -> tuple[str, ...]:
    return tuple(sorted(table, key=len, reverse=True))


def elided(text: str, end: int) -> bool:
    """Whether an apostrophe and a letter follow text[:end]: the letters before it are an elided word, as `l'` in
    `l'anno`, and no unit symbol."""
    return text[end:end + 1] in ("'", "’") and end + 1 < len(text) and is_letter(text[end + 1])


def units_at(text: str, start: int, request: Request) -> Iterator[str]:
    """The written units that start at text[start], the longest first. With CLDR data, a symbol with no `/` may take
    `²` or `³` after it, and a symbol may take `/` and a second symbol, as in `kg/m²` and `km/h²`. A symbol before
    an apostrophe and a letter is an elided word, so `2007 l'ano` holds no unit."""
    table = unit_table(request)
    symbols = _by_length(table)
    compound = "unit_symbols" in request.data

    def bases(at: int) -> Iterator[str]:
        for symbol in symbols:
            if text.startswith(symbol, at):
                power = text[at + len(symbol):at + len(symbol) + 1]
                if compound and power in POWERS and _takes_power(symbol):
                    yield symbol + power
                yield symbol

    def candidates() -> Iterator[str]:
        for base in bases(start):
            end = start + len(base)
            if compound and text[end:end + 1] == "/":
                yield from (base + "/" + denominator for denominator in bases(end + 1))
            yield base

    return iter(sorted((unit for unit in candidates() if not elided(text, start + len(unit))), key=len, reverse=True))


def _pattern(names: FrozenMap, category: str) -> str:
    return names.get(category, names["other"])


def _simple(request: Request, unit: str, category: str) -> tuple[str, str | None] | None:
    table = {**decimal_table(request), **joined_table(request), **unit_table(request)}
    if unit in table:
        return _pattern(table[unit]["names"], category), table[unit].get("gender")
    if unit[-1:] in POWERS and unit[:-1] in table and _takes_power(unit[:-1]):
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
