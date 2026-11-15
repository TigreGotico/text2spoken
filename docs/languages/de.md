# German

The file `text2spoken/lang/de.py` reads German. It needs no extra: its number words come from the CLDR spell-out rules.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `de-DE` | The default variety |
| `de-AT` | Says `Jänner` for January |
| `de-CH` | Writes `ss` for `ß`, and takes `.` as the decimal mark |

`de` serves every German tag.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, years, money, measures, percentages, telephone numbers, abbreviations, idioms, colours and lexicon entries. It does not read addresses, symbols or Roman numerals.

A German number takes the gender and the case of its noun, as in `für einen Tag` and `mit einer Frau`. The word before the number gives the case. `in`, `an` and `vor` give the dative only before a noun of time, as in `vor einer Stunde`. A form of the verb `kosten` gives the accusative to a price, so `Das kostet 1 €.` reads "einen Euro". Any other noun after the verb is its subject, so `Wie viel kostet 1 Kaffee?` reads "ein Kaffee". A noun with no known gender takes the masculine, and only the dative of a preposition, so `zu 1 Freund` reads "einem Freund".

In `de-CH` the full stop is also the decimal mark, so a time with a full stop needs `Uhr`: `um 14.30 Uhr` is a time, and `um 1.15 Franken` reads "eins Komma eins fünf Franken". `von`, `bis`, `ab` and `seit` also come before a ratio, so a time after them needs `Uhr` or a range that `Uhr` closes, as in `von 9:00 bis 17:00 Uhr`.

## Sources

The rules cite the amtliche Regelwerk of the Rat für deutsche Rechtschreibung, the CLDR data of `de`, `de_AT` and `de_CH`, Duden online, de.wiktionary, de.wikipedia and en.wikipedia. The docstring of [`de.py`](../../text2spoken/lang/de.py) gives each entry.

The test rows in `tests/data/de.tsv` cite the Regelwerk, Duden, Wiktionary or Wikipedia, and no native speaker has checked them. Of the 119 rows, 34 mark at least one part of their reading as silver: no fetched source holds that part.

## Limits

Some German readings are wrong or stay as written:

- A verb gives no case, except `kosten`. `Ich habe 1 Hund.` reads "ein Hund", not "einen Hund". `Ich erinnere mich an 1 Tag im Mai.` reads "einem Tag", but `sich erinnern an` takes the accusative.
- A price that is the subject of `kosten` takes the accusative. `Wie viel kostet 1 Euro in Dollar?` reads "einen Euro".
- `in`, `an` and `vor` before a noun that is not a noun of time give no case. `Er wohnt in 1 Haus.` reads "ein Haus".
- A noun whose gender no rule gives takes the masculine. `mit 1 Freundin` reads "einem Freundin", and `1 Ampel` reads "ein Ampel". A `default_gender` param gives the feminine in the case of the preposition: "einer Freundin". A gender hint gives the feminine with no case, "eine Freundin", unless the hint also gives the case.
- A compound of an exception takes the ending rule, so `1 Osterei` reads "eine Osterei". A noun with `Ge-` that is not neuter reads as a neuter, so `1 Gerade` reads "ein Gerade", and `Mit 1 Gelatine.` reads "einem Gelatine".
- A preposition of the genitive gives no case to a number. `Während 1 Woche` and `Innerhalb 1 Woche` read "eine Woche". In `de-CH`, `Außerhalb der 3. Woche` with `ß` reads "dritte", because the `de-CH` tables write `ss`.
- `h`, `min` and `Std.` are not units. `Er kommt in 1 h.` reads "in eins h", `Er kam vor 1 min.` reads "vor eins min", and `1 Std.` reads "ein Std.".
- A minus sign between spaces stays as written. `5 - 3 = 2` reads "fünf - drei gleich zwei".
- A number with a space as the group mark stays as written, as in `10 000`.
- In `de-CH`, a time with a full stop and no `Uhr` reads as a decimal. `um 9.15` reads "neun Komma eins fünf".
- A time after `ab`, `von`, `bis` or `seit` with no `Uhr` stays as written, as in `Ab 16:10`. `9:00-17:00 Uhr` stays as written, because the core reads the dash as a joiner.
- One half before a noun stays as written, as in `1/2 Pizza`, because `halb` declines before a noun.
- A scale abbreviation after a number stays as written. `2 Mio. Einwohner` reads "zwei Mio. Einwohner", and `2 Mio. €` reads "zwei Mio. €".
- A year with no year word reads as a cardinal. `Er wurde 1999 geboren.` reads "eintausendneunhundertneunundneunzig".
- An ordinal from one million up stays as written, and so does an ordinal with no determiner before it, as in `Er wurde 2. Sieger.`
- A determiner that does not agree with a date is ignored. `das 12/03/2024 Wetter` reads "das zwölfter März zweitausendvierundzwanzig Wetter".
- The core table `PHONE_PLANS` holds no plan for DE, AT or CH.

---
[← Arabic](ar.md) · [Home](../index.md) · [English →](en.md)
