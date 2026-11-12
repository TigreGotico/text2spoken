# text2spoken

text2spoken rewrites written text into the words that a person says when they read it aloud. It reads numbers, dates, times, money, measures, percentages, telephone numbers, colours and abbreviations. The rest of the text stays as it is, character for character.

```python
from text2spoken import normalize

normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
# 'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
```

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

The library needs Python 3.11 or later. It uses no network and loads no model.

## Uses

### Text to speech

A voice speaks words, not digits or symbols. Normalise the text before you send it to the voice:

```python
normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
# 'Meet on March fourth twenty twenty-five at seven thirty PM.'
```

The language tag selects the reading. `en-US` reads `03/04/2025` as month, day, year. `en-GB` reads it as day, month, year.

### Phonemizers

A grapheme-to-phoneme model or a rule set expects words. A digit or a symbol has no pronunciation of its own, so the phonemizer drops it or spells it wrongly. Normalise first, then phonemize:

```python
words = normalize("It is 5 km away.", "en-GB")
# 'It is five kilometres away.'
phonemes = my_phonemizer(words)
```

### Word error rate

An ASR system writes "ten thirty" where a reference transcript writes "10:30". The two texts say the same thing, but a word error rate counts each difference as an error. Normalise the reference and the hypothesis with the same tag and the same params:

```python
ref = normalize("The train leaves at 10:30 on 3 May from platform 2.", "en-GB")
hyp = normalize("the train leaves at ten thirty on the third of may from platform two", "en-GB")
# ref: 'The train leaves at ten thirty on the third of May from platform two.'
# hyp: 'the train leaves at ten thirty on the third of may from platform two'
```

Text that is already in words does not change. The library does not change case or punctuation, so lowercase both texts and remove punctuation before you score them.

## How it reads text

The library finds each written form that it can read, and replaces it with words. It does not guess. A form that it cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger:

```python
normalize("The run took 1:23:45.", "en-GB")
# 'The run took 1:23:45.'  (a duration, not a clock time)
```

A second pass changes nothing: `normalize(normalize(text, lang), lang)` gives the same text as one pass. Output depends only on the text, the tag and the params.

## The API

| Function | Returns |
| --- | --- |
| `normalize(text, lang, params=None, tokenizer=None)` | The spoken text |
| `analyze(text, lang, params=None, tokenizer=None)` | An `Analysis` with the tokens and the spans that the library found |
| `render(analysis, hints=None)` | The spoken text of an `Analysis` |
| `supports(lang)` | A `Support` record: the forms, genders and option values of a tag |
| `effective_params(lang, params=None)` | The params of a call, with the language defaults filled in |

`lang` is a BCP 47 tag, for example `en`, `en-GB` or `pt-PT`. A tag that is not valid raises `InvalidLanguageTagError`.

### Grammatical agreement

In many languages a number agrees with its noun. `analyze` and `render` let the caller give that information. `hints` maps the start offset of a span to `Features`, for example a grammatical gender:

```python
from text2spoken import analyze, render

analysis = analyze("Gate 7 opens at 9:15.", "en-US")
[(span.start, span.end, span.form) for span in analysis.spans]
# [(5, 6, <Form.CARDINAL: 'cardinal'>), (16, 20, <Form.TIME: 'time'>)]
render(analysis)
# 'Gate seven opens at nine fifteen.'
```

### Params

`NormalizationParams` is a frozen dataclass. A field that is `None` takes the default of the language variety.

| Field | Values |
| --- | --- |
| `forms` | The `Form` values to read. `params.only(Form.CARDINAL)` and `params.without(Form.TIME)` give a changed copy |
| `date_order` | `DMY`, `MDY`, `YMD` |
| `clock` | `12h`, `24h` |
| `minute_style` | `number`, `phrase` |
| `decimal_mark` | The decimal mark of the written numbers |
| `scale` | `short`, `long` |
| `default_gender` | A `FrozenMap` of language code to `GrammaticalGender` |
| `register` | `formal`, `colloquial` |
| `phone_regions` | ISO 3166 region codes for telephone number plans |
| `lexicon` | A `FrozenMap` of language tag to a `FrozenMap` of written form to spoken words |
| `strict` | `True` raises an error where the default mode logs a warning |

A lexicon entry reads a form your way:

```python
from text2spoken import FrozenMap, NormalizationParams

params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"NHS": "N H S"})}))
normalize("Ask the NHS today.", "en-GB", params)
# 'Ask the N H S today.'
```

To read only some forms, select them:

```python
from text2spoken import Form

normalize("Pay $5 on 12/03/2024 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
# 'Pay $5 on 12/03/2024 for three items.'
```

### Errors and warnings

| Case | Default mode | `strict=True` |
| --- | --- | --- |
| An argument, a param field or a hint of the wrong type | `ArgumentTypeError` | `ArgumentTypeError` |
| A param value that no language takes, such as `date_order="mdy"` | `InvalidParameterError` | `InvalidParameterError` |
| A form that the library cannot read | Stays as written, WARNING logged | `UnreadFormError` |
| A param value that the language cannot produce | Language default, `ParameterNotHonouredWarning` | `UnsupportedParameterError` |
| A gender that a language with genders does not have | `UndefinedGrammaticalGender` | `UndefinedGrammaticalGender` |
| A hint at an offset where no span starts | `HintWarning` | `InvalidHintError` |
| A lexicon value that contains a readable form | `InvalidLexiconError` | `InvalidLexiconError` |
| A tokenizer result that is not a sequence of tokens that match the text | `TokenizerError` | `TokenizerError` |

A language with no genders ignores a gender in a hint or in `default_gender`. English and every language with no file have no genders.

Every error in this table is a subclass of `Text2SpokenError`, and so of `ValueError`. `ArgumentTypeError` is also a subclass of `TypeError`. Every warning is a subclass of `Text2SpokenWarning`. A defect in a speller or a verbalizer raises its own error, with a note that names the language, the form and the text.

### Your own tokenizer

The `tokenizer` argument takes a callable `(text, lang)` that returns a sequence of `Token(start, end, text)`. Give it when your pipeline already splits text into tokens, so that the spans and the context words follow your tokens. With no tokenizer, the library uses its default.

## Languages

Each language is one file in `text2spoken/lang/`, named by its primary language subtag. A language with no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms as written.

To see what a tag reads:

```bash
python -c "from text2spoken import supports; print(supports('en-US'))"
```

To print the data of a language file as JSON, give a BCP 47 tag. The command prints the language file that `normalize` selects for that tag:

```bash
python -m text2spoken.export en
```

If the tag is not valid, or if no language file reads the tag, the command writes one error line and exits with code 1.

English reads the varieties `en-GB` and `en-US`. It does not read Roman numerals, letter codes such as `GPS`, or codes such as `X5` after a name; these stay as written. The test rows in `tests/data/en.tsv` name their source. The `checked_by` column shows that no native speaker has checked them.

Russian reads `ru-RU`, and every other `ru-*` tag selects it. Install it with `text2spoken[ru]`, which adds `ovos-number-parser`. A number agrees in gender and case with the noun after it, and the preposition before it gives the case. A noun in the prepositional in `-е` or `-ии` does not show its gender, so `в 1 квартире` reads the masculine "одном". A gender hint gives "одной".

A date with no preposition says when something happens, so it reads in the genitive: `Он родился 12 марта` reads "двенадцатого марта", and `Экзамен был 3 июня` reads "третьего июня" (Грамматика-80, § 1168, and Розенталь 1985, § 94). The date reads in the nominative where it names the day (Грамматика-80, § 1167). It does so after a label colon, as in `Дата: 9 мая`, and when it stands alone in its clause. It is also the nominative subject after a deictic word of time, as in `Сегодня 12 марта` and `Завтра будет 1 мая` (§ 2539). After 2, 3 and 4, a noun that has only plural forms takes "двое", "трое" or "четверо": `2 суток` reads "двое суток" (Розенталь 1985, § 165). The test rows in `tests/data/ru.tsv` cite Грамматика-80, Розенталь or the 2006 spelling rules, and no native speaker has checked them.

## Development

```bash
uv venv
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
