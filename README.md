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

### French

French reads cardinals, ordinals, decimals, fractions, ranges, percentages, money, measures, times, dates, abbreviations and a few idioms, for every `fr-*` tag. `fr-FR`, `fr-CA` and `fr-CH` are varieties, and any other region, such as `fr-BE`, `fr-LU`, `fr-SN` or `fr-HT`, reads as `fr-FR`. Number words follow the CLDR locale of the tag, so `fr-BE` and `fr-CH` say *septante* and *nonante*, `fr-CH` says *huitante*, and every other region says *soixante-dix*, *quatre-vingts* and *quatre-vingt-dix*.

```python
normalize("Rendez-vous le 10/11/2026 à 14 h 30, pour 3,50 € ou 21 h 5.", "fr")
# 'Rendez-vous le dix novembre deux mille vingt-six à quatorze heures trente, pour trois euros cinquante ou vingt et une heures cinq.'
normalize("Il a 71 ans et 6 °C.", "fr-BE")
# 'Il a septante et un ans et six degrés Celsius.'
```

| Written | Spoken |
| --- | --- |
| `21 h`, `14h30`, `14 h 30`, `à 14:30` | vingt et une heures, quatorze heures trente (the colon form needs a time word before it) |
| `à 12 h`, `à 0 h`, `il dort 12 h` | à midi, à minuit, il dort douze heures |
| `1er`, `2e`, `3ème`, `21e`, `1re`, `2es`, `2nd` | premier, deuxième, troisième, vingt et unième, première, deuxièmes, second |
| `10/11/2026`, `le 1er mars`, `10 novembre 2026` | dix novembre deux mille vingt-six, le premier mars |
| `3,50 €`, `0,50 €`, `12 $`, `5 £`, `1 000 000 €` | trois euros cinquante, cinquante centimes, douze dollars, cinq livres, un million d'euros |
| `3,5`, `3.5`, `0,05`, `50 %`, `-3°`, `6 °C` | trois virgule cinq, zéro virgule zéro cinq, cinquante pour cent, moins trois degrés, six degrés Celsius |
| `1/2`, `3/4`, `5/8`, `5-8 kg`, `2 000 000 km` | un demi, trois quarts, cinq huitièmes, cinq à huit kilogrammes, deux millions de kilomètres |
| `M.`, `Mme`, `Dr`, `St-Denis`, `n° 5`, `etc.` | Monsieur, Madame, Docteur, Saint-Denis, numéro cinq, et cetera |

- **Agreement.** A number that ends in 1 says *un* or *une*: *vingt et un kilos*, *vingt et une heures*. The gender comes from the hint of the caller, then from the noun after the number when it is a common feminine noun (`heure`, `minute`, `fois`, `personne`, ...), then from `default_gender`, then from the file, which is masculine. A unit or a currency has its own gender. *Cent* and *quatre-vingt* take their *s* only where the grammar says: *deux cents*, *deux cent un*, *quatre-vingts*, *quatre-vingt-un*, *quatre-vingt mille*, *deux cents millions*. *Mille* does not change.
- **Group and decimal marks.** A space, a no-break space (U+00A0), a narrow no-break space (U+202F) and an apostrophe (`1'000`, as in Switzerland) group digits, three at a time. A comma and a dot both mark a decimal. A dot that repeats groups digits (`1.000.000`). A number that the marks do not settle, such as `1.500`, stays as written with a warning, because it is 1,5 or 1500. `decimal_mark="."` makes the dot the canonical mark.
- **Decimals.** One or two digits after the comma read as a number (*trois virgule quatorze*, *zéro virgule zéro cinq*), and three or more read digit by digit.
- **Times.** `h` is clock evidence by itself, so `21 h` is *vingt et une heures* as a time and as a duration. *Midi* and *minuit* come only with a time word before the hour (`à 12 h`), on the 12-hour clock and in the phrase style, so a duration `12 h` stays *douze heures*. A time that cannot be one (`25 h 99`, `24 h 30`) stays as written with a warning. `clock="12h"` adds *du matin*, *de l'après-midi*, *du soir*. `minute_style="phrase"` says *et quart*, *et demie*, *moins le quart*, and `register="colloquial"` selects it too.
- **Regions.** `fr-CA` reads `$` as the Canadian dollar and `US$` as *dollars américains*; `register="colloquial"` says *piastres* and *cennes*. `CA$` and `C$` are Canadian dollars everywhere. `fr-CH` reads `CHF`, `Fr.` and `fr.` as *francs suisses*. All regions write the date day first, read `2026-11-10` as year first, and use the 24-hour clock by default. `fr-CH` follows CLDR with *huitante* for 80, which Geneva, Neuchâtel and Jura do not use.
- Money before a number (`€ 12,50`, `CHF 1'200.50`) and after it (`12,50 €`) read the same.

French does not read Roman numerals (`XXe`), telephone numbers, colours or expressions such as `5+3`; these stay as written. The sentence rows are in `tests/data/fr.tsv` and the region matrix is in `tests/test_french.py`; no native speaker has checked them.

## Development

```bash
uv venv
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
