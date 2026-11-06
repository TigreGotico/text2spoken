# API

Every public name comes from the top-level package:

```python
from text2spoken import normalize
```

## Functions

| Function | Result |
| --- | --- |
| `normalize(text, lang)` | Runs all passes and returns the spoken text |
| `expand_dates_and_times(text, full_lang, date_format="DMY")` | Expands dates such as `03/08/2025` and times such as `14h30`. Pass `"MDY"` to read an ambiguous date as month first |
| `expand_hyphen_digits(text)` | Splits a word from a digit that a hyphen joins. A range of digits stays as it is |
| `expand_units(text, full_lang)` | Expands units and ordinal indicators that follow a number |
| `expand_word(word, lang)` | Expands one word: a contraction, a title, a fraction or a number |
| `is_fraction(word)` | Returns `True` for a word such as `3/4` |
| `pronounce_date(date_obj, full_lang)` | Returns the spoken form of a `datetime.date` |
| `pronounce_time(time_string, full_lang)` | Returns the spoken form of a time such as `15h01` |

`normalize` catches an error from the date pass and continues. `expand_dates_and_times` does not catch it, so an unsupported language can raise.

## Tables

`CONTRACTIONS`, `TITLES` and `UNITS` are dictionaries. Each key is an ISO 639 language code, and each value maps a written form to its spoken form. The tables live in `text2spoken/tables.py`, apart from the code that applies them.

## Version

`__version__` holds the package version as a string.

## Logging

The library logs to `logging.getLogger("text2spoken")`.
