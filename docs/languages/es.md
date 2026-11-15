# Spanish

The file `text2spoken/lang/es.py` reads Spanish. Install `text2spoken[es]` for its number words, which come from `ovos-number-parser`.

## Varieties and codes

| Tag | Decimal mark |
| --- | --- |
| `es-ES` (the default variety) | Comma |
| `es-419`, `es-MX`, `es-US` | Point |
| `es-AR`, `es-CO`, `es-CL`, `es-UY`, `es-VE`, `es-EC`, `es-BO`, `es-PY`, `es-CR` | Comma |

The decimal mark of each variety comes from CLDR: `es-419`, `es-MX` and `es-US` use the point, and the others use the comma. Another American tag, such as `es-PE`, `es-CU`, `es-SV` or `es-PA`, gets `es-419`.

The varieties also differ in the currency of `$`, the reading of `#`, the reading of the first day of the month, and the reading of a whole percentage.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, telephone numbers, abbreviations and lexicon entries. A number agrees with its noun: `uno` takes the apocope `un` before a masculine noun, and the feminine `una` and `-ientas` before a feminine noun.

## Sources

Its rules cite the RAE: the Diccionario panhispánico de dudas and the DLE. The docstring of [`es.py`](../../text2spoken/lang/es.py) names the entry of each rule.

Of the 123 test rows in `tests/data/es.tsv`, 111 name a source for their reading. The other 12 are marked silver: 11 of them say that no source was found for the reading, and two of these, es-059 and es-091, name no source at all. No native speaker has checked any row.

## Limits

Spanish leaves these forms as written or reads them in a limited way:

- A number of 10^28 or more stays as written, because no test row with a source holds such a reading. ovos-number-parser reads 10^42 + 1 as "uno por diez elevado a cuarenta y dos", the value of 10^42.
- A noun abbreviation that an integer other than one counts reads in the plural: `21 vol.` reads "veintiún volúmenes". No source states this rule. The file infers it from DPD «abreviatura» 3, which reads an abbreviation as its full word, from the plural noun in the examples of DPD «uno» 2.2, and from DPD «plural» 1. The integer counts the abbreviation only when spaces alone stand between them and no digit follows the abbreviation. So `Ver cap. 2, pág. 10` and `Ley 30 art. 21` keep the singular.
- After a decimal, a noun abbreviation keeps the singular, because no source gives the number of the noun there: `Hay 1,5 vol.` reads "uno coma cinco volumen", and `Hay 2,5 vol.` reads "dos coma cinco volumen".
- In a number grouped with spaces, only the last group counts: `Son 1 000 tel.` reads "1 000 teléfonos", but `Son 1 001 tel.` reads "1 001 teléfono". A phone number right before the abbreviation counts in the same way.
- A plural abbreviation that the table does not hold, such as `vols.` or `tels.`, stays as written.
- After a phone word, a year range reads as a phone number: `Teléfono 1990-1995.` and `Ventas de teléfonos 2019-2024.` read digit by digit.
- `D.` before a capitalised word reads `don`, also after a title that reads: `Lo dijo D. D. Palmer.` reads "Lo dijo don Don Palmer.". After an initial that stays as written, as in `J. D. Salinger`, `D.` is an initial too and stays as written.
- A title after a title takes a capital, because a full stop and a capital letter end the context of the second title: `el Sr. D. Juan` reads "el señor Don Juan".
- A round million before a participle or an adjective takes `de`, because these words are also nouns: `Tengo 2000000 ahorrados.` reads "dos millones de ahorrados".
- `1000000000` reads "un millardo", the output of ovos-number-parser. The DPD («millardo», 1) finds "mil millones" more natural.
- Only a whole number from 0 to 24 after a lowercase `la` or `las` reads as a feminine hour. `Las 21 ya pasaron.` reads "veintiuno", and `las 200 de la lista` reads in the masculine.
- An adjective after a number counts as its noun and takes the masculine: `Elige las 21 mejores.` reads "veintiún mejores".
- `primero` for the first day of the month needs `1 de` and a month name. In `del 1 al 5 de mayo`, the `1` reads `uno` in every variety. `el 01 de mayo`, `el 1° de mayo` and `el 1º de mayo` stay as written. In America, `Es la 1 de mayo.` reads "la primero de mayo".
- `#` stays as written in `es-ES`, because the reading `número` is American.
- `$` follows the 2005 text of DPD appendix 4. It stays as written in `es-419`, `es-CO`, `es-VE`, `es-BO`, `es-PY` and `es-CR`, because it can be a peso or a dollar there. `es-CU`, `es-SV` and `es-PA` get `es-419`, so `$` stays as written there too.
- In `es-419` and the varieties that get it, the comma is the group mark, so `1,5 m` and `2,50 €` stay as written.
- `es-CR` reads the point as the group mark, as `es` does. CLDR gives a space for `es_CR`, and a number grouped with spaces stays as written.
- The night starts at 20:00 for a time with `p. m.`. The DPD starts it at nightfall.

---
[← English](en.md) · [Home](../index.md) · [Basque →](eu.md)
