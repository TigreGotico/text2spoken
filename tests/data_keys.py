"""The data keys that the shared code of the core reads, and the shape that each key must have.

A language file gives these keys in `data` and `Variety.data`. The core reads each one with `data.get`, so a key
with a wrong name or a wrong shape turns a rule off with no error. Clause 6 of the contract checks the shape of
each key that a file gives. `test_contract.py` checks that this list holds every key that the core reads.
"""
from collections.abc import Callable

from text2spoken.core.numbers import SIGNS
from text2spoken.params import OPTIONS, Form, FrozenMap

Shape = Callable[[object, str], None]


def text(value, where: str) -> None:
    assert type(value) is str, f"{where}: {value!r} is not a string"


def word(value, where: str) -> None:
    assert type(value) is str and value, f"{where}: {value!r} is not a non-empty string"


def character(value, where: str) -> None:
    assert type(value) is str and len(value) == 1, f"{where}: {value!r} is not one character"


def digits(value, where: str) -> None:
    assert type(value) is str and value.isascii() and value.isdigit(), f"{where}: {value!r} is not ASCII digits"


def script(value, where: str) -> None:
    assert type(value) is str and len(value) == 4 and value.isalpha() and value.istitle(), \
        f"{where}: {value!r} is not an ISO 15924 script code such as 'Latn'"


def boolean(value, where: str) -> None:
    assert type(value) is bool, f"{where}: {value!r} is not true or false"


def anything(value, where: str) -> None:
    pass


def one_of(*values: str) -> Shape:
    def check(value, where: str) -> None:
        assert value in values, f"{where}: {value!r} is not one of {sorted(values)}"
    return check


def list_of(item: Shape, length: int | None = None, minimum: int = 0) -> Shape:
    def check(value, where: str) -> None:
        assert isinstance(value, tuple), f"{where}: {value!r} is not a list"
        assert length is None or len(value) == length, f"{where}: {len(value)} entries, not {length}"
        assert len(value) >= minimum, f"{where}: fewer than {minimum} entries"
        for index, entry in enumerate(value):
            item(entry, f"{where}[{index}]")
    return check


def map_of(key: Shape, value: Shape) -> Shape:
    def check(table, where: str) -> None:
        assert isinstance(table, FrozenMap), f"{where}: {table!r} is not an object"
        for name, entry in table.items():
            key(name, f"{where} key")
            value(entry, f"{where}.{name}")
    return check


def record(optional: dict[str, Shape] | None = None, **fields: Shape) -> Shape:
    """An object that holds at least these fields, and the optional fields in their shape when it holds them; the
    language file may add its own."""
    def check(table, where: str) -> None:
        assert isinstance(table, FrozenMap), f"{where}: {table!r} is not an object"
        for name, field in fields.items():
            assert name in table, f"{where}: no {name!r}"
            field(table[name], f"{where}.{name}")
        for name, field in (optional or {}).items():
            if name in table:
                field(table[name], f"{where}.{name}")
    return check


WORDS = list_of(word)

SHAPES: dict[str, Shape] = {
    "case_suffixes": WORDS,
    "clock_marks": list_of(record(mark=word, seconds=boolean, needs=one_of("evidence", "day_period", "none"),
                                  optional={"closes_hour": boolean})),
    "color_words": WORDS,
    "currencies": map_of(word, record(symbols=list_of(word, minimum=1))),
    "day_periods": map_of(word, WORDS),
    "defaults": map_of(one_of(*OPTIONS), text),
    "digit_words": list_of(word, length=10),
    "dimension_marks": WORDS,
    "electronic_labels": map_of(word, one_of("word", "letters")),
    "electronic_schemes": map_of(word, one_of("read", "drop")),
    "electronic_symbols": map_of(character, word),
    "electronic_tlds": WORDS,
    "electronic_vowels": list_of(one_of(*"abcdefghijklmnopqrstuvwxyz"), minimum=1),
    "idioms": map_of(word, text),
    "leads": map_of(word, text),
    "letter_names": map_of(one_of(*"abcdefghijklmnopqrstuvwxyz"), word),
    "list_links": WORDS,
    "number_marks": map_of(script, list_of(record(decimal=word, group=text), minimum=1)),
    "operators": map_of(character, word),
    "percent": record(signs=list_of(word, minimum=1), position=one_of("after", "before", "either")),
    "no_phone_shapes": WORDS,
    "phone_kept_shapes": WORDS,
    "phone_shapes": WORDS,
    "phone_unit_shapes": WORDS,
    "phone_words": WORDS,
    "proclitics": WORDS,
    "range_marks": WORDS,
    "range_word": text,
    "scales": map_of(word, text),
    "short_codes": list_of(digits),
    "sign_words": map_of(one_of(*SIGNS.values()), word),
    "symbols": map_of(word, one_of(*Form)),
    "time_suffixes": WORDS,
    "time_words": WORDS,
    "unit_symbols": WORDS,
    "units": map_of(word, anything),
}
"""Each key that the core reads, with its shape. A shape names only what the core reads: the value of a unit is
for the verbalizers of the file, so the core reads the unit names only."""

READERS: dict[str, frozenset[str]] = {
    "lexicon": frozenset(),
    "cardinal": frozenset({"number_marks", "leads", "sign_words", "symbols", "proclitics", "case_suffixes"}),
    "decimal": frozenset({"number_marks", "symbols", "proclitics", "case_suffixes"}),
    "fraction": frozenset({"symbols", "units", "unit_symbols", "proclitics", "case_suffixes"}),
    "idiom": frozenset({"idioms", "proclitics", "case_suffixes"}),
    "range": frozenset({"range_marks", "symbols", "proclitics", "case_suffixes"}),
    "date_numeric": frozenset({"symbols", "proclitics", "case_suffixes"}),
    "time_clock": frozenset({"range_word", "range_marks", "clock_marks", "time_words", "day_periods", "time_suffixes"}),
    "percent": frozenset({"number_marks", "percent", "range_word", "range_marks", "proclitics", "case_suffixes"}),
    "money": frozenset({"number_marks", "currencies", "scales", "range_word", "range_marks", "proclitics",
                      "case_suffixes"}),
    "measure": frozenset({"number_marks", "symbols", "units", "unit_symbols", "dimension_marks", "range_marks",
                        "proclitics", "case_suffixes"}),
    "telephone": frozenset({"phone_words", "day_periods", "phone_shapes", "phone_unit_shapes", "phone_kept_shapes",
                          "no_phone_shapes", "short_codes", "list_links", "operators", "symbols", "proclitics",
                          "case_suffixes"}),
    "color": frozenset({"color_words"}),
    "electronic": frozenset({"electronic_schemes", "electronic_tlds"}),
    "speak_cardinal": frozenset({"digit_words", "sign_words", "leads"}),
    "speak_lexicon": frozenset(),
    "speak_electronic": frozenset({"electronic_symbols", "letter_names", "electronic_vowels", "electronic_labels",
                                   "electronic_schemes", "digit_words"}),
    "render": frozenset({"symbols"}),
    "effective_params": frozenset({"defaults"}),
}
"""The keys that each shared recognizer reads, by its name in `SHARED`. Then the keys that the shared verbalizers
`speak_cardinal`, `speak_lexicon` and `speak_electronic` read, and the keys of the unread check of `render` and of
the option defaults of `effective_params`."""

PHONE_SHAPE_KEYS = ("phone_shapes", "phone_unit_shapes", "phone_kept_shapes", "no_phone_shapes")
"""The tables of regexes that the shared telephone recognizer compiles."""

OPTIONAL = frozenset({
    "proclitics", "case_suffixes", "time_suffixes", "range_marks", "day_periods", "electronic_labels",
})
"""Keys whose absence means that the language has none, so a file that uses their reader may leave them out."""

ALTERNATIVES = (frozenset({"units", "unit_symbols"}),)
"""Keys of which a file gives at least one: its own unit table, or the unit symbols that it reads from CLDR."""
