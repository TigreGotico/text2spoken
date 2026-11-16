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

A tag whose language has no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms as written. A language that CLDR has no spell-out rules for reads only the lexicon.

## Turn forms on and off

`only` reads the forms that you name and no other:

```python
>>> normalize("Pay $5 on 12/03/2024 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
'Pay $5 on 12/03/2024 for three items.'
```

`NormalizationParams().without(Form.SYMBOL)` turns one form off, and `NormalizationParams().plus(Form.LETTERS)` turns one on. [Usage](usage.md#turn-a-form-off-or-on) shows more.

---
[← Usage](usage.md) · [Home](index.md) · [Numbers →](numbers.md)
