# German

<!-- agent-hint
covers: what the German file reads, its varieties, options, sources and limits.
source: text2spoken/lang/de.py, tests/data/de.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/de.md`
see: en.md, ../how-it-reads.md
-->

The file `text2spoken/lang/de.py` reads German. It needs no extra. Its number words come from numtag, and its years from the CLDR spell-out rules.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, years, money, measures, percentages, telephone numbers, abbreviations, idioms, colours and lexicon entries.
The file reads no e-mail or web addresses, runs of capital letters, symbols, emoji or Roman numerals.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Das ist für 1 Tag.` | `de-DE` | Das ist für einen Tag. |
| `Ich gehe mit 1 Frau.` | `de-DE` | Ich gehe mit einer Frau. |
| `Das kostet 1 €.` | `de-DE` | Das kostet einen Euro. |
| `Wie viel kostet 1 Kaffee?` | `de-DE` | Wie viel kostet ein Kaffee? |
| `Ich gehe zu 1 Freund.` | `de-DE` | Ich gehe zu einem Freund. |
| `Das war vor 1 Stunde.` | `de-DE` | Das war vor einer Stunde. |
| `Am 12.03.2024 um 14:30 Uhr.` | `de-DE` | Am zwölften März zweitausendvierundzwanzig um vierzehn Uhr dreißig. |
| `Am 3. Januar.` | `de-AT` | Am dritten Jänner. |
| `um 14.30 Uhr` | `de-CH` | um vierzehn Uhr dreissig |
| `um 1.15 Franken` | `de-CH` | um eins Komma eins fünf Franken |
| `Das Buch kostet 23,88 €.` | `de-CH` | Das Buch kostet dreiundzwanzig Euro achtundachtzig. |
| `von 9:00 bis 17:00 Uhr` | `de-DE` | von neun Uhr bis siebzehn Uhr |

A German number takes the gender and the case of its noun, and the word before the number gives the case. `in`, `an` and `vor` give the dative only before a noun of time. A form of the verb `kosten` right before a price gives it the accusative. Any other noun after the verb is its subject. A noun with no known gender takes the masculine, and only the dative of a preposition.

In `de-CH` the full stop is also the decimal mark, so a time with a full stop needs `Uhr`. `von`, `bis`, `ab` and `seit` also come before a ratio, so a time after them needs `Uhr`, or a range that `Uhr` closes.

## Varieties

| Tag | Notes |
| --- | --- |
| `de-DE` | The default variety |
| `de-AT` | Says `Jänner` for January |
| `de-CH` | Writes `ss` for `ß`, and takes `.` as the decimal mark |

`de` serves every German tag.

## Options

| Option | Values | Default (`de-DE`) | Default (`de-CH`) |
| --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` | `DMY` |
| `clock` | `24h` | `24h` | `24h` |
| `minute_style` | `number` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `,` | `.` |
| `scale` | `long` | `long` | `long` |
| `default_gender` | `feminine`, `masculine`, `neuter` | `masculine` | `masculine` |
| `phone_regions` | `AE`, `BR`, `EG`, `ES`, `FR`, `GB`, `PT`, `SA`, `US` | none | none |
| `register` | changes nothing | - | - |

## Sources

The rules cite the amtliche Regelwerk of the Rat für deutsche Rechtschreibung, the CLDR data of `de`, `de_AT` and `de_CH`, Duden online, de.wiktionary, de.wikipedia and en.wikipedia. The docstring of [`de.py`](../../text2spoken/lang/de.py) gives each entry.

Most test rows in `tests/data/de.tsv` cite the Regelwerk, Duden, Wiktionary or Wikipedia. Some cite CLDR or the design of text2spoken. No native speaker has checked them. Some rows mark at least one part of their reading as silver: that part comes from memory, and no source was read for it.

## Limits

Some German readings are wrong or stay as written:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Ich habe 1 Hund.` | `de-DE` | Ich habe ein Hund. | A verb gives no case, except `kosten`. The accusative is "einen Hund". |
| `Ich erinnere mich an 1 Tag im Mai.` | `de-DE` | Ich erinnere mich an einem Tag im Mai. | `sich erinnern an` takes the accusative. |
| `Wie viel kostet 1 Euro in Dollar?` | `de-DE` | Wie viel kostet einen Euro in Dollar? | A price that is the subject of `kosten` takes the accusative. |
| `Er wohnt in 1 Haus.` | `de-DE` | Er wohnt in ein Haus. | `in`, `an` and `vor` before a noun that is not a noun of time give no case. |
| `mit 1 Freundin` | `de-DE` | mit einem Freundin | A noun whose gender no rule gives takes the masculine. |
| `1 Ampel` | `de-DE` | ein Ampel | A noun whose gender no rule gives takes the masculine. |
| `1 Osterei` | `de-DE` | eine Osterei | A compound of an exception takes the ending rule. |
| `1 Gerade` | `de-DE` | ein Gerade | A noun with `Ge-` that is not neuter reads as a neuter. |
| `Mit 1 Gelatine.` | `de-DE` | Mit einem Gelatine. | A noun with `Ge-` that is not neuter reads as a neuter. |
| `Während 1 Woche` | `de-DE` | Während eine Woche | A preposition of the genitive gives no case to a number. |
| `Innerhalb 1 Woche` | `de-DE` | Innerhalb eine Woche | A preposition of the genitive gives no case to a number. |
| `Außerhalb der 3. Woche` | `de-CH` | Außerhalb der dritte Woche | The `de-CH` tables write `ss`, so the preposition with `ß` gives no case. |
| `Er kommt in 1 h.` | `de-DE` | Er kommt in eins h. | `h`, `min` and `Std.` are not units. |
| `Er kam vor 1 min.` | `de-DE` | Er kam vor eins min. | `h`, `min` and `Std.` are not units. |
| `1 Std.` | `de-DE` | ein Std. | `h`, `min` and `Std.` are not units. |
| `5 - 3 = 2` | `de-DE` | fünf - drei gleich zwei | A minus sign between spaces stays as written. |
| `10 000` | `de-DE` | stays as written | A number with a space as the group mark stays as written. |
| `um 9.15` | `de-CH` | um neun Komma eins fünf | In `de-CH`, a time with a full stop and no `Uhr` reads as a decimal. |
| `Ab 16:10` | `de-DE` | stays as written | A time after `ab`, `von`, `bis` or `seit` with no `Uhr` stays as written. |
| `9:00-17:00 Uhr` | `de-DE` | stays as written | The core reads the dash as a joiner, so the range stays as written. |
| `1/2 Pizza` | `de-DE` | stays as written | One half before a noun stays as written, because `halb` declines before a noun. |
| `2 Mio. Einwohner` | `de-DE` | zwei Mio. Einwohner | A scale abbreviation after a number stays as written. |
| `2 Mio. €` | `de-DE` | zwei Mio. € | A scale abbreviation after a number stays as written. |
| `Er wurde 1999 geboren.` | `de-DE` | Er wurde eintausendneunhundertneunundneunzig geboren. | In German, a year with no year word reads as a cardinal. |
| `Er wurde 2. Sieger.` | `de-DE` | stays as written | An ordinal with no determiner before it stays as written. |
| `das 12/03/2024 Wetter` | `de-DE` | das zwölfter März zweitausendvierundzwanzig Wetter | A determiner that does not agree with a date is ignored. |

A `default_gender` param gives the feminine in the case of the preposition. A gender hint gives the feminine with no case, unless the hint also gives the case:

| Written | Spoken (`de-DE`) | Spoken (`de-DE`, `default_gender=FrozenMap({"de": GrammaticalGender.FEMININE})`) |
| --- | --- | --- |
| `mit 1 Freundin` | mit einem Freundin | mit einer Freundin |

```python
>>> from text2spoken import Features, GrammaticalGender, analyze, render
>>> analysis = analyze("mit 1 Freundin", "de-DE")
>>> render(analysis, {4: Features(gender=GrammaticalGender.FEMININE)})
'mit eine Freundin'
```

The core table `PHONE_PLANS` holds no plan for DE, AT or CH.

---
[← Danish](da.md) · [Home](../index.md) · [Greek →](el.md)
