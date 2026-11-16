# French

The file `text2spoken/lang/fr.py` reads French. Its number words come from the CLDR spell-out rules, which the core dependency `unicode-rbnf` holds. The `fr` extra declares the floor of that dependency.

```python
normalize("Rendez-vous le 10/11/2026 à 14 h 30, pour 3,50 € ou 21 h 5.", "fr")
# 'Rendez-vous le dix novembre deux mille vingt-six à quatorze heures trente, pour trois euros cinquante ou vingt et une heures cinq.'
normalize("Il a 71 ans et 6 °C.", "fr-BE")
# 'Il a septante et un ans et six degrés Celsius.'
```

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `fr-FR` | The default variety. Every region with no variety of its own, such as `fr-BE`, `fr-LU`, `fr-SN` or `fr-HT`, reads as `fr-FR` |
| `fr-CA` | Reads `$` as the Canadian dollar and `US$` as *dollars américains*. Reads a telephone number digit by digit |
| `fr-CH` | Reads `CHF`, `Fr.` and `fr.` as *francs suisses* |

`fr` serves every French tag. The number words follow the CLDR locale of the tag, so `fr-BE` and `fr-CH` say *septante* and *nonante*, `fr-CH` says *huitante*, and every other region says *soixante-dix*, *quatre-vingts* and *quatre-vingt-dix*.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, percentages and per mille, money, measures, times, dates, years, telephone numbers, colours, Roman numerals, abbreviations, idioms and lexicon entries. It does not read addresses, symbols, emoji, letter codes or identifiers.

| Written | Spoken |
| --- | --- |
| `21 h`, `14h30`, `14 h 30`, `à 14:30` | vingt et une heures, quatorze heures trente |
| `à 12 h`, `à 0 h`, `il dort 12 h` | à midi, à minuit, il dort douze heures |
| `1er`, `2e`, `3ème`, `21e`, `1re`, `2es`, `2nd` | premier, deuxième, troisième, vingt et unième, première, deuxièmes, second |
| `10/11/2026`, `le 1er mars`, `10 novembre 2026` | dix novembre deux mille vingt-six, le premier mars, dix novembre deux mille vingt-six |
| `3,50 €`, `0,50 €`, `12 $`, `5 £`, `1 000 000 €` | trois euros cinquante, cinquante centimes, douze dollars, cinq livres, un million d'euros |
| `3,5`, `0,05`, `50 %`, `-3°`, `6 °C` | trois virgule cinq, zéro virgule zéro cinq, cinquante pour cent, moins trois degrés, six degrés Celsius |
| `1/2`, `3/4`, `5/8`, `5-8 kg`, `2 000 000 km` | un demi, trois quarts, cinq huitièmes, cinq à huit kilogrammes, deux millions de kilomètres |
| `M.`, `Mme`, `Dr`, `St-Denis`, `n° 5`, `etc.` | Monsieur, Madame, Docteur, Saint-Denis, numéro cinq, et cetera |

A number that ends in 1 says *un* or *une* with its noun: *vingt et un kilos*, *vingt et une heures*. The gender comes from the hint of the caller, then from the noun after the number when the table `feminine_nouns` holds it, then from `default_gender`, and then from the file, which is masculine. A unit and a currency carry their own gender. A half before a noun takes the gender of the noun: `1/2 heure` reads *une demi heure*.

*Cent* and *quatre-vingt* take their *s* only where the grammar says: *deux cents*, *deux cent un*, *quatre-vingts*, *quatre-vingt-un*, *quatre-vingt mille*, *deux cents millions*. A numeral that stands for an ordinal keeps both singular: a year, *en mille neuf cent quatre-vingt*, an ordinal, *deux cent millionième*, and a number after *page*, *p.* or *an*, *page quatre-vingt* and *l'an huit cent*. The Académie française names these two nouns.

A space, a no-break space, a narrow no-break space and an apostrophe (`1'000`, as in Switzerland) group the digits of a number, three at a time. So `1 000` is one number and `70 90 80` is three. A range, a fraction and an expression read a number grouped with a space whole: `1 000-2 000` is *mille à deux mille*, and `1 000 + 500` is *mille plus cinq cents*. A comma and a full stop both mark a decimal, and a full stop that repeats groups digits, as in `1.000.000`. A number that the marks do not settle, such as `1.500`, stays as written with a warning, because it is 1,5 or 1500. A narrow no-break space may also stand between a number and its unit, its currency, its percent sign or its scale word.

One or two digits after the decimal mark read as a number, *trois virgule quatorze*, and three or more read digit by digit.

The letter `h` is evidence of a time by itself, so `21 h` is *vingt et une heures* as a time and as a duration. The colon form needs a time word before it, such as `à`, `vers` or `dès`. *Midi* and *minuit* come only with a time word or *est* before the hour, on the 12-hour clock and in the phrase style. So `il est 12 h` reads *il est midi*, and a duration `12 h` stays *douze heures*. `clock="12h"` adds *du matin*, *de l'après-midi* or *du soir*. `minute_style="phrase"` and `register="colloquial"` say *et quart*, *et demie* and *moins le quart*.

Telephone numbers read in pairs: `06 12 34 56 78` is *zéro six douze trente-quatre cinquante-six soixante-dix-huit*. A group of one or three digits reads digit by digit. A short code of three digits reads as one number: `Composez 112.` is *Composez cent douze.* `fr-CA` reads every digit. A number reads when a phone word stands right before it, when it has the French national shape, a country code, or the trunk prefix of the region of the tag. The file adds the numbering plans of Belgium, Canada and Switzerland to those of the core.

An ordinal marker after a Roman numeral is the evidence that it is a number: `XXe siècle` is *vingtième siècle* and `Ve République` *cinquième République*. A bare numeral reads after the first name of a sovereign or a pope, as in `Louis XIV`, and after a heading word, as in `Acte II`.

In `fr-CA`, `register="colloquial"` says *piastres* and *cennes*.

## Sources

The rules cite the Académie française (Questions de langue, "Nombres" and "Deuxième, second"), the Wiktionnaire, the Lexique des règles typographiques en usage à l'Imprimerie nationale, the SI Brochure of the BIPM, CLDR, ITU-T E.164 and the ARCEP numbering plan. The docstring of [`fr.py`](../../text2spoken/lang/fr.py) gives each rule family its source.

The test rows in `tests/data/fr.tsv` name their source. Most of them say that the rule comes from memory and that no source was fetched, and no native speaker has checked any row. `tests/test_french_sources.py` compares the cardinals, ordinals, month names, unit names and currency names with `num2words`, `ovos-number-parser` and CLDR through Babel.

## Limits

Some French readings are wrong or stay as written:

- `est` and `pour` are no time words, because they also come before a ratio or a quantity. `Il est 7:30.` and `Réglée pour 7:30.` stay as written. `Il est 7 h 30.` reads.
- A range after `entre` reads with `à`: `entre 10 %-20 %` reads *entre dix pour cent à vingt pour cent*, where French says *entre ... et ...*.
- A half after a whole number and its noun reads apart: `2 ans 1/2` reads *deux ans un demi*, where French says *deux ans et demi*.
- A fraction other than a half before a noun reads with no *de*: `1/4 heure` reads *un quart heure*.
- A short code after `le` and before another word reads as a cardinal: `Composez le 3615 maintenant.` reads *trois mille six cent quinze*.
- A date with a two-digit year, such as `10/11/26`, stays as written.
- `fr-CH` follows CLDR with *huitante* for 80, which Geneva, Neuchâtel and Jura do not use.

---
[← Basque](eu.md) · [Home](../index.md) · [Portuguese →](pt.md)
