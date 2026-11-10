---
name: text2spoken
description: Rewrite written text into the words a speaker says. Use to read numbers, dates, times, money, measures, telephone numbers and abbreviations before phonemization, TTS or a word error rate score.
---

# text2spoken

Use this library when text must reach a phonemizer or a voice as words, with no digits or symbols, and to normalise a reference and a hypothesis before a word error rate score.

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

## Use

```python
from text2spoken import normalize

normalize("Dr Smith paid £3.50 for 2 tickets.", "en-GB")
```

The result is `Doctor Smith paid three pounds and fifty pence for two tickets.`

## Control

- Pass `NormalizationParams` to set the date order, the clock, the forms to read and a lexicon.
- Pass `tokenizer=` to use the tokens of your own frontend.
- Call `supports(lang)` to see what a tag reads, and `effective_params(lang, params)` to see the params that apply.
- Call `analyze` and then `render(analysis, hints)` to give a number the gender of its noun.

## Limits

- `en` reads every form except `ROMAN`, `LETTERS` and `IDENTIFIER`, which stay as written. `supports("en")` lists the forms. A language with no file reads cardinal numbers only.
- `fr` reads times, dates, money, measures, percentages, ordinals, decimals, fractions, ranges and abbreviations for every `fr-*` tag, with *septante* and *nonante* for `fr-BE` and `fr-CH`. It reads no telephone number, colour or Roman numeral. Give a gender hint, or `default_gender`, when a number agrees with a noun that the library does not know.
- A form that the library cannot read stays as written, with a WARNING log. `strict=True` raises `UnreadFormError`.
- The English test rows name their source, and no native speaker has checked them.
