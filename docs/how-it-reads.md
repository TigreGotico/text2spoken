# How it reads text

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

A form that the library cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger. A wrong reading is worse than none. Here `1:23:45` is a duration, not a clock time, so it stays:

```python
>>> from text2spoken import Form, NormalizationParams, normalize
>>> normalize("The run took 1:23:45.", "en-GB")
'The run took 1:23:45.'
```

Set `NormalizationParams(strict=True)` to get an error instead of the warning. [Errors and warnings](errors.md) gives each case.

## The same input gives the same output

The output depends only on the text, the tag, the params and the tokenizer. A second pass changes nothing: `normalize(normalize(text, lang), lang)` gives the same text as one pass. The known exceptions to the second-pass rule are on the pages of the forms and the languages that have them.

## The forms

Each written form has a `Form` value. `NormalizationParams().forms` holds every form except `LETTERS` and `EMOJI`, which are off by default. A language reads only the forms that its file offers, and `supports(lang).forms` lists them. Each character of the text belongs to one form at most. When two forms find the same characters, the form whose recognizer comes first in the language file claims them, and the other form does not read them.

| Form | What it reads | Default | Languages |
| --- | --- | --- | --- |
| `LEXICON` | An entry of the `lexicon` param | On | All |
| `CARDINAL` | A whole number: `12`, `1.234`, `-5` | On | All |
| `ORDINAL` | `1º`, `3.ª`, `1st` | On | de, en, es, eu, pt, ru |
| `DECIMAL` | `3,5`, `0.5`, `.5` | On | All |
| `FRACTION` | `1/2`, `3/4` | On | All |
| `RANGE` | `18-25`, `10-20` | On | ar, de, en, es, pt |
| `EXPRESSION` | `5+3`, `2 × 2` | On | de, en, es, eu, pt |
| `DATE` | `12/03/2024`, `2024-03-12`, `15 de maio de 2025` | On | All |
| `TIME` | `às 14:30`, `14h30`, `9am`, `10 p.m.` | On | All |
| `YEAR` | A year that a word or a suffix marks: `in 1999`, `im Jahr 1999` | On | de, en, ru |
| `MONEY` | `$5`, `2,50 €` | On | All |
| `MEASURE` | `10kg`, `25°C`, `5 km/h` | On | All |
| `PERCENT` | `20%`, `4,5 %` | On | All |
| `TELEPHONE` | `+351 912 345 678`, read digit by digit | On | de, en, es, pt |
| `IDENTIFIER` | A digit run after a word that names a code, read digit by digit | On | None |
| `LETTERS` | A run of capital letters: `NATO`, `BMW`, `MP3` | Off | en, pt |
| `ABBREVIATION` | `Dr.`, `n.º`, `etc.` | On | de, en, es, eu, pt, ru |
| `IDIOM` | `24/7`, `50/50`, from a table of the language | On | de, en |
| `ROMAN` | `Luís XIV`, `XX. mendea`, `século XIX`, `Henry VIII` | On | en, eu, pt |
| `COLOR` | `#FF0000` | On | de, en, pt |
| `ELECTRONIC` | An e-mail or web address: `ann@example.com`, `www.example.org` | On | en |
| `SYMBOL` | A character with a CLDR name, such as `©`, `§` or `→`, when no other form claims it | On | en, pt |
| `EMOJI` | An emoji, by its CLDR name | Off | en, pt |

## A language with no file

A tag whose language has no file reads cardinal numbers and decimals, and keeps all other forms as written. Each number word has one owner. A language that `ovos-number-parser` writes with a module of its own reads the words of that module. Every other language reads the CLDR spell-out rules, and the table `text2spoken/data/rbnf_corrections.json` corrects the CLDR words that are wrong, with a source for each. A few languages with a module stay on the CLDR rules while the module reads a class of numbers worse. `RBNF_HELD` in `text2spoken/core/spellers.py` names them and the class. A language with neither reads only the lexicon.

A decimal reads in the decimal mark and the group mark that CLDR gives the locale, for the digits of each script. The owner of the number words reads it: `ovos-number-parser`, or the `x.x` rule of the CLDR spell-out rules. Some numbers stay as written:

- A number with one full stop or comma and three digits after it, when the locale gives the mark the other role than the CLDR root locale does. The root locale writes `1,234.5`. Such a number can be written in either convention.
- A fraction of zeros, as in `3.0`. Both owners read it as the integer, without the zeros.

| Written | Tag | Spoken |
| --- | --- | --- |
| `3.5` | `hi` | तीन दशमलव पाँच |
| `3,500` | `hi` | तीन हज़ार पाँच सौ |
| `3,5` | `nb` | tre komma fem |
| `3,500` | `nb` | stays as written |
| `1.234` | `tr` | stays as written |
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

A language with no file has no noun genders. A number before a noun takes the default form of `ovos-number-parser`, or the first CLDR cardinal rule set of `spellout-cardinal`, `spellout-cardinal-masculine` and `spellout-numbering`, whatever the gender of the noun. Agreement with the noun needs a language file that gives the genders.

## Turn forms on and off

`only` reads the forms that you name and no other:

```python
>>> normalize("Pay $5 on 12/03/2024 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
'Pay $5 on 12/03/2024 for three items.'
```

`NormalizationParams().without(Form.SYMBOL)` turns one form off, and `NormalizationParams().plus(Form.LETTERS)` turns one on. [Usage](usage.md#turn-a-form-off-or-on) shows more.

---
[← Usage](usage.md) · [Home](index.md) · [Numbers →](numbers.md)
