# text2spoken

text2spoken rewrites written text into the words a voice speaks. It expands numbers, dates, times, units, titles and contractions. A phonemizer then reads words, not digits or symbols.

## Quickstart

```bash
pip install --pre text2spoken
```

```python
from text2spoken import normalize

print(normalize("Dr. Smith paid 3/4 of the bill at 25°C.", "en"))
print(normalize("O Sr. Silva pagou 10kg às 14h30.", "pt-PT"))
```

```text
Doctor Smith paid three quarters of the bill at twenty five degrees celsius.
O Senhor Silva pagou dez quilogramas às catorze e trinta.
```

## Where this fits

Alone: it turns written text into spoken words, with `from text2spoken import normalize`.
In the stack: it is the normalisation stage. A frontend or a TTS library calls it before phonemization, and it calls `ovos-number-parser`, `ovos-date-parser` and `unicode_rbnf`.
Through scriptconv: scriptconv has no `normalize` extra. Install `text2spoken` directly.

## What `normalize` does

`normalize(text, lang)` runs four passes in this order:

1. It expands dates and times, such as `03/08/2025` and `14h30`.
2. It splits a word from a digit that a hyphen joins, such as `sub-23`. A range such as `3-2` stays as it is.
3. It expands units and ordinal indicators, such as `10kg`, `25°C` and `1º`.
4. It reads each word, and expands contractions, titles, fractions and numbers.

Each pass is also a plain function, so a frontend can compose them and add its own rules. See [docs/api.md](docs/api.md).

The language tag selects the rules. The tables use the part before the first hyphen, so `pt-BR` and `pt-PT` share one table. `en-US` reads an ambiguous date as month first, and every other tag reads it as day first.

## Languages

These languages have tables in `text2spoken/tables.py`:

| Table | Languages |
| --- | --- |
| `CONTRACTIONS` | en |
| `TITLES` | ca, de, en, es, fr, gl, it, nl, pt |
| `UNITS` | de, en, es, fr, pt |

This command prints the same list from the installed package:

```bash
python -c "from text2spoken import CONTRACTIONS, TITLES, UNITS; [print(sorted(t)) for t in (CONTRACTIONS, TITLES, UNITS)]"
```

Numbers, dates and times come from `ovos-number-parser` and `ovos-date-parser`, so those packages set their language coverage.

To add a language, add its entries to `text2spoken/tables.py`. A new language needs no code change.

## Behaviour to know

- The library uses no network and loads no model, so it works offline.
- A language that the parsers do not support keeps its digits. The library logs an error and returns the text.
- A `text` or `lang` value of the wrong type raises `TypeError` or `AttributeError` from the code that reads it.
- Importing the library imports `ovos-date-parser`, which sets the import time.
- `ovos-config`, a dependency of `ovos-date-parser`, creates `~/.config/mycroft` at import.

## Development

```bash
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
