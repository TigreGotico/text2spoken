# Italian

The file `text2spoken/lang/it.py` reads Italian. Install `text2spoken[it]` for its number words, which come from `ovos-number-parser`, and its dates and times, which come from `ovos-date-parser`.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, percentages, expressions, dates, times, money, measures, titles, abbreviations, symbols, emoji and lexicon entries. The number 1 agrees with its noun when the file knows the gender of the noun: `un` or `uno` before a masculine noun, as the indefinite article, and `una` or `un'` before a feminine one. After a label noun, such as `pagina` or `il binario`, 1 is a label and reads `uno`. It counts the next word only when that word is a CLDR unit name, as in `la gara 1 anno fa`, or a word of `label_counted_nouns`, such as `punto` and `volta`. A unit name that is also an adverb or a preposition, as `ora` ("now"), counts only before `dopo` or `fa`: `il binario 1 ora è chiuso` reads `uno ora`, and `il cane 1 ora dopo` reads `un'ora dopo`. The genders come from a list of 59,654 Italian nouns, taken from the English Wiktionary, and from the CLDR unit names.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il Dr. Rossi ha 10 pazienti.` | `it-IT` | Il dottor Rossi ha dieci pazienti. |
| `La Sig.ra Verdi ha comprato 4 arance.` | `it-IT` | La signora Verdi ha comprato quattro arance. |
| `La Dott.ssa Neri lavora qui da 10 anni.` | `it-IT` | La dottoressa Neri lavora qui da dieci anni. |
| `Il Prof. Gallo ha 2 lezioni.` | `it-IT` | Il professor Gallo ha due lezioni. |
| `Il libro ha 21 pagine.` | `it-IT` | Il libro ha ventuno pagine. |
| `Riceverete 1 anno di abbonamento.` | `it-IT` | Riceverete un anno di abbonamento. |
| `Ho adottato 1 gatta.` | `it-IT` | Ho adottato una gatta. |
| `Porta 1 zaino.` | `it-IT` | Porta uno zaino. |
| `Ho 1 amica a Roma.` | `it-IT` | Ho un'amica a Roma. |
| `Ho visto 1 uomo.` | `it-IT` | Ho visto un uomo. |
| `Il binario 1 è chiuso.` | `it-IT` | Il binario uno è chiuso. |
| `Ha vinto la gara 1 anno fa.` | `it-IT` | Ha vinto la gara un anno fa. |
| `Leggi pagina 1 oggi.` | `it-IT` | Leggi pagina uno oggi. |
| `La partita è finita 1 a 0.` | `it-IT` | La partita è finita uno a zero. |
| `Ne ho visto 1 di loro.` | `it-IT` | Ne ho visto uno di loro. |
| `Sono 2.000.000 persone.` | `it-IT` | Sono due milioni di persone. |
| `La città conta 2.000.000 abitanti.` | `it-IT` | La città conta due milioni di abitanti. |
| `Sono arrivati 108 ospiti.` | `it-IT` | Sono arrivati centootto ospiti. |
| `Nel 2003 si è laureato.` | `it-IT` | Nel duemilatré si è laureato. |
| `Il valore è 3,14.` | `it-IT` | Il valore è tre virgola uno quattro. |
| `Ci sono 1'000 persone.` | `it-CH` | Ci sono mille persone. |
| `La strada è lunga 2.5 km.` | `it-CH` | La strada è lunga due virgola cinque chilometri. |
| `Negli anni '60 si ballava.` | `it-CH` | Negli anni 'sessanta si ballava. |
| `L'interesse è del 9%.` | `it-IT` | L'interesse è del nove per cento. |
| `I 3/4 della popolazione.` | `it-IT` | I tre quarti della popolazione. |
| `Mi dia 1/2 chilo.` | `it-IT` | Mi dia mezzo chilo. |
| `Compra 1/2 lattuga.` | `it-IT` | Compra mezza lattuga. |
| `È la 2ª volta.` | `it-IT` | È la seconda volta. |
| `Il 180º giorno.` | `it-IT` | Il centottantesimo giorno. |
| `Il 108º giorno.` | `it-IT` | Il centoottesimo giorno. |
| `Il 210º giorno.` | `it-IT` | Il duecentesimo decimo giorno. |
| `Il 1° maggio.` | `it-IT` | Il primo maggio. |
| `Nel 21° secolo.` | `it-IT` | Nel ventunesimo secolo. |
| `Abito al 3° piano.` | `it-IT` | Abito al terzo piano. |
| `Il 1/2/2003 è festa.` | `it-IT` | Il primo febbraio duemilatré è festa. |
| `Ci vediamo il 13/11.` | `it-IT` | Ci vediamo il tredici novembre. |
| `Ci vediamo il 12/03/2024 alle 14:30.` | `it-IT` | Ci vediamo il dodici marzo duemilaventiquattro alle quattordici e trenta. |
| `Ci vediamo alle 12:00.` | `it-IT` | Ci vediamo a mezzogiorno. |
| `Ci vediamo alle 1:30.` | `it-IT` | Ci vediamo all'una e trenta. |
| `Il biglietto costa 15 €.` | `it-IT` | Il biglietto costa quindici euro. |
| `Costa 1 £.` | `it-IT` | Costa una sterlina britannica. |
| `Costa 12,50 €.` | `it-IT` | Costa dodici euro e cinquanta centesimi. |
| `Costano € 2 milioni.` | `it-IT` | Costano due milioni di euro. |
| `Costa 1.000.000 €.` | `it-IT` | Costa un milione di euro. |
| `Costa 8,50 euro.` | `it-IT` | Costa otto euro e cinquanta centesimi. |
| `Costa 5 $.` | `it-IT` | Costa cinque dollari. |
| `Costa 20 CHF.` | `it-CH` | Costa venti franchi svizzeri. |
| `Il film dura 1 h.` | `it-IT` | Il film dura un'ora. |
| `Ho camminato 1 km.` | `it-IT` | Ho camminato un chilometro. |
| `4 + 5 = 9` | `it-IT` | quattro più cinque è uguale a nove |
| `Leggi l'art. 3 della Costituzione.` | `it-IT` | Leggi l'articolo tre della Costituzione. |

A title reads as the word that stands before a name, in lowercase, and takes a capital only where a clause starts. When the noun phrase has a feminine determiner, such as `la`, `sig.`, `prof.`, `dott.` and `Dr.` read the feminine word. Possessives and the adjectives of `title_adjectives`, such as `cara` and `vecchia`, may come between the determiner and the title. Any other word ends the noun phrase. With no determiner, a feminine adjective before the title makes it feminine, as in a letter heading:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il dott. Bruni è in ferie.` | `it-IT` | Il dottor Bruni è in ferie. |
| `Scrivo al sig. Mario Rossi.` | `it-IT` | Scrivo al signor Mario Rossi. |
| `Sig. Rossi, prego.` | `it-SM` | Signor Rossi, prego. |
| `La prof. Gallo insegna latino.` | `it-IT` | La professoressa Gallo insegna latino. |
| `Ho parlato con la nostra Dott. Ferri.` | `it-IT` | Ho parlato con la nostra dottoressa Ferri. |
| `Ho scritto alla sig. Rossi.` | `it-IT` | Ho scritto alla signora Rossi. |
| `La vecchia prof. Neri insegna ancora.` | `it-IT` | La vecchia professoressa Neri insegna ancora. |
| `Questa mattina Prof. Rossi ha parlato.` | `it-IT` | Questa mattina professor Rossi ha parlato. |
| `Egregia Dott. Neri, le scrivo.` | `it-IT` | Egregia dottoressa Neri, le scrivo. |

A day and a month, as `13/11`, read as a date only after a word of `date_words`, such as `il` and `dal`, and only when the day is above 12. A smaller day can also be the month of a month/day date, so the pair stays as written. `24/7` also stays as written:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Dal 31/3 il museo è chiuso.` | `it-IT` | Dal trentuno marzo il museo è chiuso. |
| `Ci vediamo il 5/6.` | `it-IT` | Ci vediamo il 5/6. |
| `Il 24/7 è un orario continuo.` | `it-IT` | Il 24/7 è un orario continuo. |

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `it-IT` (the default variety) | Comma | Full stop |
| `it-CH` | Full stop | `'` |
| `it-SM` | Comma | Full stop |

The marks of each variety come from CLDR. The varieties read the same words. In `it-CH`, a decimal point reads as a decimal. Two forms stay as written, because Italian text also writes them with the point: three digits after the point, which may be a thousands group, and an hour and two digits, which may be a clock time.

## Options

| Option | Values | Default (`it-IT`) |
| --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` |
| `clock` | `24h` | `24h` |
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

The rules cite the Vocabolario Treccani, the Enciclopedia dell'Italiano Treccani, entry "numerali", and the answers of the Accademia della Crusca. The unit names, the currency names and the symbol names come from CLDR. The gender of a noun comes from `text2spoken/data/wiktionary/it_noun_genders.json`, which `scripts/extract_noun_genders.py` makes from the categories "Italian masculine nouns" and "Italian feminine nouns" of the English Wiktionary (CC BY-SA 4.0). It also lists the words of the categories of Italian prepositions, conjunctions, adverbs, pronouns, determiners and articles. The file `text2spoken/data/wiktionary/LICENSE` gives the licence and the attribution. The docstring of [`it.py`](../../text2spoken/lang/it.py) names the entry of each rule.

Each of the 222 test rows in `tests/data/it.tsv` names a source for its reading. No native speaker has checked any row.

## Limits

Italian leaves these forms as written, or reads them as shown:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Arrivano tra 1 e 2 ore.` | `it-IT` | Arrivano tra 1 e due ore. | 1 before "e" or "o" stays as written: uno takes the gender of its noun, and the noun comes later. |
| `Siamo a 46° nord.` | `it-IT` | stays as written | `°` before a word that is not a noun of `ordinal_nouns` writes an angle or a coordinate, and `°` alone reads no unit. |
| `È il 2500000º cliente.` | `it-IT` | stays as written | An ordinal above 999999 stays as written, because no source gives the one-word form that ovos-number-parser writes for it, as "tremilionecinquecentomillesimo". |
| `Il totale è 6.000 franchi.` | `it-CH` | stays as written | In `it-CH` three digits after the point may be a thousands group. |
| `La riunione è 8.00.` | `it-CH` | stays as written | In `it-CH` an hour and two digits after the point may be a clock time. With a time word, as in `alle 8.00`, it reads as a time. |
| `Il 3,5% dei voti.` | `it-CH` | stays as written | `it-CH` reads no decimal comma. |
| `Costa 2.500 ¥.` | `it-IT` | stays as written | `¥` belongs to the yen and the yuan in CLDR, so an amount next to it stays as written. |
| `Le corsie sono larghe 3,50 metri.` | `it-IT` | Le corsie sono larghe tre virgola cinque zero metri. | The digits after the decimal mark read one by one, as the CLDR spell-out rule reads them. |
| `Antonio oggi compie 41 anni.` | `it-IT` | Antonio oggi compie quarantuno anni. | A compound in uno keeps its full form. Before a noun the short form "quarantun anni" is also correct. |
| `Ha 10.000.000 follower.` | `it-IT` | stays as written | A number that ends in a scale word reads before a noun of the noun list, its regular plural and a function word that is no noun. The loanword "follower" is in neither list, and a word that no list holds may be a verb. |

---
[← French](fr.md) · [Home](../index.md) · [Portuguese →](pt.md)
