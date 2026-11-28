# Basque

<!-- agent-hint
covers: what the Basque file reads, its varieties, options, sources and limits.
source: text2spoken/lang/eu.py, tests/data/eu.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/eu.md`
see: fr.md, ../how-it-reads.md
-->

The file `text2spoken/lang/eu.py` reads Basque: the standard language (batua) of the Euskaltzaindia norms. Its number words come from `ovos-number-parser`, which the base install holds.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, Roman numerals, abbreviations and lexicon entries. Basque has no grammatical gender.

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
| `30 000 pertsona` | hogeita hamar mila pertsona |
| `10%-20%` | ehuneko hamarretik ehuneko hogeira |
| `5 €-10 €` | bost eurotik hamar eurora |
| `10 000-20 000 bitartean` | hamar milatik hogei milara bitartean |

The file reads `00:00ak` and `01:00ak` with the day period. The file follows the table of Araua 203, page 53, which reads `01:00` with "goizeko". The worked example on the same page reads it as "gaueko ordu bata". The abbreviation `or.` always reads "orrialdea" and `pl.` "plaza", although the norm also lists other readings.

Basque has no range word. A hyphen between two amounts reads with case endings: the first end takes `-tik` and the second end takes `-ra`, as Araua 203, page 52, reads the timetable `09:00-13:00` "bederatzietatik ordu batera". Two percentages, amounts or measures read so before `bitartean` or at the end of a clause. Two bare numbers read so only before `bitartean`, because at the end of a clause they may be a score, such as `0-2`.

Araua 203, section 3.2.1.1, groups digits with a space, so a space is a group mark of the file, as the full stop is. Three groups of three digits stay as written, because that is also the shape of a telephone number: alone, after a two-digit group, or with the first group in brackets. Digit groups after a country code, such as `+34`, also stay as written. A fraction in groups after the decimal comma, or after a decimal point, stays as written.

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

Most rows in `tests/data/eu.tsv` cite a page of the norm. Some rows cite EIMA, *Ortotipografia*, and some cite it alone. A row marked silver gives a reading that the norm does not write. Guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

The silver row is eu-002, the day-first order of a slash date with the year last, which the norm does not write. The guard rows are eu-080, eu-081, eu-082, eu-093, eu-112, eu-134, eu-137, eu-138, eu-140 to eu-147 and eu-154 to eu-160. They hold `16:9` and `3:16`, `#decade`, `13/13/2024`, `€5eko`, `U2`, `¥5`, the telephone shapes `943 123 456`, `+34 944 158 155`, `+34 944 15 81 55`, `0034 943 123 456`, `34 943 123 456` and `(943) 123 456`, the grouped fractions `0,264 7`, `4 712,395 8`, `74 835,140 71` and `3.141 592 6`, and seven ranges that stay as written, such as `10%–20%`, `10 000-20 000 lagun` and `Urdinak 0-2 aitzinatu dira`.

## Limits

These forms stay as written in Basque:

| Written | Spoken (`eu-ES`) | Limit |
| --- | --- | --- |
| `+34 944 158 155` | stays as written | The file has no telephone reading, so digit groups after a country code stay as written. |
| `4 712,395 8` | stays as written | A fraction in groups after the decimal comma would read its first group alone. |
| `10 000-20 000 lagun` | stays as written | A range before a noun stays as written. The ending belongs on the noun, and no norm gives the reading. |
| `% 2-% 5 igoko da` | stays as written | A range before a verb stays as written. It may give the size of the rise, or its start and its end. |
| `1898-1900 artean` | stays as written | A range before any word other than `bitartean` stays as written. |
| `10%–20%` | stays as written | An en dash stays as written. Araua 197, note 13, gives it to the minus sign. |
| `15-20 000 bitartean` | stays as written | A first number that is less than the first group of the second may stand for thousands. |
| `20 000-30 000 €` | stays as written | A range with one symbol, after the second number only, stays as written. |
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
