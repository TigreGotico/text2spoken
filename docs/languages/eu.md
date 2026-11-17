# Basque

The file `text2spoken/lang/eu.py` reads Basque: the standard language (batua) of the Euskaltzaindia norms. Its number words come from `ovos-number-parser`, which the base install holds.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, expressions, dates, times, money, measures, percentages, Roman numerals, abbreviations and lexicon entries. Basque has no grammatical gender.

A Basque case ending joins the digits, as in `2024ko`, `25ean` and `15:00etan`, and the file joins it to the last spoken word. A Roman numeral and a full stop read as an ordinal only on evidence, such as a noun of the `roman_nouns` table after it.

| Written | Spoken (`eu-ES`) |
| --- | --- |
| `2024ko martxoaren 12an` | bi mila eta hogeita lauko martxoaren hamabian |
| `Urriaren 25ean etorriko da.` | Urriaren hogeita bostean etorriko da. |
| `15:00etan hasiko da.` | arratsaldeko hiruretan hasiko da. |
| `XX. mendean` | hogeigarren mendean |
| `00:00ak dira.` | gaueko hamabiak dira. |
| `01:00ak dira.` | goizeko ordu bata dira. |
| `Ikus 5. or.` | Ikus bosgarren orrialdea. |
| `Gernikako pl. 3` | Gernikako plaza hiru |

The file reads `00:00ak` and `01:00ak` with the day period. The file follows the table of Araua 203, page 53, which reads `01:00` with "goizeko". The worked example on the same page reads it as "gaueko ordu bata". The abbreviation `or.` always reads "orrialdea" and `pl.` "plaza", although the norm also lists other readings.

## Varieties

| Tag | Notes |
| --- | --- |
| `eu-ES` | The one variety. Every Basque tag reads it |

The file has no variety for a dialect, so a tag such as `eu-x-zuberera` reads the standard language.

## Options

| Option | Values | Default (`eu-ES`) |
| --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` |
| `clock` | `12h`, `24h` | `12h` |
| `minute_style` | `number` | `number` |
| `decimal_mark` | `,` | `,` |
| `scale` | `long` | `long` |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

## Sources

The rules come from the norms of Euskaltzaindia, the Basque academy: Araua 7 (cardinals), Araua 196 (abbreviations), Araua 197 (symbols) and Araua 203, "Zenbakizko adierazpenak". The rule for a code noun and a number pair also cites EIMA, *Ortotipografia*, the style guide of the Basque Government. The docstring of [`eu.py`](../../text2spoken/lang/eu.py) gives the section of each rule.

Of the 132 rows in `tests/data/eu.tsv`, 123 cite a page of the norm, and one of them is silver. 15 rows cite EIMA, *Ortotipografia*, and 2 of them cite it alone. 7 guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

The silver row is eu-002, the day-first order of a slash date with the year last, which the norm does not write. The guard rows are eu-080, eu-081, eu-082, eu-088, eu-091, eu-093 and eu-112. They hold `16:9` and `3:16`, `#decade`, `13/13/2024`, `10%-20%`, `5 €-10 €`, `€5eko` and `U2`.

## Limits

These forms stay as written in Basque:

| Written | Spoken (`eu-ES`) | Limit |
| --- | --- | --- |
| `30 000 pertsona` | stays as written | The group mark of the file is the full stop, so a number with spaces between its groups stays as written. |
| `10%-20%` | stays as written | A range of percentages, amounts or measures stays as written. Basque marks a range with the endings `-tik` and `-ra`, and the file has no rule for them. |
| `5 €-10 €` | stays as written | The same rule. |
| `€5eko` | stays as written | An amount with the currency symbol first and a case ending stays as written. |
| `COVID-19` | stays as written | A code of letters, a hyphen and digits stays as written. |
| `A-8 errepidea` | A zortzi errepidea | One capital letter before the hyphen reads as a sigla and a number. |
| `B. eta C. aukerak` | stays as written | A Roman numeral of one letter stays as written, unless a noun of the `roman_nouns` table follows it, or it is `I`, `V` or `X` with a case ending after a name. |
| `I. eranskina` | stays as written | The same rule. |
| `V. mendean` | bosgarren mendean | A noun of the `roman_nouns` table follows it, so it reads. |
| `Elisabet I.a` | Elisabet lehena | `I`, `V` or `X` with a case ending after a name reads. |
| `XIX., XX. eta XXI. mendeetan` | hemeretzigarren, hogeigarren eta hogeita batgarren mendeetan | A Roman numeral of two letters or more reads before a noun of the `roman_nouns` table, a case ending, the comma of a list, or `eta` or `edo` and a numeral that reads. |
| `II. 1995ean sortu zen.` | II. mila bederatziehun eta laurogeita hamabostean sortu zen. | With none of these after it, it stays as written. |
| `XX. mende batean` | stays as written | A Roman numeral before a noun of the `roman_nouns` table and the word `bat` stays as written. The measure reading writes one unit in that order, as `1 °C` reads "gradu bat" (Araua 203, page 21), so the noun is no evidence there. |
| `Trena 15:00 irteten da.` | stays as written | A clock time with no case ending and no day period stays as written, as in a timetable. |

---
[← Spanish](es.md) · [Home](../index.md) · [French →](fr.md)
