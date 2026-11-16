# English

The file `text2spoken/lang/en.py` reads English. It needs no extra: its number words come from the CLDR spell-out rules.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `en-GB` | The default variety. A bare `en` reads as `en-GB`. Reads `12/03/2024` day first, and "one hundred and one" |
| `en-US` | Reads `12/03/2024` month first, and "one hundred one" |

Every other `en-*` tag reads the variety that `linguatag.closest_lang` gives it, so `en-AU` reads `en-GB`.

## What it reads

The file reads every form except identifiers. The `LETTERS` and `EMOJI` forms are off by default, as in every language. A letter code such as `GPS` or `X5` stays as written, unless the `LETTERS` form is on. [How it reads text](../how-it-reads.md) describes the addresses, the emoji, and the units, currencies and symbols of CLDR, which English reads.

## Sources

Number words come from CLDR RBNF. Unit words, currency names and symbol names come from CLDR 49. The names of the address symbols come from Wiktionary, and the letter names from Wikipedia, "English alphabet", which gives them from the Oxford English Dictionary. The syllable rule of the `LETTERS` form follows Wikipedia, "English phonology" and "English orthography". The docstring of [`en.py`](../../text2spoken/lang/en.py) gives each source.

The test rows in `tests/data/en.tsv` name their source. The `checked_by` column shows that no native speaker has checked them. There are 521 rows.

## Roman numerals

A Roman numeral reads when the word before it shows that it is a number. After a regnal title and a capitalised name, or after a name of the `regnal_names` table, it is a regnal number. It reads "the" and an ordinal. So `Henry VIII had six wives.` reads "Henry the Eighth had six wives.", and `King Charles III spoke.` reads "King Charles the Third spoke." After any other capitalised word, or after a noun of the `roman_nouns` table, it reads as a cardinal. So `World War II` reads "World War Two", and `Super Bowl LVII` reads "Super Bowl Fifty-Seven". Wikipedia, "Roman numerals", and the BBC News style guide give these readings.

A numeral of one letter reads only after a regnal title and a name, and after a noun of two words such as `World War`. So `Malcolm X spoke.` and `The book I read.` stay as written. A numeral that is also an acronym, such as `DC`, `CD` or `MD`, reads only after a regnal title and a name, so `Fly to Washington DC.` stays as written. A measurement over the FLORES+ devtest and "meio milhão de frases" gives that list.

Known limits of the form in English:

- A generational suffix reads as a cardinal, because the name before it is in no table. `Taft IV` reads "Taft Four".

## Runs of capital letters

A run that splits into English syllables stays as written, and any other run reads letter by letter. A table in the language file holds the runs that the rule reads wrong: `CIA`, `IRS`, `USA`, `IBS` and `IDS` read letter by letter. In English, an e-mail or web address reads as an address, and not as a run.

Known limits of the form in English:

- The rule reads some initialisms as words, because no source in the language file names them: `CEO` and `WHO` stay as written in English.
- In English, a coda takes the s of the -s/-z morpheme. So the rule reads some three-letter initialisms of a vowel, a consonant and s as words: `ABS` and `ITS` stay as written. `letter_runs` lists the ones that a source spells, such as `IBS` and `IDS`.

The limits that English shares with Portuguese are on the [How it reads text](../how-it-reads.md#runs-of-capital-letters) page. [Edge cases](#edge-cases) gives how English phonemizers read the letter names.

## Limits of units, currencies and symbols

- `ft` does not read as feet, because `ft.` also names "featuring" in a music credit, as in `Maroon 5 ft. Cardi B`.
- A unit before a noun reads in the plural. `A 5 µm hole.` reads "A five micrometres hole".
- A euro amount with a comma for the decimal mark stays as written in English, as in `€12,50`.

The limits that English shares with Portuguese are on the [How it reads text](../how-it-reads.md#units-currencies-and-symbols) page.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

### Letter names in English phonemizers

- Some English letter names do not read right in every English phonemizer, and no other spelling that Wiktionary gives as the name reads right in more of them. misaki does not know `ef` (F) or `ar` (R). In `double-u` (W), orthography2ipa reads `double` with the vowel of "out" on its rules alone, and g2p_en drops the /j/. An address reads the same names.
- `a`, the name of A, reads as the article inside a phrase. So `nine a em` and `a at bee dot com` read the article in every English phonemizer measured. Before a full stop, espeak-ng and misaki read `a` as the letter name, as in `u ess a.` for `the USA.`. The other spelling `ay` reads as "aye", the name of I, in espeak-ng, so the table keeps `a`.

### Addresses on a second pass

A word of a spoken address can become the key or the context of another form on a second pass, so the second pass changes the first. Four cases are known:

- The last label and the full stop after it can form an abbreviation. `See a@b.etc.` reads "See a at bee dot etc.", and a second pass reads "et cetera".
- A final `@` reads "at", and a second pass takes it as the time word of a time after it. Only spaces or punctuation can stand between them. `Write x.com@ 9:30` reads "Write ex dot com at 9:30", and a second pass reads "nine thirty". `Write x.com@ (9:30)` gives the same result inside the brackets.
- A month name as the first or the last label of an address forms a date with the digits next to it on a second pass. `See example.com/May 05 for details.` reads "See example dot com slash May 05 for details.", and a second pass reads "May fifth". `On 05 May@x.com we met.` reads "On 05 May at ex dot com we met.", and a second pass reads "the fifth of May".
- A Roman numeral that an address keeps as written, or that has the end of an address as its context, reads on a second pass. `Chapter XIV٢http://x` reads "Chapter XIV two aitch tee tee pee colon slash slash ex", and a second pass reads "Fourteen".

### Currency signs next to other text

- A currency sign at the start or the end of an address stays as written in the address, and a second pass reads it with the number next to it. `x@€ 08` reads "ex at € 08", and a second pass reads "ex at eight euros". The same holds for the signs of the CLDR currencies: `x@₦ 08` reads "ex at ₦ 08", and a second pass reads "ex at eight Nigerian nairas".
- A money range whose last amount ends in a letter code, with a joiner and a digit after it, stays as written, and the amount after the joiner reads. A second pass reads the range. `$0–0USD+2$` reads "$0–0USD+two dollars", and a second pass reads "zero dollars to zero dollars+two dollars".
- An amount right before a run of digits that starts with `0` reads, and the run stays as written. A second pass reads the run digit by digit. `€2 07946001800` reads "two euros 07946001800", and `USD20 07946001800` reads "twenty dollars 07946001800".
- With the `LETTERS` form on, an amount before a symbol and digits can stay as written while the symbol and the digits read. `US$0 0∇2` reads "US$0 0 nabla two", and a second pass reads "zero dollars zero nabla two".

The edge cases that English shares with Portuguese are on the [How it reads text](../how-it-reads.md#edge-cases) page.

---
[← German](de.md) · [Home](../index.md) · [Spanish →](es.md)
