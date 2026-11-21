# How it reads text

<!-- agent-hint
covers: the rules that hold for every form, the list of forms, and the reading of a language with no file.
source: text2spoken/core/recognizers.py, text2spoken/core/spellers.py, text2spoken/data/rbnf_corrections.json, text2spoken/data/date_readings.json
generated: no
verify: `pytest tests/test_docs_examples.py -k how-it-reads.md && python -c "import re;from text2spoken import Form,NormalizationParams;t=open('docs/how-it-reads.md').read();rows=dict(re.findall(r'^\| \x60([A-Z]+)\x60 \|.*\| (On|Off) \|$',t,re.M));d=NormalizationParams().forms;assert rows=={f.name:('On' if f in d else 'Off') for f in Form},rows"`
see: numbers.md, api.md
-->

text2spoken finds each written form that it can read, such as a number, a date or a sum of money, and replaces it with words. The rest of the text stays as it is, character for character.

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Dr Smith paid £3.50 for 2 tickets on 14 March 2024.` | Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four. |

This page gives the rules that hold for every form, and the list of forms. One page for each group of forms gives examples, options and limits:

| Page | Forms |
| --- | --- |
| [Numbers](numbers.md) | Cardinals, ordinals, decimals, fractions, ranges, expressions, Roman numerals, telephone numbers, identifiers, idioms |
| [Dates and times](dates-and-times.md) | Dates, clock times, years |
| [Money, units and symbols](money-units-and-symbols.md) | Money, measures, percentages, symbols, colours |
| [Addresses, letters and emoji](addresses-letters-and-emoji.md) | E-mail and web addresses, runs of capital letters, abbreviations, emoji |

## It does not guess

A form that the library cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger. A wrong reading is worse than none. A form is unsure when it has two readings that the context does not choose between. A form with one reading that a speaker reads with ease is not unsure: when it stays as written, that is a bug. Here `1:23:45` can be a clock time or a duration, and nothing in the sentence chooses, so it stays:

```python
>>> from text2spoken import Form, NormalizationParams, normalize
>>> normalize("The time was 1:23:45.", "en-GB")
'The time was 1:23:45.'
```

Set `NormalizationParams(strict=True)` to get an error instead of the warning. [Errors and warnings](errors.md) gives each case.

## The same input gives the same output

The output depends only on the text, the tag, the params and the tokenizer. A second pass changes nothing: `normalize(normalize(text, lang), lang)` gives the same text as one pass. The known exceptions to the second-pass rule are on the pages of the forms and the languages that have them.

## The forms

<!-- agent-hint: the forms of one language come from its file, so read supports(lang).forms and not this table. -->

Each written form has a `Form` value. `NormalizationParams().forms` holds every form except `LETTERS` and `EMOJI`, which are off by default. A language reads only the forms that its file offers. `supports(lang).forms` lists them, and each language page names them. Each character of the text belongs to one form at most. When two forms find the same characters, the form whose recognizer comes first in the language file claims them, and the other form does not read them.

| Form | What it reads | Default |
| --- | --- | --- |
| `LEXICON` | An entry of the `lexicon` param | On |
| `CARDINAL` | A whole number: `12`, `1.234`, `-5` | On |
| `ORDINAL` | `1º`, `3.ª`, `1st` | On |
| `DECIMAL` | `3,5`, `0.5`, `.5` | On |
| `FRACTION` | `1/2`, `3/4` | On |
| `RANGE` | `18-25`, `10-20` | On |
| `EXPRESSION` | `5+3`, `2 × 2` | On |
| `DATE` | `12/03/2024`, `2024-03-12`, `15 de maio de 2025` | On |
| `TIME` | `às 14:30`, `14h30`, `9am`, `10 p.m.` | On |
| `YEAR` | A year that a word or a suffix marks: `in 1999`, `im Jahr 1999` | On |
| `MONEY` | `$5`, `2,50 €` | On |
| `MEASURE` | `10kg`, `25°C`, `5 km/h` | On |
| `PERCENT` | `20%`, `4,5 %` | On |
| `TELEPHONE` | `+351 912 345 678`, read digit by digit | On |
| `IDENTIFIER` | A digit run after a word that names a code, read digit by digit. No language file reads it | On |
| `LETTERS` | A run of capital letters: `NATO`, `BMW`, `MP3` | Off |
| `ABBREVIATION` | `Dr.`, `n.º`, `etc.` | On |
| `IDIOM` | `24/7`, `50/50`, from a table of the language | On |
| `ROMAN` | `Luís XIV`, `XX. mendea`, `século XIX`, `Henry VIII` | On |
| `COLOR` | `#FF0000` | On |
| `ELECTRONIC` | An e-mail or web address: `ann@example.com`, `www.example.org` | On |
| `SYMBOL` | A character with a CLDR name, such as `©`, `§` or `→`, when no other form claims it | On |
| `EMOJI` | An emoji, by its CLDR name | Off |

## A language with no file

A tag whose language has no file reads cardinal numbers and decimals, and keeps all other forms as written. Each number word has one owner. A language that `ovos-number-parser` writes with a module of its own reads the words of that module. Every other language reads the CLDR spell-out rules, and the table `text2spoken/data/rbnf_corrections.json` corrects the CLDR words that are wrong, with a source for each. A CLDR rule set with no rule for a magnitude reads no number of that magnitude: the Serbian ordinal rules end at 400, so a say-as ordinal of 1000 or more gives the plain reading. A few languages with a module stay on the CLDR rules while the module reads a class of numbers worse. `RBNF_HELD` in `text2spoken/core/spellers.py` names them and the class. A language with neither reads only the lexicon.

A number reads in the decimal mark and the group mark that CLDR gives the locale, for the digits of each script. Each mark has one role in a locale, so `1.234` is one thousand two hundred and thirty-four in Turkish and `3,500` is three and a half in Norwegian Bokmål. Where the CLDR number pattern of the locale has a second group size, as `#,##,##0.###` in Hindi, Tamil and Indian English, `1,00,000` is one number. Groups of three read there too.

The owner of the number words reads a decimal: `ovos-number-parser`, or the `x.x` rule of the CLDR spell-out rules. `ovos-number-parser` says the decimal mark of Czech, Ukrainian, Azerbaijani and Asturian with the word for a full stop, where these locales write a comma, so `RBNF_HELD_DECIMALS` reads their decimals through the CLDR rules. CLDR has no Asturian rules, so an Asturian decimal stays as written. A fraction of zeros, as in `3.0`, stays as written too, because both owners read it as the integer, without the zeros.

| Written | Tag | Spoken |
| --- | --- | --- |
| `3.5` | `hi` | तीन दशमलव पाँच |
| `3,500` | `hi` | तीन हज़ार पाँच सौ |
| `1,00,000` | `hi` | एक लाख |
| `3,5` | `nb` | tre komma fem |
| `3,500` | `nb` | tre komma fem null null |
| `1.234` | `tr` | bin iki yüz otuz dört |
| `1,5` | `cs` | jeden čárka pět |
| `3.0` | `hi` | stays as written |

A minus before a number reads when its owner has a word for it. A hyphen between two numbers, after a letter or before a percent sign is no minus. A minus after a number or after a dash can mark a range or a code, so the minus and its number stay as written. A minus next to a currency symbol stays as written with the amount. A negative number grouped with spaces that are no group mark of the locale, as in `-1 000`, stays as written whole:

| Written | Tag | Spoken |
| --- | --- | --- |
| `-5` | `uk` | мінус п'ять |
| `-3.5` | `hi` | ऋण तीन दशमलव पाँच |
| `сьогодні -5 градусів` | `uk` | сьогодні мінус п'ять градусів |
| `код A-5` | `uk` | код A-п'ять |
| `знижка -5%` | `uk` | stays as written |
| `від 5 -10 градусів` | `uk` | stays as written |
| `Баланс: -50 €` | `uk` | stays as written |
| `температура -1 000 градусів` | `uk` | stays as written |

A language with no file reads no noun genders. A number before a noun takes the default form of `ovos-number-parser`, or the first CLDR cardinal rule set of `spellout-cardinal`, `spellout-cardinal-masculine` and `spellout-numbering`, whatever the gender of the noun. Agreement with the noun needs a language file that gives the genders. The genders of a language with no file are the genders of its ordinals, and only a say-as ordinal reads them (see below).

SSML `say-as` markup reads more forms in a language with no file, because the markup gives the evidence (see [API, say_as](api.md#say_as)). `digits` and `telephone` read each digit by its cardinal from the same owner, and `characters` keeps each letter alone, as written. `ordinal` reads the ordinal of the module, or the CLDR rule set `spellout-ordinal`, else `spellout-ordinal-masculine`, else `spellout-ordinal-common`. Where the module reads the ordinal in more than one gender, as for Polish, or CLDR has an ordinal rule set for more than one gender, as for Hindi, `default_gender` chooses the gender:

```python
>>> from text2spoken import SayAs, normalize
>>> normalize("912 345 678", "uk", say_as=SayAs(interpret_as="telephone"))
"дев'ять один два три чотири п'ять шість сім вісім"
>>> normalize("3", "uk", say_as=SayAs(interpret_as="ordinal"))
'третій'
>>> normalize("3", "hi", say_as=SayAs(interpret_as="ordinal"))
'तीसरा'
>>> from text2spoken import FrozenMap, GrammaticalGender, NormalizationParams
>>> feminine = NormalizationParams(default_gender=FrozenMap({"pl": GrammaticalGender.FEMININE}))
>>> normalize("3", "pl", feminine, say_as=SayAs(interpret_as="ordinal"))
'trzecia'
```

A `date` reads by the CLDR `long` date pattern of the language, with the month name of CLDR and the numbers of the same owner. In Danish, Finnish, Czech and Slovak the pattern writes the day as `d.`, an ordinal, so the day reads as an ordinal. Where the grammar of the language gives a form that the pattern does not show, `data/date_readings.json` gives it, with its source. The Polish day is an ordinal, the Czech day takes the genitive, and the Ukrainian day is a neuter ordinal, with the year as a genitive ordinal and `р.` read as `року`. Hungarian reads its year and day as cardinals, and Occitan puts the day first. A pattern with a field or an abbreviation that has no words and no entry in that file gives the plain reading:

```python
>>> normalize("2026-11-09", "pl", say_as=SayAs(interpret_as="date"))
'dziewiąty listopada dwa tysiące dwadzieścia sześć'
>>> normalize("2026-11-09", "cs", say_as=SayAs(interpret_as="date"))
'devátého listopadu dva tisíce dvacet šest'
>>> normalize("2026-11-09", "uk", say_as=SayAs(interpret_as="date"))
"дев'яте листопада дві тисячі двадцять шостого року"
>>> normalize("09/11/2026", "da", say_as=SayAs(interpret_as="date", format="dmy"))
'niende november to tusind og seksogtyve'
```

## Turn forms on and off

`only` reads the forms that you name and no other:

```python
>>> normalize("Pay $5 on 12/03/2024 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
'Pay $5 on 12/03/2024 for three items.'
```

`NormalizationParams().without(Form.SYMBOL)` turns one form off, and `NormalizationParams().plus(Form.LETTERS)` turns one on. [Usage](usage.md#turn-a-form-off-or-on) shows more.

---
[← Usage](usage.md) · [Home](index.md) · [Numbers →](numbers.md)
