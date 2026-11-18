# Arabic

The file `text2spoken/lang/ar.py` reads Modern Standard Arabic in Arabic script, with no diacritics. A diacritizer runs after it. Its number words come from `ovos-number-parser`, which the base install holds.

## What it reads

The file reads cardinals, decimals, fractions, ranges, dates, times, money, measures, percentages and lexicon entries. A number agrees in gender and case with the noun after it. An ordinal follows the noun that it ranks, and one follows the noun that it counts.

| Written | Tag | Spoken |
| --- | --- | --- |
| `الطابق 3` | `ar` | الطابق الثالث |
| `دفعت $1` | `ar` | دفعت دولار واحد |
| `اشتريت 3 كتب` | `ar` | اشتريت ثلاثة كتب |
| `في 3 سيارات` | `ar` | في ثلاث سيارات |
| `النسبة 2.5%` | `ar` | النسبة اثنان فاصلة خمسة في المئة |
| `%10 خصم` | `ar` | عشرة في المئة خصم |
| `الساعة 3:30` | `ar` | الساعة الثالثة والنصف |
| `موعدك 15/9/1447هـ` | `ar` | موعدك الخامس عشر من رمضان ألف وأربعمئة وسبعة وأربعين هجري |
| `النسبة 10%-20%` | `ar` | النسبة عشرة في المئة إلى عشرين في المئة |
| `العرض من 1 إلى 7 مارس` | `ar` | العرض من الأول إلى السابع من مارس |

These stay as written: telephone numbers, operators such as `5+3`, a number with a `+` sign, and the word `ريال` before a number.

| Written | Spoken (`ar`) |
| --- | --- |
| `اتصل 0501234567` | stays as written |
| `الناتج 5+3` | stays as written |
| `الفرق +5` | stays as written |
| `الثمن ريال 5` | stays as written |

## Varieties

| Tag | Notes |
| --- | --- |
| `ar-001` | The default variety. A bare `ar` reads as `ar-001` |
| `ar-DZ`, `ar-TN`, `ar-IQ`, `ar-JO`, `ar-PS`, `ar-SY`, `ar-LB`, `ar-LY`, `ar-MA`, `ar-MR` | Each regional tag reads the month names and number marks of its CLDR locale |

A regional tag such as `ar-EG` reads Modern Standard Arabic words.

Each spoken Arabic lect of ISO 639-3 that writes Arabic script reads as itself:

- It reads the month names and the number marks of its region. A tag with no region, or with a region that is not the region below, reads the region below.
- It reads in the colloquial register, because colloquial Arabic has no case marking (Ryding 2005, p. 166).
- In the colloquial register, its number words come from `ovos-number-parser` with the code of the lect. Where the parser has no dialect words for a lect, the words are colloquial Standard Arabic: the oblique case, with no case ending.

| Written | Tag | Spoken |
| --- | --- | --- |
| `الطقس 13 جميل 250 جدا` | `ar` | الطقس ثلاثة عشر جميل مئتان وخمسون جدا |
| `الطقس 13 جميل 250 جدا` | `arz` | الطقس تلتاشر جميل ميتين وخمسين جدا |
| `الطقس 13 جميل 250 جدا` | `ary` | الطقس تلتاش جميل ميتين وخمسين جدا |
| `25/7/1930` | `ary` | الخامس والعشرين من يوليوز ألف وتسعمية وتلاتين |
| `الوزن 2,5` | `ary` | الوزن تنين فاصلة خمسة |
| `الطقس 13 جميل 250 جدا` | `apc` | الطقس تلتعش جميل ميتين وخمسين جدا |

| Lect | Region | Number words |
| --- | --- | --- |
| `arz` Egyptian | `EG` | Egyptian |
| `acw` Hijazi | `SA` | Hijazi |
| `afb` Gulf | `KW` | Gulf |
| `ars` Najdi | `SA` | Najdi |
| `apc` Levantine | `SY` | Levantine |
| `ary` Moroccan | `MA` | Moroccan |
| `aeb` Tunisian | `TN` | Tunisian |
| `arq` Algerian | `DZ` | Algerian |
| `acm` Mesopotamian, `ayl` Libyan | `IQ`, `LY` | Colloquial Standard Arabic, from `ovos-number-parser` with the code of the lect |
| `aao`, `aec`, `apd`, `auz`, `avl`, `abh`, `abv`, `acq`, `acx`, `adf`, `ayh`, `ayn`, `ayp`, `shu`, `ssh` | `DZ`, `EG`, `SD`, `UZ`, `EG`, `TJ`, `BH`, `YE`, `OM`, `OM`, `YE`, `YE`, `IQ`, `TD`, `AE` | Colloquial Standard Arabic, from `ovos-number-parser` with the code of the lect |
| `arb` Standard Arabic | none | Modern Standard Arabic, in the formal register |

The region of each lect is the region of its CLDR 49 likely subtags, which Glottolog lists among the countries of the lect. `register="formal"` gives a lect the words and the case of `ar`.

The tag `ajp` reads as `apc`. ISO 639-3 retired `ajp` (South Levantine) and merged it into `apc` (change request 2022-006).

## Options

The `register` option chooses formal or colloquial words. A spoken lect such as `arz` defaults to `colloquial`.

| Option | Values | Default (`ar-001`) | Default (`ar-DZ`) |
| --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY` | `DMY` | `DMY` |
| `clock` | `12h` | `12h` | `12h` |
| `decimal_mark` | `,`, `.` | `.` | `,` |
| `register` | `colloquial`, `formal` | `formal` | `formal` |
| `default_gender` | `feminine`, `masculine` | `masculine` | `masculine` |
| `minute_style` | changes nothing | - | - |
| `scale` | changes nothing | - | - |
| `phone_regions` | changes nothing | - | - |

## Sources

The rules cite Karin C. Ryding, *A Reference Grammar of Modern Standard Arabic* (Cambridge University Press, 2005), W. Wright, *A Grammar of the Arabic Language* (3rd edition, 1896), Wiktionary, Arabic Wikipedia, the ISO 639-3 macrolanguage table of iso639-3.sil.org, the CLDR 49 data of each locale, the CLDR 49 likely subtags and the country lists of Glottolog. The number words of a lect come from `ovos-number-parser`, whose tables cite a grammar for each word. The docstring of [`ar.py`](../../text2spoken/lang/ar.py) gives the page of each rule.

In `tests/data/ar.tsv`, the 171 rows cite their source, and no native speaker has checked them. A row of a lect takes its number words from `ovos-number-parser` and says so.

## Limits

Some Arabic readings are wrong or stay as written:

| Written | Spoken (`ar`) | Limit |
| --- | --- | --- |
| `اشترى 200 كتاب` | اشترى مئتا كتاب | A number that is the object of a verb takes the nominative. Only a preposition, a semi-preposition or a year noun before it gives the oblique case. The object takes "مئتي كتاب" (Ryding 2005, p. 347). |
| `فوق 20 طابقا` | فوق عشرون طابقا | Only the semi-prepositions بعد, قبل, نحو, خلال, طوال and مع give the genitive. Another semi-preposition gives the nominative. |
| `وصلت 3 طائرات` | وصلت ثلاثة طائرات | A feminine plural that the `feminine_plurals` table does not list counts as masculine, because a plural in -aat also comes from masculine nouns. The feminine طائرة takes "ثلاث". |
| `اشتريت 3 من السيارات` | اشتريت ثلاثة من السيارات | The word after a number counts as its noun, also when it is من. |
| `الثمن 3 مليون ريال` | الثمن ثلاثة مليون ريال | A scale word reads as the noun of the number only after a currency symbol. Ryding (p. 353) gives the plural ملايين. |
| `الثمن -5 ريال` | الثمن سالب خمسة ريال | A negative amount of money reads as a number, and the noun stays singular. |

The colloquial register reads every number, dual and ordinal in the oblique case. Ryding (p. 343, note 11) gives the oblique form in spoken Arabic for the tens only, so the rest is a choice with no source:

| Written | Spoken (`ar`) | Spoken (`ar`, `register="colloquial"`) |
| --- | --- | --- |
| `جاء 200 رجل` | جاء مئتا رجل | جاء مئتي رجل |
| `جاء 20 رجلا` | جاء عشرون رجلا | جاء عشرين رجلا |

Some Arabic readings wait for a native speaker:

| Written | Spoken (`ar`) | Limit |
| --- | --- | --- |
| `الساعة 1:30` | stays as written | One o'clock stays as written, because the sources give no form for it: a speaker can say الواحدة or الأولى. |
| `الساعة 13:15` | stays as written | Every time from 13:00 to 13:59 stays as written for the same reason. |
| `الساعة 12:45` | stays as written | `12:45` names the next hour, so it stays as written too. |
| `الساعة 0:30` | stays as written | A time from 0:00 to 0:59 stays as written. The CLDR name of its day period is "في المساء", which no source here confirms for midnight. |
| `النسبة 0.05` | stays as written | A fraction part with a leading zero stays as written, because no source gives its reading. |
| `دفعت 800 دولار` | دفعت ثمانمئة دولار | 800 reads ثمانمئة, where Ryding (2005, p. 348) writes thamaanii mi'at-in. Not fetched: no copy of that page was read. |
| `دفعت 45001 دولار` | دفعت خمسة وأربعون ألف وواحد دولار | 45,001 reads with no tamyiz ending on the thousand, as ovos-number-parser writes it. |

---
[← Errors and warnings](../errors.md) · [Home](../index.md) · [Catalan →](ca.md)
