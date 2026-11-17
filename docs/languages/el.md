# Greek

The file `text2spoken/lang/el.py` reads Greek. It needs no extra, because its number words come from the CLDR spell-out rules.

## What it reads

The file reads cardinals, with a minus, and lexicon entries. A number takes the gender and the case of the noun that it counts: 1, 3, 4, 13, 14, the hundreds from 200 and 1000 change. With no noun, or before a word that the file does not know, a number takes the neuter, the form of counting. The genders come from a list of Greek nouns and adjectives, with their inflected forms, taken from the English Wiktionary.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Έχω 3 βιβλία.` | `el-GR` | Έχω τρία βιβλία. |
| `Έχω 3 γάτες.` | `el-GR` | Έχω τρεις γάτες. |
| `Υπάρχει 1 σκύλος εδώ.` | `el-GR` | Υπάρχει ένας σκύλος εδώ. |
| `Έχω 1 σκύλο.` | `el-GR` | Έχω έναν σκύλο. |
| `Υπάρχουν 1234 γυναίκες εδώ.` | `el-GR` | Υπάρχουν χίλιες διακόσιες τριάντα τέσσερις γυναίκες εδώ. |
| `Η βιβλιοθήκη έχει 1.234 βιβλία.` | `el-GR` | Η βιβλιοθήκη έχει χίλια διακόσια τριάντα τέσσερα βιβλία. |
| `Υπάρχουν 200 μεγάλες γάτες εδώ.` | `el-GR` | Υπάρχουν διακόσιες μεγάλες γάτες εδώ. |
| `Η τιμή των 3 βιβλίων είναι υψηλή.` | `el-GR` | Η τιμή των τριών βιβλίων είναι υψηλή. |
| `Θα σου τηλεφωνήσω στις 3 περίπου.` | `el-GR` | Θα σου τηλεφωνήσω στις τρεις περίπου. |
| `Γεννήθηκε στην Αθήνα το 1956.` | `el-GR` | Γεννήθηκε στην Αθήνα το χίλια εννιακόσια πενήντα έξι. |
| `Η 1 Μαΐου είναι αργία.` | `el-GR` | Η πρώτη Μαΐου είναι αργία. |
| `Μέτρησα ως το 4.` | `el-GR` | Μέτρησα ως το τέσσερα. |
| `Η θερμοκρασία ήταν -5 σήμερα.` | `el-GR` | Η θερμοκρασία ήταν μείον πέντε σήμερα. |

The file finds the noun in the words after the number. It skips up to two adjectives, and it skips a second number after `ή`, `έως`, `ως`, `μέχρι` or `με`, as in `3 ή 4 γυναίκες`. An article right before the number, as `τα`, `τις` or `στους`, gives the gender when no noun follows, and it decides when it and the noun disagree. A form that is only accusative or only genitive gives its case, as `σκύλους` and `βιβλίων`. A day before a month name takes the feminine of ημέρα, and day 1 reads πρώτη.

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `el-GR` (the default variety) | Comma | Full stop |

The marks come from CLDR. `el` serves every Greek tag.

## Options

| Option | Values | Default (`el-GR`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | `feminine`, `masculine`, `neuter` | `neuter` |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

`default_gender` sets the gender of a number with no noun, or with a noun that the file does not know:

| Written | Tag | Spoken | Spoken (`default_gender=FrozenMap({"el": GrammaticalGender.FEMININE})`) |
| --- | --- | --- | --- |
| `Μου έστειλε 3 emails.` | `el-GR` | Μου έστειλε τρία emails. | Μου έστειλε τρεις emails. |

## Sources

The number words come from the CLDR RBNF rule sets of `el`. The case words come from the accusative and genitive rule sets of CLDR on its main branch. Three words take the spelling of CLDR main and of the English Wiktionary: `χιλιάδες`, `ενενήντα` and `δεκατρείς`. The gender of a noun comes from `text2spoken/data/wiktionary/el_nouns.json`. The script `scripts/extract_el_nouns.py` makes that file from the categories "Greek masculine nouns", "Greek feminine nouns", "Greek neuter nouns" and "Greek adjectives" of the English Wiktionary (CC BY-SA 4.0). The inflected forms come from the Wiktextract dump at kaikki.org. The `source` field of that file names both. The rules of agreement cite Wikipedia, "Modern Greek grammar", UTS #35 and the English Wiktionary. The docstring of [`el.py`](../../text2spoken/lang/el.py) names the entry of each rule.

Each of the 71 test rows in `tests/data/el.tsv` names a source for its reading. No native speaker has checked any row.

## Limits

Greek leaves these forms as written, or reads them as shown:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Κοστίζει 5 €.` | `el-GR` | stays as written | Money, percentages, measures and numeric dates stay as written, as in a language with no file. |
| `Το υπόλοιπο είναι -50 €.` | `el-GR` | stays as written | An amount with a minus stays as written too. |
| `Πήρε 3,5 κιλά.` | `el-GR` | stays as written | The file reads no decimal. |
| `Μένω στον 2ο όροφο.` | `el-GR` | stays as written | The file reads no ordinal. |
| `Ήρθαν 200 γιατροί.` | `el-GR` | Ήρθαν διακόσιοι γιατροί. | A noun of two genders, as γιατροί, reads the masculine. When all the doctors are women, the feminine διακόσιες is right. |
| `Ήρθαν 200 φοιτητές.` | `el-GR` | Ήρθαν διακόσιοι φοιτητές. | A form that is nominative and accusative reads the nominative. After a verb that takes an object, as in `Είδα 200 φοιτητές`, the accusative διακόσιους is right. |
| `Οι σελίδες 5-10 λείπουν.` | `el-GR` | stays as written | A hyphen between two numbers writes a range, and the file holds no range word. |

---
[← German](de.md) · [Home](../index.md) · [English →](en.md)
