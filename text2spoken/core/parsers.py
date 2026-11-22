"""The one module that imports ovos-number-parser and ovos-date-parser (design section 5.4).

Each name of `WRITERS` imports its library on its first use, so `import text2spoken` imports neither library, and a
language pays for the import at its first number or date. When the writers move to another package, `WRITERS` and
`number_writer_languages` are the one place to change.
"""
from __future__ import annotations

import pkgutil
from functools import cache
from importlib import import_module

WRITERS = {
    "pronounce_number": ("ovos_number_parser", "pronounce_number"),
    "pronounce_ordinal": ("ovos_number_parser", "pronounce_ordinal"),
    "pronounce_fraction": ("ovos_number_parser", "pronounce_fraction"),
    "GrammaticalGender": ("ovos_number_parser.util", "GrammaticalGender"),
    "Scale": ("ovos_number_parser.util", "Scale"),
    "spoken_date": ("ovos_date_parser.spoken", "spoken_date"),
    "spoken_time": ("ovos_date_parser.spoken", "spoken_time"),
}
"""Each name that text2spoken reads from the parsers: its module and its attribute."""


def __getattr__(name: str):
    try:
        module, attribute = WRITERS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    return getattr(import_module(module), attribute)


@cache
def number_writer_languages() -> frozenset[str]:
    """The languages that ovos-number-parser writes with a module of its own, `numbers_<code>`. It reads every other
    language through CLDR RBNF: the docstring of `pronounce_number` says "Falls back to Unicode RBNF for unsupported
    languages"."""
    package = import_module("ovos_number_parser")
    return frozenset(module.name.removeprefix("numbers_") for module in pkgutil.iter_modules(package.__path__)
                     if module.name.startswith("numbers_"))
