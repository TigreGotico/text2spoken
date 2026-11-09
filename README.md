# text2spoken

text2spoken rewrites written text into the words that a speaker says. It reads numbers, dates, times, money, measures, telephone numbers, colours, titles and abbreviations. A phonemizer then gets words, not digits or symbols.

## Quickstart

```bash
uv pip install --prerelease=allow text2spoken
```

```python
from text2spoken import normalize

print(normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB"))
print(normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US"))
print(normalize("Ich habe 21 Äpfel.", "de"))
```

```text
Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.
Meet on March fourth twenty twenty-five at seven thirty PM.
Ich habe einundzwanzig Äpfel.
```

## Where this fits

Alone, it turns written text into spoken words with `normalize`. In the speech stack, it is the normalisation stage: a frontend or a TTS library calls it before phonemization. It calls `unicode_rbnf` to spell numbers, `quebra-frases` to tokenize, and `linguatag` with `langcodes` to read language tags.

## The API

`normalize(text, lang, params=None, tokenizer=None)` returns the spoken text. `lang` is a BCP 47 tag. A tag that is not valid BCP 47 raises `InvalidLanguageTagError`.

`analyze` and `render` split the same work in two. `analyze` returns an `Analysis` that holds the tokens and the spans it found. `render(analysis, hints)` speaks it, and `hints` maps a span start to `Features`, such as a grammatical gender. A frontend that knows the noun after a number uses the hint to make the number agree.

`supports(lang)` returns a `Support` record. It tells which file reads the tag, which forms that file reads, which genders it has, and which values each option takes. `effective_params(lang, params)` returns the params that apply to a call after the language defaults fill the empty fields.

### Params

`NormalizationParams` is a frozen dataclass. Each field that is `None` takes the default of the language variety.

| Field | Values |
| --- | --- |
| `forms` | the `Form` values to read; `params.only(Form.CARDINAL)` and `params.without(Form.TIME)` change it |
| `date_order` | `DMY`, `MDY`, `YMD` |
| `clock` | `12h`, `24h` |
| `minute_style` | `number`, `phrase` |
| `decimal_mark` | the decimal mark of the written numbers |
| `scale` | `short`, `long` |
| `default_gender` | a `FrozenMap` of language file code to `GrammaticalGender` |
| `register` | `formal`, `colloquial` |
| `phone_regions` | ISO 3166 region codes for telephone plans |
| `lexicon` | a `FrozenMap` of language tag to a `FrozenMap` of written form to spoken words |
| `strict` | `True` raises where the default mode warns or keeps the written form |

```python
from text2spoken import FrozenMap, NormalizationParams, normalize

params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"NHS": "N H S"})}))
print(normalize("Ask the NHS today.", "en-GB", params))  # Ask the N H S today.
```

A value that a language cannot produce gives a `ParameterNotHonouredWarning`, and the language default applies. In strict mode it raises `UnsupportedParameterError`. A gender that a language does not have raises `UndefinedGrammaticalGender` in both modes.

### The tokenizer hook

The tokenizer is a callable `(text, lang)` that returns a sequence of `Token(start, end, text)`. The default is `quebra-frases`. A frontend that has its own tokenizer passes it as `tokenizer=`, so that the spans and the context words follow its tokens. A token whose text does not match the text at its offsets raises `TokenizerError`.

### Written forms that stay

The library keeps a written form that it cannot read, and logs a WARNING on the `text2spoken` logger. In strict mode it raises `UnreadFormError` instead.

## Languages

Each language is one file in `text2spoken/lang/`, named by its primary subtag. `en.py` reads the forms that `supports("en")` lists, with the varieties `en-GB` and `en-US`. It does not read Roman numerals, letter codes such as `GPS` or `X5`, or a digit code after a word that names a code (the forms `ROMAN`, `LETTERS` and `IDENTIFIER`), and keeps them as written. A language with no file reads cardinal numbers through the CLDR rules of `unicode_rbnf`, and keeps all other forms as written.

This command prints what a tag reads:

```bash
python -c "from text2spoken import supports; print(supports('en-US'))"
```

`python -m text2spoken.export en` prints the data of a language file as JSON.

The 261 English rows in `tests/data/en.tsv` name their source. No native speaker has checked them, and each row says so in its `checked_by` column.

## Behaviour to know

- The library uses no network and loads no model, so it works offline.
- Importing the library imports no parser. The first call loads the language files.
- A digit run that the library cannot read for sure stays as written: the duration `1:23:45`, the short number in `Call 911 now.`, and `3/4 kg`. A count after a lowercase noun reads as a number, not a year, so `in 1234 steps` reads "one thousand two hundred and thirty-four steps".
- A second pass changes nothing: `normalize(normalize(t, lang), lang)` returns the text of the first pass. The tests check this over every row and over seeded random text.

## Development

```bash
uv venv && uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
