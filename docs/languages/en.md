# English

<!-- agent-hint
covers: what the English file reads, its varieties, options, sources and limits.
source: text2spoken/lang/en.py, tests/data/en.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/en.md`
see: ../addresses-letters-and-emoji.md, ../money-units-and-symbols.md
-->

The file `text2spoken/lang/en.py` reads English. It needs no extra, because its number words come from the CLDR spell-out rules.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, years, money, measures, percentages, telephone numbers, runs of capital letters, abbreviations, idioms, Roman numerals, colours, e-mail and web addresses, symbols, emoji and lexicon entries.
The file reads no identifiers. The `LETTERS` and `EMOJI` forms are off by default, as in every language, so a letter code such as `GPS` or `X5` stays as written unless the `LETTERS` form is on.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Dr Smith paid £3.50 for 2 tickets on 14 March 2024.` | `en-GB` | Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four. |
| `Meet on 03/04/2025 at 7:30 pm.` | `en-US` | Meet on March fourth twenty twenty-five at seven thirty PM. |
| `Room 101 is 5 km away.` | `en-GB` | Room one hundred and one is five kilometres away. |
| `Room 101 is 5 km away.` | `en-US` | Room one hundred one is five kilometers away. |
| `Write to ann@example.com.` | `en-GB` | Write to ann at example dot com. |
| `Call 911 now.` | `en-US` | Call nine one one now. |
| `© 2024` | `en-GB` | copyright two thousand and twenty-four |
| `The Prof. arrived.` | `en-US` | The Professor arrived. |
| `It costs 23,88 €.` | `en-US` | It costs twenty-three euros and eighty-eight cents. |

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

The test rows in `tests/data/en.tsv` name their source. The `checked_by` column shows that no native speaker has checked them.

## Roman numerals

A Roman numeral reads only where a rule gives its reading. Every other numeral stays as written, because a capitalised word alone does not tell a title of a work, a product or a council from a name.

A regnal number reads "the" and an ordinal. Wikipedia, "Roman numerals", says that regnal numbers "are usually read as ordinals". A regnal number follows a regnal title and a name, such as King, Queen, Pope, Saint, Emperor or Tsar before the name, or a name of the `regnal_names` table. Only spaces part the title, the name and the numeral. One mark can also part the title from a name of `regnal_names`, as an apposition does in `the Holy Roman Emperor, Henry V` and `our king [Charles I]`. The marks are the comma, the parentheses, the square brackets, the straight and curly double quotes, the single quotes and the guillemets `«` and `»`. A single quote, `'` or `’`, is also an apostrophe, as in `the princess' Charles`, so it parts the title from the name only when it opens a quote: a space comes before it and the name comes after it. A slash, a colon, two marks or any other mark after the title leaves the text as written, and so does any mark before a name outside `regnal_names`. The `regnal_names` table holds the names from the Wikipedia lists of monarchs, popes and emperors that the docstring of `en.py` names, such as Adrian, the name of six popes, and Gustav, a name of the kings of Sweden.

A generational suffix from II to IV reads the same way. Wikipedia, "Name suffix", says: "he can use the II suffix, which is pronounced "the second"". The suffix follows exactly two words: a given name and a surname. The file `text2spoken/data/en/given_names.json` holds 6,515 given names, the 1,000 names of each sex that the US Social Security Administration records most often in each year from 1900 to 2020. The file `text2spoken/data/en/surnames.json` holds the 1,000 most frequent surnames of the 2010 US census. Many given names are also words, such as Star or Golden, and the surname check keeps a title of a work such as `Star Trek II` as written. A title of a work, a company, a product or a place that is built from a given name and a surname of the two files reads as a person, as `Harry Potter IV` and `Morgan Stanley III` do. The text alone does not tell such a name from a person.

After a noun of a series, the numeral reads as a cardinal. The nouns of the `roman_nouns` table are chapter, volume, book, act, grade, episode, section, part, phase, class, level, stage, type, war, and the names World War and Super Bowl. A numeral of the `roman_words` table, such as `XL`, `MX` or `CD`, is also a word or an initialism. It reads only after a noun of the `roman_letter_nouns` table, whose members take numbers and never letters (chapter, volume, book, act, episode, war, World War and Super Bowl), and only when no word in lowercase follows it. A class, a type, a part, a phase, a grade, a section, a stage and a level are labelled with letters too, so after these nouns a numeral of `roman_words` stays as written. A numeral of one letter reads only after a regnal title and a name, and after a noun of two words. After a name, the numeral reads only up to 30.

| Written | Spoken (`en-GB`) | Note |
| --- | --- | --- |
| `Henry VIII had six wives.` | Henry the Eighth had six wives. | A regnal number. |
| `King Harald V of Norway.` | King Harald the Fifth of Norway. | One letter reads after a regnal title and a name. |
| `John Smith III spoke.` | John Smith the Third spoke. | A generational suffix after a given name and a surname. |
| `Hank Williams III sang.` | Hank Williams the Third sang. | A generational suffix after a given name and a surname. |
| `Rocky II was a hit.` | stays as written | No rule names `Rocky`, so the numeral stays as written. |
| `Vatican II changed the Mass.` | stays as written | No rule names `Vatican`, so the numeral stays as written. |
| `Read Chapter IV.` | Read Chapter Four. | A noun of a series. |
| `Read Chapter XL.` | Read Chapter Forty. | `XL` is a word of `roman_words`, and no word in lowercase follows it. |
| `Type II diabetes.` | Type Two diabetes. | A noun of a series. |
| `It is a type MX record.` | stays as written | `MX` is an initialism of `roman_words`, and a word in lowercase follows it. |
| `He drove a Class CL.` | stays as written | A class is labelled with letters too. |
| `The Super Bowl XL Champions came home.` | The Super Bowl Forty Champions came home. | Super Bowl takes numbers and never letters. |
| `World War I began.` | World War One began. | One letter reads after a noun of two words. |
| `Malcolm X spoke.` | stays as written | One letter after a name needs a regnal title. Malcolm is also the name of four kings of Scotland. |
| `Adrian IV was the only English pope.` | Adrian the Fourth was the only English pope. | A name of `regnal_names`. |
| `Venice gets a queen / Best I've ever seen.` | stays as written | A slash parts the title from the next word. |
| `The first Bosnian King, Tvrtko I, held the fortress.` | The first Bosnian King, Tvrtko the First, held the fortress. | A comma before a name of `regnal_names` is an apposition. |
| `I pray God our king [Charles I] may follow him.` | I pray God our king [Charles the First] may follow him. | A bracket before a name of `regnal_names` opens an apposition. |
| `The emperor «Pedro I» signed the decree.` | The emperor «Pedro the First» signed the decree. | A guillemet opens an apposition. |
| `Was it the princess' Charles I danced with?` | stays as written | The apostrophe of a possessive opens no apposition, so `I` stays a pronoun. |
| `Hail the king: Henry V opens tonight.` | stays as written | A colon parts the title from the name. |
| `Harry Potter IV was a working title.` | Harry Potter the Fourth was a working title. | A title built from a given name and a surname reads as a person. |
| `Baltimore MD is far.` | stays as written | No rule names `Baltimore`, so the initialism `MD` stays as written. |

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
| `It costs $23,88.` | `en-US` | stays as written | A decimal comma reads only next to `€`, the currency that CLDR writes with the comma in German, Spanish, French and Italian. |
| `On 5 Jan II Corps attacked.` | `en-GB` | On five Jan the Second Corps attacked. | A name of `regnal_names` reads its numeral anywhere, also in the name of a ship, a club or a military unit. Jan is the name of three kings of Poland and also the short form of January, so a corps after a date reads as a regnal number. |

The limits that English shares with Portuguese are on the [Money, units and symbols](../money-units-and-symbols.md#limits) page.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

### Letter names in English phonemizers

A letter reads by the name that Wikipedia, "English alphabet", gives from the Oxford English Dictionary, with `zed` in `en-GB` and `zee` in `en-US`. C reads `see`, another spelling of its name, because the English phonemizer misaki has no `cee` in its American lexicon. An address reads the same names.

`a`, the name of A, reads as the article inside a phrase, so `nine a em` and `a at bee dot com` read the article in every English phonemizer measured. Before a full stop, espeak-ng and misaki read `a` as the letter name, as in `u ess a.` for `the USA.`. The other spelling `ay` reads as "aye", the name of I, in espeak-ng, so the table keeps `a`.

| Written | Spoken (`en-US`, `LETTERS` on) |
| --- | --- |
| `Call the BBC at 9 AM.` | Call the bee bee see at nine a em. |
| `Mail a@b.com now.` | Mail a at bee dot com now. |
| `I live in the USA.` | I live in the u ess a. |

### Addresses on a second pass

A word of a spoken address can become the key or the context of another form on a second pass, so the second pass changes the first. Five rules cause it:

| Written | Spoken (`en-GB`) | Second pass (`en-GB`) | Why |
| --- | --- | --- | --- |
| `See a@b.etc.` | See a at bee dot etc. | See a at bee dot et cetera. | The last label and the full stop after it form an abbreviation. |
| `Write x.com@ 9:30` | Write ex dot com at 9:30 | Write ex dot com at nine thirty | A final `@` reads "at", and a second pass takes it as the time word of a time after it. Only spaces or punctuation can stand between them. |
| `Write x.com@ (9:30)` | Write ex dot com at (9:30) | Write ex dot com at (nine thirty) | The same holds inside brackets. |
| `See example.com/May 05 for details.` | See example dot com slash May 05 for details. | See example dot com slash May fifth for details. | A month name as the first or the last label of an address forms a date with the digits next to it. |
| `On 05 May@x.com we met.` | On 05 May at ex dot com we met. | On the fifth of May at ex dot com we met. | The same rule, with the month name as the first label. |
| `Pay 2,51 €m.www.x.in` | Pay 2,51 € em dot double-u double-u double-u dot ex dot i en | Pay two euros and fifty-one cents em dot double-u double-u double-u dot ex dot i en | A currency sign that starts an address stays as written in its reading. The first pass keeps the number before it, because the sign touches the letter after it. The reading puts a space after the sign, and a second pass reads the number and the sign as money. |
| `No.00 €1,000.www.x.in` | No.00 € one , zero zero zero dot double-u double-u double-u dot ex dot i en | No.zero euros one , zero zero zero dot double-u double-u double-u dot ex dot i en | The same rule, with a digit after the sign. |
| `Chapter XIV٢http://x` | Chapter XIV two aitch tee tee pee colon slash slash ex | Chapter Fourteen two aitch tee tee pee colon slash slash ex | An address keeps a Roman numeral as written, and a second pass reads it. |

### Currency signs next to other text

| Written | Tag | Spoken | Second pass | Why |
| --- | --- | --- | --- | --- |
| `x@€ 08` | `en-GB` | ex at € 08 | ex at eight euros | A currency sign at the start or the end of an address stays as written in the address, and a second pass reads it with the number next to it. |
| `x@₦ 08` | `en-GB` | ex at ₦ 08 | ex at eight Nigerian nairas | The same holds for the signs of the CLDR currencies. |
| `$0–0USD+2$` | `en-US` | `$0–0USD+two dollars` | zero dollars to zero dollars+two dollars | A money range whose last amount ends in a letter code, with a joiner and a digit after it, stays as written, and the amount after the joiner reads. |
| `€2 07946001800` | `en-GB` | two euros zero seven nine four six zero zero one eight zero zero | two euros zero seven nine four six zero zero one eight zero zero | An amount right before a run of digits that starts with `0` reads, and the run reads digit by digit after it. |
| `USD20 07946001800` | `en-GB` | twenty dollars zero seven nine four six zero zero one eight zero zero | twenty dollars zero seven nine four six zero zero one eight zero zero | The same rule. |

With the `LETTERS` form on, an amount before a symbol and digits reads, and the symbol and the digits read after it:

| Written | Spoken (`en-US`, `LETTERS` on) | Second pass (`en-US`, `LETTERS` on) |
| --- | --- | --- |
| `US$0 0∇2` | zero dollars zero nabla two | zero dollars zero nabla two |

The edge cases that English shares with Portuguese are on the [Money, units and symbols](../money-units-and-symbols.md#limits) and [Addresses, letters and emoji](../addresses-letters-and-emoji.md#edge-cases) pages.

---
[← Greek](el.md) · [Home](../index.md) · [Spanish →](es.md)
