"""The parameters of a call: the forms to read and the options of each reading."""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any, Literal

from text2spoken.errors import ArgumentTypeError, InvalidParameterError


class FrozenMap(Mapping):
    """An immutable, hashable mapping: key and value pairs sorted by key, with unique keys."""

    __slots__ = ("_items", "_index", "_hash")

    def __init__(self, items: Mapping | Iterable[tuple[Any, Any]] = ()):
        pairs = items.items() if isinstance(items, Mapping) else items
        index = dict(pairs)
        self._items = tuple(sorted(index.items(), key=lambda pair: pair[0]))
        self._index = index
        self._hash: int | None = None

    def __getitem__(self, key):
        return self._index[key]

    def __iter__(self) -> Iterator:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __reduce__(self):
        return FrozenMap, (self._items,)

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._items)
        return self._hash

    def __eq__(self, other) -> bool:
        if isinstance(other, FrozenMap):
            return self._items == other._items
        return isinstance(other, Mapping) and dict(self._items) == dict(other)

    def __repr__(self) -> str:
        return f"FrozenMap({dict(self._items)!r})"


def freeze(value: Any) -> Any:
    """A JSON value with each object as a FrozenMap and each list as a tuple."""
    if isinstance(value, Mapping):
        return FrozenMap((key, freeze(item)) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


def thaw(value: Any) -> Any:
    """The JSON value of a frozen value: the inverse of freeze."""
    if isinstance(value, Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [thaw(item) for item in value]
    return value


class Form(StrEnum):
    LEXICON = "lexicon"
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    RANGE = "range"
    EXPRESSION = "expression"
    DATE = "date"
    TIME = "time"
    YEAR = "year"
    MONEY = "money"
    MEASURE = "measure"
    PERCENT = "percent"
    TELEPHONE = "telephone"
    IDENTIFIER = "identifier"
    LETTERS = "letters"
    ABBREVIATION = "abbreviation"
    IDIOM = "idiom"
    ROMAN = "roman"
    COLOR = "color"


class GrammaticalGender(StrEnum):
    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"
    COMMON = "common"


class Animacy(StrEnum):
    ANIMATE = "animate"
    INANIMATE = "inanimate"
    PERSONAL = "personal"


_CHOICES = {
    "date_order": frozenset({"DMY", "MDY", "YMD"}),
    "clock": frozenset({"12h", "24h"}),
    "minute_style": frozenset({"number", "phrase"}),
    "scale": frozenset({"short", "long"}),
    "register": frozenset({"formal", "colloquial"}),
}

OPTIONS = ("date_order", "clock", "minute_style", "decimal_mark", "scale", "default_gender", "register",
           "phone_regions")
"""The options that a language file declares in `options` or `not_applicable`."""


@dataclass(frozen=True, kw_only=True)
class NormalizationParams:
    forms: frozenset[Form] = frozenset(Form)
    date_order: Literal["DMY", "MDY", "YMD"] | None = None
    clock: Literal["12h", "24h"] | None = None
    minute_style: Literal["number", "phrase"] | None = None
    decimal_mark: str | None = None
    scale: Literal["short", "long"] | None = None
    default_gender: FrozenMap = field(default_factory=FrozenMap)
    register: Literal["formal", "colloquial"] | None = None
    phone_regions: frozenset[str] | None = None
    lexicon: FrozenMap = field(default_factory=FrozenMap)
    strict: bool = False

    def __post_init__(self):
        if not isinstance(self.forms, frozenset) or not all(isinstance(f, Form) for f in self.forms):
            raise ArgumentTypeError("forms must be a frozenset of Form")
        for name, choices in _CHOICES.items():
            value = getattr(self, name)
            if value is not None and value not in choices:
                raise InvalidParameterError(f"{name} must be one of {sorted(choices)} or None, not {value!r}")
        if self.decimal_mark is not None and (not isinstance(self.decimal_mark, str) or len(self.decimal_mark) != 1):
            raise InvalidParameterError(f"decimal_mark must be one character or None, not {self.decimal_mark!r}")
        if not isinstance(self.default_gender, FrozenMap) or not all(
                isinstance(code, str) and isinstance(gender, GrammaticalGender)
                for code, gender in self.default_gender.items()):
            raise ArgumentTypeError("default_gender must be a FrozenMap of language code to GrammaticalGender")
        if self.phone_regions is not None and (
                not isinstance(self.phone_regions, frozenset)
                or not all(isinstance(region, str) for region in self.phone_regions)):
            raise ArgumentTypeError("phone_regions must be a frozenset of ISO 3166 region codes or None")
        if not isinstance(self.lexicon, FrozenMap) or not all(
                isinstance(tag, str) and isinstance(entries, FrozenMap)
                and all(isinstance(k, str) and k and isinstance(v, str) for k, v in entries.items())
                for tag, entries in self.lexicon.items()):
            raise ArgumentTypeError(
                "lexicon must be a FrozenMap of language tag to a FrozenMap of written form to spoken words")
        if not isinstance(self.strict, bool):
            raise ArgumentTypeError("strict must be a bool")

    def only(self, *forms: Form) -> NormalizationParams:
        return replace(self, forms=frozenset(forms))

    def without(self, *forms: Form) -> NormalizationParams:
        return replace(self, forms=self.forms - frozenset(forms))

