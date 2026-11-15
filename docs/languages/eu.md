# Basque

The file `text2spoken/lang/eu.py` reads Basque: the standard language (batua) of the Euskaltzaindia norms. Install it with `text2spoken[eu]`, which adds `ovos-number-parser`.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `eu-ES` | The one variety. Every Basque tag reads it |

The file has no variety for a dialect, so a tag such as `eu-x-zuberera` reads the standard language.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, expressions, dates, times, money, measures, percentages, Roman numerals, abbreviations and lexicon entries. Basque has no grammatical gender.

A Basque case ending joins the digits, as in `2024ko`, `25ean` and `15:00etan`, and the file joins it to the last spoken word: `2024ko martxoaren 12an` reads "bi mila eta hogeita lauko martxoaren hamabian". A Roman numeral and a full stop read as an ordinal only on evidence, such as a noun of the `roman_nouns` table after it: `XX. mendean` reads "hogeigarren mendean".

The file reads `00:00ak` as "gaueko hamabiak" and `01:00ak` as "goizeko ordu bata", with the day period. Araua 203, page 53, reads `01:00` as "gaueko ordu bata". The abbreviation `or.` always reads "orrialdea" and `pl.` "plaza", although the norm also lists other readings.

## Sources

The rules come from the norms of Euskaltzaindia, the Basque academy: Araua 7 (cardinals), Araua 196 (abbreviations), Araua 197 (symbols) and Araua 203, "Zenbakizko adierazpenak". The rule for a code noun and a number pair also cites EIMA, *Ortotipografia*, the style guide of the Basque Government. The docstring of [`eu.py`](../../text2spoken/lang/eu.py) gives the section of each rule.

In `tests/data/eu.tsv`, 123 rows cite a page of the norm, and one of them is silver. 2 rows cite EIMA, *Ortotipografia*. 7 guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

## Limits

These forms stay as written in Basque:

- A number with spaces between its groups, as in `30 000`, because the group mark of the file is the full stop.
- A range of percentages, amounts or measures, as in `10%-20%` and `5 €-10 €`. Basque marks a range with the endings `-tik` and `-ra`, and the file has no rule for them.
- An amount with the currency symbol first and a case ending, as in `€5eko`.
- A code of letters, a hyphen and digits, as in `COVID-19`. One capital letter before the hyphen reads as a sigla and a number: `A-8` reads "A zortzi".
- A Roman numeral of one letter, unless a noun of the `roman_nouns` table follows it, as in `V. mendean`, or it is `I`, `V` or `X` with a case ending after a name, as in `Elisabet I.a`. So `B. eta C. aukerak` and `I. eranskina` stay as written.
- A Roman numeral of two letters or more, unless a noun of the `roman_nouns` table, a case ending, the comma of a list, or `eta` or `edo` and a numeral that reads follows it. So `XIX., XX. eta XXI. mendeetan` reads, and `II. 1995ean sortu zen.` keeps `II.` as written.
- A Roman numeral before a noun of the `roman_nouns` table and the word `bat`, as in `XX. mende batean`. The measure reading writes one unit in that order, as `1 °C` reads "gradu bat" (Araua 203, page 21), so the noun is no evidence there.
- A clock time with no case ending and no day period, as in a timetable.

## Edge cases

The silver row is eu-002, the day-first order of a slash date with the year last, which the norm does not write. The guard rows are eu-080, eu-081, eu-082, eu-088, eu-091, eu-093 and eu-112. They hold `16:9` and `3:16`, `#decade`, `13/13/2024`, `10%-20%`, `5 €-10 €`, `€5eko` and `U2`.

---
[← Spanish](es.md) · [Home](../index.md) · [Portuguese →](pt.md)
