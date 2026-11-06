"""Text normalization: rewriting written text into the words a voice should speak.

``normalize(text, lang)`` is the entry point. It runs the raw text through the
per-concern passes in this package — dates and times, hyphen-joined
word/digit pairs, units and ordinal indicators, then a word-by-word pass that
expands contractions, titles, fractions and bare numbers — so that nothing
reaches the phonemizer as digits or symbols.

The language-specific lookup tables live in :mod:`text2spoken.tables`,
apart from the code that applies them, so a new language is a data change.
"""

from text2spoken.datetimes import (
    _normalize_dates_and_times,
    pronounce_date,
    pronounce_time,
)
from text2spoken.numbers import (
    _get_number_separators,
    _normalize_number_word,
    is_fraction,
)
from text2spoken.tables import CONTRACTIONS, TITLES, UNITS
from text2spoken.text import (
    _normalize_word,
    _normalize_word_hyphen_digit,
    expand_word,
    normalize,
)
from text2spoken.units import _normalize_units
from text2spoken.version import __version__

expand_dates_and_times = _normalize_dates_and_times
expand_hyphen_digits = _normalize_word_hyphen_digit
expand_units = _normalize_units

__all__ = [
    "CONTRACTIONS",
    "TITLES",
    "UNITS",
    "__version__",
    "expand_dates_and_times",
    "expand_hyphen_digits",
    "expand_units",
    "expand_word",
    "is_fraction",
    "normalize",
    "pronounce_date",
    "pronounce_time",
]
