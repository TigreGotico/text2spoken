# Catalan

<!-- agent-hint
covers: what the Catalan file reads, its varieties, options, sources and limits.
source: text2spoken/lang/ca.py, tests/data/ca.tsv
generated: no
verify: pytest tests/test_rows.py tests/test_docs_examples.py -k "ca- or ca.md"
see: de.md, ../how-it-reads.md
-->

The file `text2spoken/lang/ca.py` reads Catalan. Its number words come from `ovos-number-parser`, which the base install holds.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, money, measures, percentages, abbreviations, symbols, emoji and lexicon entries. A number reads in the masculine, unless the unit or the currency after it has another gender, or the caller gives `default_gender`.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Hi ha 22 alumnes i 43 professors.` | `ca-ES` | Hi ha vint-i-dos alumnes i quaranta-tres professors. |
| `Vam comptar 977 ocells.` | `ca-ES` | Vam comptar nou-cents setanta-set ocells. |
| `Deixa'm 1.000 euros.` | `ca-AD` | Deixa'm mil euros. |
| `Hi ha 1.000.000 de persones.` | `ca-ES` | Hi ha un milió de persones. |
| `Som a -3 graus.` | `ca-ES` | Som a menys tres graus. |
| `El 7è pis i la 3a planta.` | `ca-ES` | El setè pis i la tercera planta. |
| `El 1r. classificat.` | `ca-ES` | El primer classificat. |
| `El valor és 3,14.` | `ca-ES` | El valor és tres coma u quatre. |
| `La nota mitjana és 2,50.` | `ca-ES` | La nota mitjana és dos coma cinc zero. |
| `El 40% de la població activa.` | `ca-ES-valencia` | El quaranta per cent de la població activa. |
| `Ho vol 3/4 de la població.` | `ca-ES` | Ho vol tres quarts de la població. |
| `Va obtenir 1/3 dels vots.` | `ca-ES` | Va obtenir un terç dels vots. |
| `Costa 21 €.` | `ca-ES` | Costa vint-i-un euros. |
| `Costa 20 milions €.` | `ca-ES` | Costa vint milions d'euros. |
| `Vam pagar 10 $.` | `ca-ES-valencia` | Vam pagar deu dòlars. |
| `Pesa 3 kg.` | `ca-ES` | Pesa tres quilograms. |
| `Fa 2 h que espere.` | `ca-ES` | Fa dues hores que espere. |
| `Som a 19 °C.` | `ca-AD` | Som a dinou graus Celsius. |
| `Va a 20 km/h.` | `ca-ES` | Va a vint quilòmetres per hora. |
| `El Dr. Puig i la Dra. Vidal.` | `ca-ES` | El doctor Puig i la doctora Vidal. |
| `Porta pomes, peres, etc.` | `ca-ES` | Porta pomes, peres, etcètera. |
| `Vegeu la pàg. 24 i el núm. 5.` | `ca-ES` | Vegeu la pàgina vint-i-quatre i el número cinc. |
| `Vegeu el § 3.` | `ca-ES` | Vegeu el paràgraf tres. |
| `Vegeu els §§ 3 i 4.` | `ca-ES` | Vegeu els paràgrafs tres i quatre. |

A hyphen joins the tens and the units, and the units and the hundreds, as the Ortografia catalana of the IEC writes them. An ordinal is the number and the last letter of its word: `r`, `n`, `t` and `è` give the masculine, and `a` gives the feminine. A full stop after the letter belongs to the ordinal when a lowercase word follows.

Each digit after the decimal comma reads alone, so the zero of `2,50` stays. The digit 1 then reads "u", the name of the number. A fraction reads with the names "terç", "quart" and "quint" before `de`, `del`, `dels` or `d'`, or at the end of a clause.

An amount reads in the gender of its currency. The file gives the euro and the dollar the masculine. A unit takes its gender from CLDR, so the hour takes the feminine, as the table above shows. A number with the group mark before a word reads only when its words are the same in both genders. A scale word before the currency takes "de", as in "vint milions d'euros".

## Varieties

| Tag | Notes |
| --- | --- |
| `ca-ES` (the default variety) | Catalan of Spain, by the norm of the IEC. |
| `ca-AD` | Andorra. The words are those of `ca-ES`. |
| `ca-ES-valencia` | Valencian. The words are the forms of the IEC, which the AVL accepts. |

| Written | Tag | Spoken |
| --- | --- | --- |
| `Vam fer 8 km.` | `ca-ES-valencia` | Vam fer vuit quilòmetres. |
| `El 5è curs i la 5a fila.` | `ca-ES-valencia` | El cinquè curs i la cinquena fila. |

The Diccionari normatiu valencià of the AVL gives "huit", "dèsset" and "cinqué" first, and "vuit", "disset" and "cinquè" as accepted forms. ovos-number-parser writes the second set for every variety. The varieties take their currency and unit names from the CLDR data of their own locale.

## Options

| Option | Values | Default (`ca-ES`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | `feminine`, `masculine` | `masculine` |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

`default_gender` sets the gender of a number that stands with no noun:

| Written | Tag | Spoken | Spoken (`default_gender=FrozenMap({"ca": GrammaticalGender.FEMININE})`) |
| --- | --- | --- | --- |
| `En tinc 1.` | `ca-ES` | En tinc un. | En tinc una. |
| `En tinc 2.` | `ca-ES` | En tinc dos. | En tinc dues. |
| `En tinc 200.` | `ca-ES` | En tinc dos-cents. | En tinc dues-centes. |

The file always reads the comma as the decimal mark and the full stop as the group mark.

## Sources

The rules cite the Ortografia catalana of the Institut d'Estudis Catalans, the Diccionari normatiu valencià of the Acadèmia Valenciana de la Llengua and the guide "Abreviacions" of the Generalitat de Catalunya. Currency names, unit names and the names of symbols and emoji come from CLDR 49. The docstring of [`ca.py`](../../text2spoken/lang/ca.py) quotes the source of each rule.

Each of the 82 rows in `tests/data/ca.tsv` cites a source. 25 guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

## Limits

The file reads no dates, times, ranges, telephone numbers, identifiers, words in capitals letter by letter, idioms, Roman numerals, colours, expressions or web and email addresses. A year in figures reads as a cardinal. `supports("ca")` lists the forms it reads. Catalan also leaves these forms as written or reads them in a limited way:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Té 1 casa.` | `ca-ES` | Té un casa. | A number before a noun does not agree with the noun, because the file does not know the gender of a noun. Only a unit and a currency give a gender. |
| `Té 1.234 pàgines.` | `ca-ES` | stays as written | A number with the group mark whose words change in the feminine stays as written before a word. |
| `En tinc 21.` | `ca-ES` | En tinc vint-i-un. | ovos-number-parser writes "vint-i-un" where the name of the number is "vint-i-u". |
| `En va venir 91.` | `ca-ES` | En va venir noranta-un. | The same: the Ortografia catalana writes "noranta-u". |
| `L'acte està previst per a les 17 h.` | `ca-ES-valencia` | stays as written | A feminine number reads only when ovos-number-parser writes its correct form. The parser writes "disseta" for 17 and "vinta" for 20, so these stay as written before a feminine unit. |
| `El 101è aniversari.` | `ca-ES` | stays as written | An ordinal above 100 stays as written: the parser writes "cent primer" for 101. |
| `Els 1rs i les 2es.` | `ca-ES` | stays as written | A plural ordinal stays as written. |
| `La 2.a edició.` | `ca-ES` | stays as written | An ordinal with a full stop before its letter stays as written. |
| `Espera 1/2 hora.` | `ca-ES` | stays as written | "mig" agrees with its noun ("mitja hora"), so 1/2 before a word stays as written. |
| `Vam quedar el 3/4.` | `ca-ES` | stays as written | After `el`, `del` and the other date words, a fraction may be a date, so it stays as written. |
| `Costa 2,50 €.` | `ca-ES` | stays as written | An amount with cents stays as written. |
| `Costa 2 £.` | `ca-ES` | stays as written | CLDR gives the pound no gender, so an amount whose words change in the feminine stays as written. |
| `Costa 20 M€.` | `ca-ES` | Costa vint M€. | `M€` and `MEUR` do not read as "milions d'euros". |
| `Fa -5 €.` | `ca-ES` | Fa menys cinc €. | A negative amount reads the number and keeps the sign. |
| `Puja un +5 %.` | `ca-ES` | stays as written | No source gives the word for the sign `+`, so a number with it stays as written. |
| `Un objectiu de 35 mm.` | `ca-ES` | stays as written | CLDR names the millimetre "mil·límetre" and the millilitre "mil·lilitre", and the library reads no name with the middle dot. CLDR gives `m` to the month and to the metre, so it does not read either. |
| `Una sala de 3 × 4 cm.` | `ca-ES` | stays as written | No source gives the Catalan word for the dimension mark. |
| `La Prof. Oliver.` | `ca-ES` | stays as written | `Prof.` is "professor" or "professora", and the file does not know the gender. |
| `Vegeu ∞.` | `ca-ES` | stays as written | A CLDR name with the apostrophe ’, as "signe d’infinit", does not read. |
| `El 12/03/2024 a les 7:30.` | `ca-ES` | stays as written | ovos-date-parser reads no Catalan date or time, so a numeric date and a clock time stay as written. |
| `Hi ha 1 000 000 de persones.` | `ca-ES` | stays as written | A number with spaces between its groups stays as written. |
| `Truca al 93 123 45 67.` | `ca-ES` | Truca al 93 123 quaranta-cinc seixanta-set. | The file reads no telephone numbers. Two groups that a space parts stay as written, and each other group reads as a cardinal. |
| `El rei Lluís XIV.` | `ca-ES` | stays as written | A Roman numeral stays as written. |

---
[← Arabic](ar.md) · [Home](../index.md) · [German →](de.md)
