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

`de` serves every German tag. `de-DE` is the default. `de-AT` says `Jänner` for January. `de-CH` writes `ss` for `ß` and takes `.` as the decimal mark. A German number takes the gender and the case of its noun, as in `für einen Tag` and `mit einer Frau`. The word before the number gives the case. `in`, `an` and `vor` give the dative only before a noun of time, as in `vor einer Stunde`. A form of the verb `kosten` gives the accusative to a price, so `Das kostet 1 €.` reads "einen Euro". Any other noun after the verb is its subject, so `Wie viel kostet 1 Kaffee?` reads "ein Kaffee". A noun with no known gender takes the masculine, and only the dative of a preposition, so `zu 1 Freund` reads "einem Freund". In `de-CH` the full stop is also the decimal mark, so a time with a full stop needs `Uhr`: `um 14.30 Uhr` is a time, and `um 1.15 Franken` reads "eins Komma eins fünf Franken". `von`, `bis`, `ab` and `seit` also come before a ratio, so a time after them needs `Uhr` or a range that `Uhr` closes, as in `von 9:00 bis 17:00 Uhr`.

Some German readings are still wrong or stay as written:

- A verb gives no case, except `kosten`. `Ich habe 1 Hund.` reads "ein Hund", not "einen Hund". `Ich erinnere mich an 1 Tag im Mai.` reads "einem Tag", but `sich erinnern an` takes the accusative.
- A price that is the subject of `kosten` takes the accusative. `Wie viel kostet 1 Euro in Dollar?` reads "einen Euro".
- `in`, `an` and `vor` before a noun that is not a noun of time give no case. `Er wohnt in 1 Haus.` reads "ein Haus".
- A noun whose gender no rule gives takes the masculine. `mit 1 Freundin` reads "einem Freundin", and `1 Ampel` reads "ein Ampel". A `default_gender` param or a gender hint gives the feminine.
- A compound of an exception takes the ending rule, so `1 Osterei` reads "eine Osterei". A noun with `Ge-` that is not neuter reads as a neuter, so `1 Gerade` reads "ein Gerade", and `Mit 1 Gelatine.` reads "einem Gelatine".
- A preposition of the genitive gives no case to a number. `Während 1 Woche` and `Innerhalb 1 Woche` read "eine Woche". In `de-CH`, `Außerhalb der 3. Woche` with `ß` reads "dritte", because the `de-CH` tables write `ss`.
- `h`, `min` and `Std.` are not units. `Er kommt in 1 h.` reads "in eins h", `Er kam vor 1 min.` reads "vor eins min", and `1 Std.` reads "ein Std.".
- A minus sign between spaces stays as written. `5 - 3 = 2` reads "fünf - drei gleich zwei".
- A number with a space as the group mark stays as written, as in `10 000`.
- In `de-CH`, a time with a full stop and no `Uhr` reads as a decimal. `um 9.15` reads "neun Komma eins fünf".
- A time after `ab`, `von`, `bis` or `seit` with no `Uhr` stays as written, as in `Ab 16:10`. `9:00-17:00 Uhr` stays as written, because the core reads the dash as a joiner.
- One half before a noun stays as written, as in `1/2 Pizza`, because `halb` declines before a noun.
- A scale abbreviation after a number stays as written. `2 Mio. Einwohner` reads "zwei Mio. Einwohner", and `2 Mio. €` reads "zwei Mio. €".
- A year with no year word reads as a cardinal. `Er wurde 1999 geboren.` reads "eintausendneunhundertneunundneunzig".
- An ordinal from one million up stays as written, and so does an ordinal with no determiner before it, as in `Er wurde 2. Sieger.`
- A determiner that does not agree with a date is ignored. `das 12/03/2024 Wetter` reads "das zwölfter März zweitausendvierundzwanzig Wetter".
- The core table `PHONE_PLANS` holds no plan for DE, AT or CH.

The test rows in `tests/data/de.tsv` cite the Regelwerk, Duden, Wiktionary or Wikipedia, and no native speaker has checked them.

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

English and Portuguese take the words for units from the Unicode CLDR, release 49. The data ships in `text2spoken/data/cldr/` under the Unicode License v3, and `scripts/extract_cldr.py` writes it. A unit symbol that cannot be a word, such as `km/h`, `°C`, `kWh` or `µm`, reads with no list. A symbol made only of letters reads only when the language file lists it in `unit_symbols`, so `1 in 3` and `29 GB golds` keep `in` and `GB`. `a/b` reads with the `per` pattern, and `²` and `³` read with the square and cubic patterns: `10 kg/m²` reads "ten kilograms per square metre", and `5 µm` reads "cinco micrómetros" in `pt-PT`. A Portuguese number takes the gender of its unit, so `2 h` reads "duas horas". In `en-US`, `5 ml` stays as written, because CLDR writes the American symbol as `mL`.

Russian reads `ru-RU`, and every other `ru-*` tag selects it. Install it with `text2spoken[ru]`, which adds `ovos-number-parser`. A number agrees in gender and case with the noun after it, and the preposition before it gives the case. A noun in the prepositional in `-е` or `-ии` does not show its gender, so `в 1 квартире` reads the masculine "одном". A gender hint gives "одной".

A date with no preposition says when something happens, so it reads in the genitive: `Он родился 12 марта` reads "двенадцатого марта", and `Экзамен был 3 июня` reads "третьего июня" (Грамматика-80, § 1168, and Розенталь 1985, § 94). A date that closes its clause reads in the nominative in two places. Only "года", closing quotes and one of the marks ". ! ? …", or the end of the clause, follow such a date. A date before a comma reads in the genitive, because the clause often goes on after the comma: `1 мая, в субботу, мы поехали на дачу` and `Тогда, 1 мая, мы уехали` read "первого мая". The first place is after a label colon, where the date names the day (§ 1167): `Дата: 9 мая.` reads "девятое мая". The second place is where the date is the subject of "был", "была", "было", "будет", "есть" or a form of "наступить" (§ 2536, § 2539, § 2681). In that clause only these verbs and words such as "а", "но", "ведь", "вот", "и", "ли", "наконец", "уже", "сегодня" and "завтра" come before the date. So `Вот и наступило 1 сентября` reads "первое сентября", and `Сегодня уже 1 мая` reads "первое мая". A date alone in its clause is a nominative sentence (§ 2522, § 2524), so `1 мая.` and `Почему магазин закрыт? Ведь 1 мая!` read "первое мая". After only "да" or "а", the date reads in the genitive, because a reply takes its form from the question (§ 1954): `Да, 1 мая.` reads "первого мая". Only the words after the last colon or opening quote count, so `Он сказал: «Сегодня 1 мая».` reads "первое мая". A subject before the verb, or a word after the date, makes the date a time again: `Лето наступило 1 июня` and `Было 1 мая подписано соглашение` read the genitive. The pronoun "это" is a subject too (Розенталь 1985, § 189), so `Это было 1 мая` reads "первого мая". After 2, 3 and 4, a noun that has only plural forms takes "двое", "трое" or "четверо": `2 суток` reads "двое суток" (Розенталь 1985, § 165). The nouns "детей", "ребят" and "людей" take them only where the number is the subject. That is the case first in the clause, after "было", and after a phrase with "у", "в" or "во" that opens the clause: `У моей сестры 2 детей` reads "двое детей", and `В семье 3 детей` reads "трое детей" (Грамматика-80, § 2455). After a verb or a preposition of the accusative, as in `Я видел 2 детей` and `Я видел в парке 2 детей`, the number stays as written. Another preposition takes the cardinal in its case: `Для 2 детей` reads "для двух детей" (Грамматика-80, § 1366). A sign reads "плюс" or "минус".

Some Russian readings are still wrong:

- `Нас было 2` reads "два", not "двое".
- An object before the verb, as in `3 детей я видел`, reads "трое", not "троих".
- An adverb before the adjective, as in `2 очень маленьких детей`, hides the noun, so the number reads "два".
- A date before a dash reads in the genitive, also after "сегодня": `Сегодня 1 мая — День весны` reads "первого мая".
- A date before a comma, a colon or a bracket reads in the genitive, also where it is the subject: `Было 1 мая, шёл дождь`, `Сегодня 1 мая, в субботу, мы идём на парад`, `«Сегодня 1 мая», — сказал он` and `Сегодня (1 мая) праздник`. A dateline such as `1 мая, вторник` and a label before a comma such as `Дата: 9 мая, вторник` read in the genitive too.
- `Да здравствует 1 мая!` reads "первого", although the date is the subject of "здравствует".
- A quoted title of a date word before the date makes the date read in the nominative: `«Завтра» 1 мая.` and `Я купил «Завтра» и «Сегодня» 1 мая.` read "первое".
- A date after a comma with no space is not taken as a date, so the number reads as a cardinal: `Он сказал: «Сегодня,1 мая».` reads "Сегодня,одна мая".
- A phrase with "у", "в" or "во" that does not open the clause stays as written: `В семье у нас 3 детей`. So does a phrase that the three words before the number do not show whole: `У нас в семье 3 детей`.
- The prepositional in `-е` or `-ии` and some nouns in `-ь` read masculine without a gender hint.
- A count after a verb reads the nominative, and an animate accusative reads the cardinal.

The test rows in `tests/data/ru.tsv` cite Грамматика-80, Розенталь or the 2006 spelling rules, and no native speaker has checked them.

## Development

```bash
uv venv
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
