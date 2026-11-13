"""Currency names and currency symbols from the CLDR data of a variety (design section 4.7).

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/<tag>.currencies.json`, with the parent chain already
resolved. A language file that gives `currency_symbols` reads its currencies from that file: each currency reads with
its CLDR display name in the plural category of the number. A language file with no `currency_symbols` reads its own
`currencies` table.

The symbols are the CLDR symbols of the locale and the ISO 4217 code of each currency. A CLDR symbol that two
currencies share reads as the currency whose `symbol` it is in the locale; the extractor leaves out a symbol that no
currency or two currencies hold so. Many symbols are also words or letters of running text (`K`, `L`, `R`, `kr`,
`Ft`, `TOP`, `ALL`), so a symbol reads only in one of two cases: it holds a currency sign, a character of the Unicode
general category `Sc` such as `$`, `€` or `₹`, or the language file lists it in `currency_symbols`. A currency with a
CLDR name that holds a character other than a letter, a space, `-` or `'` does not read, because a reading holds words
only (design section 11). The sign `¤` of XXX, "(unknown currency)", so stays as written, and it still belongs to
`MONEY`, so the `SYMBOL` form does not read it either.

An entry of the `currencies` table of the language file wins over CLDR for that currency only. A name by plural
category, such as `one` or `other`, replaces the CLDR name. `symbols` assigns each symbol that it lists to the
currency, so a symbol that CLDR shares between currencies, such as the narrow `¥`, reads as that currency. `minor`
gives the names of the minor unit, which CLDR does not hold.
"""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.language import Request
from text2spoken.params import FrozenMap, freeze

_OWN = frozenset({"symbols", "minor"})


@lru_cache(maxsize=None)
def cldr_part(tag: str, part: str) -> FrozenMap:
    """The CLDR data file `<tag>.<part>.json` of a variety tag, read on first use, or an empty map when the
    release gives the variety no such file."""
    path = files("text2spoken") / "data" / "cldr" / f"{tag}.{part}.json"
    if not path.is_file():
        return FrozenMap()
    return freeze(json.loads(path.read_text(encoding="utf-8")))


def words_only(name: str) -> bool:
    """Whether a CLDR name holds words only: letters, spaces, `-` and `'`."""
    return all(char.isalpha() or char.isspace() or char in "-'" for char in name)


def has_sign(symbol: str) -> bool:
    """Whether a symbol holds a currency sign, a character of the Unicode general category `Sc`."""
    return any(unicodedata.category(char) == "Sc" for char in symbol)


@lru_cache(maxsize=64)
def _owners(tag: str, listed: tuple[str, ...], own: FrozenMap) -> FrozenMap:
    """The currency of each symbol that the CLDR table of the variety lists, with the symbols that the language file
    assigns over them."""
    currencies = cldr_part(tag, "currencies")["currencies"]
    owner = {symbol: code for code, currency in currencies.items()
             for symbol in (*currency["symbols"], code) if has_sign(symbol) or symbol in listed}
    return FrozenMap(owner | {symbol: code for code, entry in own.items() for symbol in entry.get("symbols", ())})


@lru_cache(maxsize=64)
def _cldr_table(tag: str, listed: tuple[str, ...], own: FrozenMap) -> FrozenMap:
    owner = _owners(tag, listed, own)
    table = {}
    for code, currency in cldr_part(tag, "currencies")["currencies"].items():
        symbols = tuple(sorted(symbol for symbol, holder in owner.items() if holder == code))
        if symbols and all(map(words_only, currency["names"].values())):
            entry = own.get(code, FrozenMap())
            names = {**currency["names"], **{key: value for key, value in entry.items() if key not in _OWN}}
            table[code] = FrozenMap({**names, "symbols": symbols,
                                     **({"minor": entry["minor"]} if "minor" in entry else {})})
    return FrozenMap(table)


def currency_table(request: Request) -> FrozenMap:
    """The currencies that the request reads, by ISO 4217 code: the names by plural category, `symbols` and,
    when the language gives one, `minor`. With `currency_symbols`, the CLDR currencies of the variety with the
    entries of the `currencies` table over them. Without it, the `currencies` table of the language."""
    data = request.data
    if "currency_symbols" not in data:
        return data.get("currencies", FrozenMap())
    return _cldr_table(request.variety.tag, tuple(data["currency_symbols"]), data.get("currencies", FrozenMap()))


@lru_cache(maxsize=64)
def _table_signs(table: FrozenMap) -> frozenset[str]:
    return frozenset(symbol for currency in table.values() for symbol in currency["symbols"])


@lru_cache(maxsize=64)
def _cldr_signs(tag: str, listed: tuple[str, ...], own: FrozenMap) -> frozenset[str]:
    return frozenset(_owners(tag, listed, own))


def currency_signs(request: Request) -> frozenset[str]:
    """Every symbol that the currency table of the variety lists, also the symbol of a currency whose name does not
    read, such as `¤`."""
    data = request.data
    if "currency_symbols" not in data:
        return _table_signs(currency_table(request))
    return _cldr_signs(request.variety.tag, tuple(data["currency_symbols"]), data.get("currencies", FrozenMap()))


@lru_cache(maxsize=64)
def _by_length(table: FrozenMap) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(((symbol, code) for code, currency in table.items() for symbol in currency["symbols"]),
                        key=lambda pair: len(pair[0]), reverse=True))


def currency_symbols(request: Request) -> tuple[tuple[str, str], ...]:
    """Each symbol that reads as a currency, with its code, the longest first, so `R$` wins over `$`."""
    return _by_length(currency_table(request))


def currency_name(currency: FrozenMap, category: str) -> str:
    """The name of a currency in a plural category. A missing category reads as `other`, as in CLDR."""
    return currency.get(category, currency["other"])
