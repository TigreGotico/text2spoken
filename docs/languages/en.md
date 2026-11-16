# English

The file `text2spoken/lang/en.py` reads English. It needs no extra, because its number words come from the CLDR spell-out rules.

## What it reads

The file reads every form except identifiers. The `LETTERS` and `EMOJI` forms are off by default, as in every language, so a letter code such as `GPS` or `X5` stays as written unless the `LETTERS` form is on.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Dr Smith paid £3.50 for 2 tickets on 14 March 2024.` | `en-GB` | Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four. |
| `Meet on 03/04/2025 at 7:30 pm.` | `en-US` | Meet on March fourth twenty twenty-five at seven thirty PM. |
| `Room 101 is 5 km away.` | `en-GB` | Room one hundred and one is five kilometres away. |
| `Room 101 is 5 km away.` | `en-US` | Room one hundred one is five kilometers away. |
| `Write to ann@example.com.` | `en-GB` | Write to ann at example dot com. |
| `Call 911 now.` | `en-US` | Call nine one one now. |
| `© 2024` | `en-GB` | copyright two thousand and twenty-four |

[Money, units and symbols](../money-units-and-symbols.md) describes the units, currencies and symbols of CLDR, which English reads. [Addresses, letters and emoji](../addresses-letters-and-emoji.md) describes the addresses and the emoji.

## Varieties

| Tag | Notes |
| --- | --- |
| `en-GB` | The default variety. A bare `en` reads as `en-GB`. Reads `12/03/2024` day first, and "one hundred and one" |
| `en-US` | Reads `12/03/2024` month first, and "one hundred one" |

Every other `en-*` tag reads the variety that `linguatag.closest_lang` gives it, so `en-AU` reads `en-GB`.

## Options

| Option | Values | Default (`en-GB`) | Default (`en-US`) |
| --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` | `MDY` |
| `clock` | `12h`, `24h` | `12h` | `12h` |
| `minute_style` | `number`, `phrase` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `.` | `.` |
| `scale` | `short` | `short` | `short` |
| `phone_regions` | `AE`, `BR`, `EG`, `ES`, `FR`, `GB`, `PT`, `SA`, `US` | `GB` | `US` |
| `default_gender` | changes nothing | - | - |
| `register` | changes nothing | - | - |

## Sources

Number words come from CLDR RBNF. Unit words, currency names and symbol names come from CLDR 49. The names of the address symbols come from Wiktionary, and the letter names from Wikipedia, "English alphabet", which gives them from the Oxford English Dictionary. The syllable rule of the `LETTERS` form follows Wikipedia, "English phonology" and "English orthography". The docstring of [`en.py`](../../text2spoken/lang/en.py) gives each source.

The test rows in `tests/data/en.tsv` name their source. The `checked_by` column shows that no native speaker has checked them. There are 535 rows.

## Roman numerals

A Roman numeral after a capitalised name reads "the" and an ordinal, as a regnal number or a generational suffix. Wikipedia, "Roman numerals", says that regnal numbers "are usually read as ordinals", and Wikipedia, "Name suffix", says the same of a generational suffix: "he can use the II suffix, which is pronounced "the second"". After a noun of a series, the numeral reads as a cardinal. The nouns of the `roman_nouns` table are chapter, volume, book, act, grade, part, phase, class, level, stage, type, war, and the names World War and Super Bowl.

| Written | Spoken (`en-GB`) | Note |
| --- | --- | --- |
| `Henry VIII had six wives.` | Henry the Eighth had six wives. | A regnal number. |
| `King Harald V of Norway.` | King Harald the Fifth of Norway. | One letter reads after a regnal title and a name. |
| `Hank Williams III sang.` | Hank Williams the Third sang. | A generational suffix. |
| `Read Chapter IV.` | Read Chapter Four. | A noun of a series. |
| `Type II diabetes.` | Type Two diabetes. | A noun of a series. |
| `World War I began.` | World War One began. | One letter reads after a noun of two words. |
| `Malcolm X spoke.` | stays as written | One letter after a name needs a regnal title. Malcolm is also the name of four kings of Scotland, so a list of names cannot tell them apart. |
| `Baltimore MD is far.` | stays as written | `MD` is an initialism, in the `roman_words` table. |

## Runs of capital letters

A run that splits into English syllables stays as written, and any other run reads letter by letter. A table in the language file holds the runs that the rule reads wrong, such as `CIA`, `IRS`, `USA`, `IBS` and `IDS`, which read letter by letter. An e-mail or web address reads as an address, and not as a run.

| Written | Spoken (`en-GB`, `LETTERS` on) | Note |
| --- | --- | --- |
| `NATO met.` | stays as written | The run splits into English syllables. |
| `The CIA met.` | The see i a met. | The table spells it. |
| `Ask the CEO.` | stays as written | Limit: no source in the language file names it, so the rule reads it as a word. |
| `Ask WHO.` | stays as written | Limit: as for `CEO`. |
| `ABS brakes.` | stays as written | Limit: an English coda takes the s of the -s/-z morpheme, so a vowel, a consonant and s can read as a word. |
| `Check ITS data.` | stays as written | Limit: as for `ABS`. |
| `IBS and IDS.` | i bee ess and i dee ess. | `letter_runs` lists the ones that a source spells. |

The limits that English shares with Portuguese are on the [Addresses, letters and emoji](../addresses-letters-and-emoji.md#runs-of-capital-letters) page. [Letter names in English phonemizers](#letter-names-in-english-phonemizers) gives how English phonemizers read the letter names.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Maroon 5 ft. Cardi B` | `en-GB` | Maroon five ft. Cardi B | `ft` does not read as feet, because `ft.` also names "featuring" in a music credit. |
| `It is 6 ft tall.` | `en-GB` | It is six ft tall. | The same rule keeps `ft` as written after a number. |
| `A 5 µm hole.` | `en-GB` | A five micrometres hole. | A unit before a noun reads in the plural. |
| `It costs €12,50.` | `en-GB` | stays as written | A euro amount with a comma for the decimal mark stays as written. |

The limits that English shares with Portuguese are on the [Money, units and symbols](../money-units-and-symbols.md#limits) page.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

### Letter names in English phonemizers

Some English letter names do not read right in every English phonemizer, and no other spelling that Wiktionary gives as the name reads right in more of them. misaki does not know `ef` (F) or `ar` (R). In `double-u` (W), orthography2ipa reads `double` with the vowel of "out" on its rules alone, and g2p_en drops the /j/. An address reads the same names.

`a`, the name of A, reads as the article inside a phrase, so `nine a em` and `a at bee dot com` read the article in every English phonemizer measured. Before a full stop, espeak-ng and misaki read `a` as the letter name, as in `u ess a.` for `the USA.`. The other spelling `ay` reads as "aye", the name of I, in espeak-ng, so the table keeps `a`.

| Written | Spoken (`en-US`, `LETTERS` on) |
| --- | --- |
| `Call the BBC at 9 AM.` | Call the bee bee see at nine a em. |
| `Mail a@b.com now.` | Mail a at bee dot com now. |
| `I live in the USA.` | I live in the u ess a. |

### Addresses on a second pass

A word of a spoken address can become the key or the context of another form on a second pass, so the second pass changes the first. Four rules cause it:

| Written | Spoken (`en-GB`) | Second pass (`en-GB`) | Why |
| --- | --- | --- | --- |
| `See a@b.etc.` | See a at bee dot etc. | See a at bee dot et cetera. | The last label and the full stop after it form an abbreviation. |
| `Write x.com@ 9:30` | Write ex dot com at 9:30 | Write ex dot com at nine thirty | A final `@` reads "at", and a second pass takes it as the time word of a time after it. Only spaces or punctuation can stand between them. |
| `Write x.com@ (9:30)` | Write ex dot com at (9:30) | Write ex dot com at (nine thirty) | The same holds inside brackets. |
| `See example.com/May 05 for details.` | See example dot com slash May 05 for details. | See example dot com slash May fifth for details. | A month name as the first or the last label of an address forms a date with the digits next to it. |
| `On 05 May@x.com we met.` | On 05 May at ex dot com we met. | On the fifth of May at ex dot com we met. | The same rule, with the month name as the first label. |
| `Chapter XIV٢http://x` | Chapter XIV two aitch tee tee pee colon slash slash ex | Chapter Fourteen two aitch tee tee pee colon slash slash ex | An address keeps a Roman numeral as written, and a second pass reads it. |

### Currency signs next to other text

| Written | Tag | Spoken | Second pass | Why |
| --- | --- | --- | --- | --- |
| `x@€ 08` | `en-GB` | ex at € 08 | ex at eight euros | A currency sign at the start or the end of an address stays as written in the address, and a second pass reads it with the number next to it. |
| `x@₦ 08` | `en-GB` | ex at ₦ 08 | ex at eight Nigerian nairas | The same holds for the signs of the CLDR currencies. |
| `$0–0USD+2$` | `en-US` | `$0–0USD+two dollars` | zero dollars to zero dollars+two dollars | A money range whose last amount ends in a letter code, with a joiner and a digit after it, stays as written, and the amount after the joiner reads. |
| `€2 07946001800` | `en-GB` | two euros 07946001800 | two euros zero seven nine four six zero zero one eight zero zero | An amount right before a run of digits that starts with `0` reads, and the run stays as written. |
| `USD20 07946001800` | `en-GB` | twenty dollars 07946001800 | twenty dollars zero seven nine four six zero zero one eight zero zero | The same rule. |

With the `LETTERS` form on, an amount before a symbol and digits can stay as written while the symbol and the digits read:

| Written | Spoken (`en-US`, `LETTERS` on) | Second pass (`en-US`, `LETTERS` on) |
| --- | --- | --- |
| `US$0 0∇2` | `US$0 0 nabla two` | zero dollars zero nabla two |

The edge cases that English shares with Portuguese are on the [Money, units and symbols](../money-units-and-symbols.md#limits) and [Addresses, letters and emoji](../addresses-letters-and-emoji.md#edge-cases) pages.

---
[← German](de.md) · [Home](../index.md) · [Spanish →](es.md)
