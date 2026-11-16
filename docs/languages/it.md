# Italian

The file `text2spoken/lang/it.py` reads Italian. It needs no extra: its number words come from the CLDR spell-out rules, which the core install holds.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, percentages, expressions, money, measures, titles, abbreviations, symbols, emoji and lexicon entries. The number 1 agrees with its noun when the file knows the noun: `un` before a masculine unit, currency or scale word, and `una` before a feminine one.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il Dr. Rossi ha 10 pazienti.` | `it-IT` | Il dottor Rossi ha dieci pazienti. |
| `La Sig.ra Verdi ha comprato 4 arance.` | `it-IT` | La signora Verdi ha comprato quattro arance. |
| `La Dott.ssa Neri lavora qui da 10 anni.` | `it-IT` | La dottoressa Neri lavora qui da dieci anni. |
| `Il Prof. Gallo ha 2 lezioni.` | `it-IT` | Il professor Gallo ha due lezioni. |
| `Il libro ha 21 pagine.` | `it-IT` | Il libro ha ventuno pagine. |
| `Sono arrivati 108 ospiti.` | `it-IT` | Sono arrivati centootto ospiti. |
| `Nel 2003 si è laureato.` | `it-IT` | Nel duemilatré si è laureato. |
| `Il valore è 3,14.` | `it-IT` | Il valore è tre virgola uno quattro. |
| `Ci sono 1'000 persone.` | `it-CH` | Ci sono mille persone. |
| `L'interesse è del 9%.` | `it-IT` | L'interesse è del nove per cento. |
| `I 3/4 della popolazione.` | `it-IT` | I tre quarti della popolazione. |
| `È la 2ª volta.` | `it-IT` | È la seconda volta. |
| `Il biglietto costa 15 €.` | `it-IT` | Il biglietto costa quindici euro. |
| `Costa 1 £.` | `it-IT` | Costa una sterlina britannica. |
| `Costano € 2 milioni.` | `it-IT` | Costano due milioni di euro. |
| `Costa 20 CHF.` | `it-CH` | Costa venti franchi svizzeri. |
| `Il film dura 1 h.` | `it-IT` | Il film dura una ora. |
| `Ho camminato 1 km.` | `it-IT` | Ho camminato un chilometro. |
| `4 + 5 = 9` | `it-IT` | quattro più cinque è uguale a nove |
| `Leggi l'art. 3 della Costituzione.` | `it-IT` | Leggi l'articolo tre della Costituzione. |

A title reads as the word that stands before a name, in lowercase, and takes a capital only where a clause starts:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il dott. Bruni è in ferie.` | `it-IT` | Il dottor Bruni è in ferie. |
| `Scrivo al sig. Mario Rossi.` | `it-IT` | Scrivo al signor Mario Rossi. |
| `Sig. Rossi, prego.` | `it-SM` | Signor Rossi, prego. |

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `it-IT` (the default variety) | Comma | Full stop |
| `it-CH` | Full stop | `'` |
| `it-SM` | Comma | Full stop |

The marks of each variety come from CLDR. The varieties read the same words. In `it-CH`, a number with a decimal point stays as written, because Italian text also writes a thousands group and a clock time with the point.

## Options

| Option | Values | Default (`it-IT`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | `feminine`, `masculine` | `masculine` |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

`default_gender` sets the gender of a 1 that stands with no noun:

| Written | Tag | Spoken | Spoken (`default_gender=FrozenMap({"it": GrammaticalGender.FEMININE})`) |
| --- | --- | --- | --- |
| `Ne ho 1.` | `it-IT` | Ne ho uno. | Ne ho una. |

## Sources

The rules cite the Vocabolario Treccani and the Enciclopedia dell'Italiano Treccani, entry "numerali". The unit names, the currency names and the symbol names come from CLDR. The docstring of [`it.py`](../../text2spoken/lang/it.py) names the entry of each rule.

Each of the 82 test rows in `tests/data/it.tsv` names a source for its reading. No native speaker has checked any row.

## Limits

Italian leaves these forms as written:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Ci vediamo il 12/03/2024 alle 14:30.` | `it-IT` | stays as written | The file reads no date, time or year in figures, because ovos-date-parser has no Italian reading for them. |
| `Ho visto 1 gatto.` | `it-IT` | stays as written | 1 before a lowercase word stays as written. uno takes the gender of its noun, and the file does not know the gender of that word. |
| `Arrivano tra 1 e 2 ore.` | `it-IT` | Arrivano tra 1 e due ore. | The same rule: the noun of the 1 comes later. |
| `Mi dia 1/2 chilo.` | `it-IT` | stays as written | 1/2 before a noun is the adjective mezzo, which agrees with its noun. |
| `Costa 12,50 €.` | `it-IT` | stays as written | An amount of money with decimals stays as written, because no source of the file gives the reading of the cents. |
| `Il 150º anniversario.` | `it-IT` | stays as written | An ordinal above 100 stays as written, because the CLDR rules give the wrong word for 180. |
| `Il 1° maggio.` | `it-IT` | stays as written | The degree sign also writes an angle or a temperature, so it is no ordinal mark. Write `1º`. |
| `Fa 30° oggi.` | `it-IT` | stays as written | The same rule: `°` alone reads no unit, and `°C` reads as degrees Celsius. |
| `Il totale è 6.000 franchi.` | `it-CH` | stays as written | In `it-CH` the point is the decimal mark, and a number with a point stays as written. A text from Italy writes the thousands group with the point. |
| `La riunione è alle 8.00.` | `it-CH` | stays as written | The same rule: the point also writes a clock time. |
| `Il 3,5% dei voti.` | `it-CH` | stays as written | `it-CH` reads no decimal comma. |
| `Negli anni '60 si ballava.` | `it-CH` | stays as written | The group mark of `it-CH` is `'`, so the number of a decade written with an apostrophe gives no reading. |
| `Le banconote da 5 $ e 100 $.` | `it-IT` | stays as written | `$` and `¥` belong to more than one currency in CLDR, so an amount next to them stays as written. |
| `Le corsie sono larghe 3,50 metri.` | `it-IT` | Le corsie sono larghe tre virgola cinque zero metri. | The digits after the decimal mark read one by one, as the CLDR spell-out rule reads them. |
| `Antonio oggi compie 41 anni.` | `it-IT` | Antonio oggi compie quarantuno anni. | A compound in uno keeps its full form. Before a noun the short form "quarantun anni" is also correct. |

---
[← Basque](eu.md) · [Home](../index.md) · [Portuguese →](pt.md)
