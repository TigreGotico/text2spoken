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

- `en` reads every form except `ROMAN` and `IDENTIFIER`, which stay as written. `de` also leaves `ELECTRONIC`, `SYMBOL`, `LETTERS` and `EMOJI` as written. `nl` reads no dates, times, ranges, telephone numbers or addresses: a numeric date and a clock time stay as written, a number reads as a year only right after `in het jaar` or `anno`, and each group of a telephone number reads as a cardinal. `supports("en")` lists the forms. A language with no file reads cardinal numbers, decimals, a minus before them and lexicon entries only, and only the lexicon when CLDR has no spell-out rules for it.
- `fr` reads every form except `ELECTRONIC`, `SYMBOL`, `EMOJI`, `LETTERS` and `IDENTIFIER`, for every `fr-*` tag, with *septante* and *nonante* for `fr-BE` and `fr-CH`. Give a gender hint, or `default_gender`, when a number agrees with a noun that the file does not know.
- `el` reads cardinals in the gender and the case of their noun, a minus, percentages, common fractions and numeric dates. Money, measures, decimals and ordinals stay as written. A number with no known noun takes the neuter.
- The `EMOJI` and `LETTERS` forms read emoji and runs of capital letters in `en` and `pt`. They are off by default. Turn one on with `NormalizationParams().plus(Form.EMOJI)`.
- `it` reads no date, time or year in figures, so they stay as written.
- `ja` reads what a language with no file reads, and the decimal mark reads 点: `3.5` reads "三点五". A number next to a kanji or a kana, as in `3個`, stays as written, because the phonemizer pyopenjtalk-plus reads it with the sound of its counter.
- `zh` reads a number next to the word that follows it, as Chinese writes it. Before a measure word 2 reads 两, and a year reads digit by digit. A time stays as written, and so does a number whose reading the next word does not settle, as in `2人`.
- `ca` reads no date or time in figures, so they stay as written. A year reads as a cardinal: `L'any 2024` reads "L'any dos mil vint-i-quatre". A number before a noun reads in the masculine, and only a unit or a currency gives it another gender.
- A form that the library cannot read stays as written, with a WARNING log. `strict=True` raises `UnreadFormError`.
- The English, German and French test rows name their source, and no native speaker has checked them.

## Docs

- [Quickstart](docs/quickstart.md) and [usage](docs/usage.md).
- [How it reads text](docs/how-it-reads.md): each form, and which forms are off by default.
- [API](docs/api.md) and [errors and warnings](docs/errors.md).
- [Languages](docs/index.md#languages): the varieties, sources and limits of each language.
