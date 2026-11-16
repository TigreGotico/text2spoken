# Spanish

The file `text2spoken/lang/es.py` reads Spanish. Install `text2spoken[es]` for its number words, which come from `ovos-number-parser`.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, telephone numbers, abbreviations and lexicon entries. A number agrees with its noun: `uno` takes the apocope `un` before a masculine noun, and the feminine `una` and `-ientas` before a feminine noun.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Hay 21 libros.` | `es-ES` | Hay veintiún libros. |
| `Hay 21 casas.` | `es-ES` | Hay veintiuna casas. |
| `Hay 200 casas.` | `es-ES` | Hay doscientas casas. |
| `Mide 1,5 m.` | `es-ES` | Mide uno coma cinco metros. |
| `Mide 1.5 m.` | `es-MX` | Mide uno punto cinco metros. |
| `Llega el 12/03/2024 a las 14:30.` | `es-ES` | Llega el doce de marzo de dos mil veinticuatro a las catorce treinta. |
| `Es el 1 de mayo.` | `es-ES` | Es el uno de mayo. |
| `Es el 1 de mayo.` | `es-MX` | Es el primero de mayo. |
| `Cuesta $5.` | `es-MX` | Cuesta cinco pesos. |
| `Llame al #5.` | `es-MX` | Llame al número cinco. |
| `Subió un 100 %.` | `es-ES` | Subió un cien por cien. |
| `Subió un 100 %.` | `es-MX` | Subió un ciento por ciento. |

## Varieties

| Tag | Decimal mark |
| --- | --- |
| `es-ES` (the default variety) | Comma |
| `es-419`, `es-MX`, `es-US` | Point |
| `es-AR`, `es-CO`, `es-CL`, `es-UY`, `es-VE`, `es-EC`, `es-BO`, `es-PY`, `es-CR` | Comma |

The decimal mark of each variety comes from CLDR: `es-419`, `es-MX` and `es-US` use the point, and the others use the comma. Another American tag, such as `es-PE`, `es-CU`, `es-SV` or `es-PA`, gets `es-419`.

The varieties also differ in the currency of `$`, the reading of `#`, the reading of the first day of the month, and the reading of a whole percentage, as the table above shows.

## Options

| Option | Values | Default (`es-ES`) | Default (`es-MX`) |
| --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` | `DMY` |
| `clock` | `24h` | `24h` | `24h` |
| `minute_style` | `number`, `phrase` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `,` | `.` |
| `scale` | `long` | `long` | `long` |
| `default_gender` | `feminine`, `masculine` | `masculine` | `masculine` |
| `phone_regions` | `AE`, `BR`, `EG`, `ES`, `FR`, `GB`, `PT`, `SA`, `US` | `ES` | none |
| `register` | changes nothing | - | - |

## Sources

Its rules cite the RAE: the Diccionario panhispánico de dudas and the DLE. The docstring of [`es.py`](../../text2spoken/lang/es.py) names the entry of each rule.

Of the 123 test rows in `tests/data/es.tsv`, 111 name a source for their reading. The other 12 are marked silver: 11 of them say that no source was found for the reading. Two of the silver test rows, es-059 and es-091, name no source at all. No native speaker has checked any row.

## Limits

Spanish leaves these forms as written or reads them in a limited way:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Hay 10000000000000000000000000001 granos.` | `es-ES` | stays as written | A number of 10^28 or more stays as written, because no test row with a source holds such a reading. ovos-number-parser reads 10^42 + 1 as "uno por diez elevado a cuarenta y dos", the value of 10^42. |
| `Hay 21 vol.` | `es-ES` | Hay veintiún volúmenes | A noun abbreviation that an integer other than one counts reads in the plural. No source states this rule. The file infers it from DPD «abreviatura» 3, which reads an abbreviation as its full word, from the plural noun in the examples of DPD «uno» 2.2, and from DPD «plural» 1. |
| `Ver cap. 2, pág. 10` | `es-ES` | Ver capítulo dos, página diez | The integer counts the abbreviation only when spaces alone stand between them and no digit follows the abbreviation, so these keep the singular. |
| `Ley 30 art. 21` | `es-ES` | Ley treinta artículo veintiuno | The same rule. |
| `Hay 1,5 vol.` | `es-ES` | Hay uno coma cinco volumen | After a decimal, a noun abbreviation keeps the singular, because no source gives the number of the noun there. |
| `Hay 2,5 vol.` | `es-ES` | Hay dos coma cinco volumen | The same rule. |
| `Hay 3 vols.` | `es-ES` | Hay tres vols. | A plural abbreviation that the table does not hold, such as `vols.` or `tels.`, stays as written. |
| `Tengo 2000000 ahorrados.` | `es-ES` | Tengo dos millones de ahorrados. | A round million before a participle or an adjective takes `de`, because these words are also nouns. |
| `Hay 1000000000 granos.` | `es-ES` | Hay un millardo de granos. | This is the output of ovos-number-parser. The DPD («millardo», 1) finds "mil millones" more natural. |
| `Las 21 ya pasaron.` | `es-ES` | Las veintiuno ya pasaron. | Only a whole number from 0 to 24 after a lowercase `la` or `las` reads as a feminine hour. |
| `las 200 de la lista` | `es-ES` | las doscientos de la lista | The same rule: 200 reads in the masculine. |
| `Elige las 21 mejores.` | `es-ES` | Elige las veintiún mejores. | An adjective after a number counts as its noun and takes the masculine. |
| `del 1 al 5 de mayo` | `es-MX` | del uno al cinco de mayo | `primero` for the first day of the month needs `1 de` and a month name, so this `1` reads `uno` in every variety. |
| `el 01 de mayo` | `es-MX` | stays as written | The same rule. `el 1° de mayo` and `el 1º de mayo` also stay as written. |
| `Es la 1 de mayo.` | `es-MX` | Es la primero de mayo. | In America, this reads "la primero de mayo". |
| `Llame al #5.` | `es-ES` | stays as written | `#` stays as written in `es-ES`, because the reading `número` is American. |
| `Cuesta $5.` | `es-419` | stays as written | `$` follows the 2005 text of DPD appendix 4. It stays as written in `es-419`, `es-CO`, `es-VE`, `es-BO`, `es-PY` and `es-CR`, because it can be a peso or a dollar there. |
| `Cuesta $5.` | `es-CU` | stays as written | `es-CU`, `es-SV` and `es-PA` get `es-419`, so `$` stays as written there too. |
| `Mide 1,5 m.` | `es-419` | stays as written | In `es-419` and the varieties that get it, the comma is the group mark. |
| `Cuesta 2,50 €.` | `es-419` | stays as written | The same rule. |
| `Son 1 000 000.` | `es-CR` | stays as written | `es-CR` reads the point as the group mark, as `es` does. CLDR gives a space for `es_CR`, and a number grouped with spaces stays as written. |
| `Llega a las 8:30 p. m.` | `es-ES` | Llega a las ocho y media de la noche. | The night starts at 20:00 for a time with `p. m.`. The DPD starts it at nightfall. |

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

| Written | Spoken (`es-ES`) | Why |
| --- | --- | --- |
| `Son 1 000 tel.` | Son 1 000 teléfonos | In a number grouped with spaces, only the last group counts. |
| `Son 1 001 tel.` | Son 1 001 teléfono | The same rule. A phone number right before the abbreviation counts in the same way. |
| `Teléfono 1990-1995.` | Teléfono uno nueve nueve cero uno nueve nueve cinco. | After a phone word, a year range reads as a phone number. |
| `Ventas de teléfonos 2019-2024.` | Ventas de teléfonos dos cero uno nueve dos cero dos cuatro. | The same rule. |
| `Lo dijo D. D. Palmer.` | Lo dijo don Don Palmer. | `D.` before a capitalised word reads `don`, also after a title that reads. |
| `J. D. Salinger` | stays as written | After an initial that stays as written, `D.` is an initial too and stays as written. |
| `el Sr. D. Juan` | el señor Don Juan | A title after a title takes a capital, because a full stop and a capital letter end the context of the second title. |

---
[← English](en.md) · [Home](../index.md) · [Basque →](eu.md)
