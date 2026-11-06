---
name: text2spoken
description: Rewrite written text into the words a voice speaks. Use to expand numbers, dates, times, units, titles and contractions before phonemization or TTS.
---

# text2spoken

Use this library when text must reach a phonemizer as words, with no digits or symbols.

## Install

```bash
pip install --pre text2spoken
```

## Use

```python
from text2spoken import normalize

normalize("Dr. Smith paid 3/4 of the bill at 25°C.", "en")
```

The result is `Doctor Smith paid three quarters of the bill at twenty five degrees celsius.`

## Compose

A frontend can run one pass and add its own rules around it. The plain functions are `expand_dates_and_times`, `expand_hyphen_digits`, `expand_units` and `expand_word`. See `docs/api.md`.

## Limits

- A language that the parsers do not support keeps its digits. The call logs an error and raises nothing.
- Tables cover a fixed set of languages. Read `TITLES`, `UNITS` and `CONTRACTIONS` for the list.
- Add a language in `text2spoken/tables.py`. It needs no code change.
