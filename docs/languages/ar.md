# Arabic

The file `text2spoken/lang/ar.py` reads Modern Standard Arabic in Arabic script, with no diacritics. A diacritizer runs after it. Install it with `text2spoken[ar]`, which adds `ovos-number-parser`.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `ar-001` | The default variety. A bare `ar` reads as `ar-001` |
| `ar-DZ`, `ar-TN`, `ar-IQ`, `ar-JO`, `ar-PS`, `ar-SY`, `ar-LB`, `ar-LY`, `ar-MA`, `ar-MR` | Each regional tag reads the month names and number marks of its CLDR locale |

The Arabic varieties of ISO 639-3 that write Arabic script read as `ar`, with no dialect words: `aao`, `abh`, `abv`, `acm`, `acq`, `acw`, `acx`, `adf`, `aeb`, `aec`, `afb`, `apd`, `arb`, `arq`, `ars`, `ary`, `arz`, `auz`, `avl`, `ayh`, `ayl`, `ayn`, `ayp`, `shu` and `ssh`. `apc` (Levantine) is not one of them.

## What it reads

The file reads cardinals, decimals, fractions, ranges, dates, times, money, measures, percentages and lexicon entries. The default clock is `12h`, and the `register` param chooses formal or colloquial words.

A number agrees in gender and case with the noun after it, and an ordinal follows the noun that it ranks: `الطابق 3` reads "الطابق الثالث". One follows the noun that it counts, so `$1` reads "دولار واحد". Telephone numbers, operators such as `5+3`, a number with a `+` sign, and the word `ريال` before a number stay as written.

## Sources

The rules cite Karin C. Ryding, *A Reference Grammar of Modern Standard Arabic* (Cambridge University Press, 2005), W. Wright, *A Grammar of the Arabic Language* (3rd edition, 1896), Wiktionary and the CLDR 49 data of each locale. The docstring of [`ar.py`](../../text2spoken/lang/ar.py) gives the page of each rule.

In `tests/data/ar.tsv`, the 78 rows cite their source, and no native speaker has checked them.

## Limits

Some Arabic readings are wrong or stay as written:

- A number that is the object of a verb takes the nominative. Only a preposition, a semi-preposition or a year noun before it gives the oblique case. `اشترى 200 كتاب` reads "مئتا كتاب", where the object takes "مئتي كتاب" (Ryding 2005, p. 347).
- Only the semi-prepositions بعد, قبل, نحو, خلال, طوال and مع give the genitive. Another semi-preposition gives the nominative: `فوق 20 طابقا` reads "فوق عشرون طابقا".
- A feminine plural that the `feminine_plurals` table does not list counts as masculine, because a plural in -aat also comes from masculine nouns. `وصلت 3 طائرات` reads "ثلاثة طائرات", where the feminine طائرة takes "ثلاث".
- The word after a number counts as its noun, also when it is من. `اشتريت 3 من السيارات` reads "ثلاثة من السيارات".
- A scale word reads as the noun of the number only after a currency symbol. `الثمن 3 مليون ريال` reads "ثلاثة مليون ريال", where Ryding (p. 353) gives the plural ملايين.
- A negative amount of money reads as a number, and the noun stays singular: `الثمن -5 ريال` reads "سالب خمسة ريال".
- The colloquial register reads every number, dual and ordinal in the oblique case. Ryding (p. 343, note 11) gives the oblique form in spoken Arabic for the tens only, so the rest is a choice with no source.

Some Arabic readings wait for a native speaker:

- One o'clock stays as written, because the sources give no form for it: a speaker can say الواحدة or الأولى. So `الساعة 1:30`, every time from 13:00 to 13:59, and `12:45`, which names the next hour, stay as written.
- A time from 0:00 to 0:59 stays as written. The CLDR name of its day period is "في المساء", which no source here confirms for midnight.
- A fraction part with a leading zero stays as written, because no source gives its reading. `النسبة 0.05` stays as written.
- 800 reads ثمانمئة, where Ryding (2005, p. 348) writes thamaanii mi'at-in.
- 45,001 reads خمسة وأربعون ألف وواحد, with no tamyiz ending on the thousand, as ovos-number-parser writes it.

---
[← Errors and warnings](../errors.md) · [Home](../index.md) · [German →](de.md)
