"""Arabic: `ar`, its CLDR regional varieties, and the spoken Arabic lects of ISO 639-3.

The output is in Arabic script with no diacritics; a diacritizer runs after normalisation. `SERVES` holds the active
members of the ISO 639-3 macrolanguage `ara` (iso639-3.sil.org, macrolanguage table) that write Arabic script; the
CLDR 49 likely subtags give Latin script to `acy` and `pga`. A regional tag such as `ar-MA` reads the month names and
the number marks of its CLDR 49 locale (`numbers.json`, `ca-gregorian.json`), and Modern Standard Arabic words.

A spoken lect reads as itself. Its region is the region of its CLDR 49 likely subtags (`likelySubtags.json`), which
Glottolog lists among the countries of the lect, so `ary` reads the Moroccan month names and decimal comma of `ar-MA`.
Ryding writes that "colloquial forms of Arabic do not have case marking" (p. 166), so a lect reads in the colloquial
register by default. Each code of `SERVES` but `arb` names a regional or ethnic variety in the ISO 639-3 code table,
such as "Egyptian Arabic" or "Chadian Arabic"; `arb` is "Standard Arabic" and stays formal, as `ar` does. In the
colloquial register, the number words of a lect come from ovos-number-parser with the code of the lect, so `arz`
reads the Egyptian تلتاشر for 13 and `apc` the Levantine تلتعش. A lect with no dialect words in ovos-number-parser
reads colloquial Standard Arabic, which the parser gives each member of the macrolanguage `ara`. ISO 639-3 change
request 2022-006 merged the retired South Levantine `ajp` into `apc`, and linguatag standardizes `ajp` to `apc`, so an
`ajp` tag reads as `apc`.

The rules and their sources:

- Agreement (Ryding 2005, chapter 15). One follows the noun that it counts: waaHid "behaves syntactically as an
  adjective, following the counted noun, and agreeing with it in case and gender" (p. 330). Two follows the noun too
  (p. 333), and a noun in the dual counts two with no numeral (p. 332). From 3 to 10 a number takes the gender
  opposite to its noun (p. 334), and eight before a feminine plural is ثماني (p. 336). From 11 to 99 the noun follows
  in the accusative singular (pp. 339-345). A noun that ends in taa' marbuuTa is feminine (p. 121), and the plurals
  in -aat of masculine nouns (Wright 1896, vol. 1, section 303) make the feminine plurals a table. The gender of a
  plural is the gender of its singular: "if the singular noun is masculine, the numeral will have the feminine
  marker taa' marbuuTa, and if the singular noun is feminine, the numeral will be in the masculine form" (p. 334).
  So the table holds plurals whose singular ends in taa' marbuuTa. Ryding writes that "Most feminine nouns are
  marked by the taa' marbuuTa suffix" (p. 121), and the ending of a plural is no such mark: the plurals of the
  pattern أفعلة, such as أجهزة, the plural of the masculine جهاز, end in ة, and the table `afila_plurals` lists them,
  so that their numbers read as those of a masculine noun, as in `5 أجهزة`. A shape rule reads the feminine singulars
  of the same shape (أوقية, أونصة, أهمية, أغنية) wrong, so a table lists the plurals.
- A number that names a thing counts no noun. "In recitation form, in counting without a counted noun, or in referring
  to a specific numeral alone, the form with taa' marbuuTa is usually used" (Ryding 2005, p. 335). The example of that
  page is "raqm-u sittat-in huwa raqm-un siHriyy-un", "The number six is a magic number". So a number after رقم, or
  after the lead #, which reads رقم, reads this form: `الحافلة رقم 42 متأخرة` reads اثنان وأربعون. No source names
  other label nouns. The file reads a number after موديل or موديلات, a model or a model year, in this form too:
  `السيارة موديل 2026 متوفرة` reads ألفان وستة وعشرون. Of three to ten, "The counted noun itself is plural,
  indefinite, and in the genitive case" (p. 335). So after a code in Latin letters, as in `MG 5 متوفرة`, a singular in
  taa' marbuuTa after 3 to 10 is no noun that the number counts, and the number names a thing. A noun of a CLDR 49
  unit stays a counted noun: CLDR writes the few count of length-inch as "{0} بوصة". A number after a definite noun,
  as in `الحلقة 7 كاملة`, still agrees with the word after it: web text often counts a singular after 3 to 10, as in
  `التحضير 10 دقيقة`, so a singular word after the number is no sign of a label.
- A number that starts a line and that a mark of `list_marks` and a space follow, as in `4- وطبيعة المنتج`, numbers
  an item of a list. It counts no noun and reads the form with taa' marbuuTa, as in counting: "waaHid-un, ithnaani,
  thalaathat-un!" (Ryding 2005, p. 335). No source names the list mark; the rule rests on p. 335 and on a corpus
  measure.
- A counted noun after the number is indefinite. Of three to ten, "The counted noun itself is plural, indefinite,
  and in the genitive case" (Ryding 2005, p. 335). "In the definite form, the numeral is in apposition with the
  noun. It follows the noun" (p. 338), and a definite noun counted by eleven or twelve comes before the numeral too
  (p. 340). The definite article "is attached as a prefix" and "is a proclitic particle, i.e., always attached to a
  word" (p. 40), and bi-, li- and ka- "need to be prefixed to the noun that follows" (p. 367), with li- before the
  article written لل (p. 371). So a word with the article after a proclitic, as in `فاز 5 بالجائزة` or `المادة 23
  للائحة`, is no noun that the number counts, as a word with the bare article is not. The conjunctions wa- and fa-
  (p. 72) may come first, as in والسيارة.
- Case. A number after a preposition or a semi-preposition (p. 367) or a year noun (pp. 351-353) is genitive. Ryding
  writes that "colloquial forms of Arabic do not have case marking" (p. 166), and "In spoken Arabic, the tens numbers
  are reduced to one case, the genitive-accusative" (p. 343, note 11). So the colloquial register reads the tens in
  the oblique form. It also reads every other number, the dual and the ordinals in the oblique form; no source gives
  this choice, and the README lists it. With no diacritics, the genitive and the accusative of a number are one
  written form, the oblique form of ovos-number-parser, and the oblique dual ends in -ayni (p. 332).
- Hundreds, thousands and millions. A dual before its counted noun drops its nuun (p. 347), a thousand or a million
  counted from 11 to 99 with no noun is an accusative tamyiz (pp. 350 and 353), and a scale word makes the million
  the counted noun of an amount (p. 353).
- Ordinals follow the noun that they rank and agree with it (pp. 354-359). A date reads the day as a masculine
  ordinal, then من and the month (pp. 357-358). A numeric date with the era mark هـ or ه after it is a date of the
  Hijri calendar: the month is the Hijri month, and the mark reads هجري (English Wiktionary, هـ: "abbreviation of
  هِجْرِيّ (hijriyy): in the year of the Hegira (AH)"). The mark م after a numeric date reads ميلادي (English
  Wiktionary, م: "abbreviation of مِيلَادِيّ (mīlādiyy), AD, CE").
  In a range of days before one month, the first day is a date of that month and reads as an ordinal too, as
  Arabic Wikipedia writes it: "من الأول إلى السابع من آذار" (أستراليا في الألعاب البارالمبية الشتوية 2002, oldid
  71881762) and "من الثاني إلى الرابع من فبراير" (ردود الفعل على الأمر التنفيذي رقم 13769, oldid 76868665).
  Before the definite article, li- drops the alif of the article: "the laam of li- attaches directly to the laam
  of the definite article (e.g., li-l-jaamicat-i)" (p. 371). So للطابق is ل and الطابق.
- Ranges. إلى is a preposition, so the number after it is genitive (pp. 366-367). In a range of two percentages,
  amounts or times, such as `10%-20%`, the second takes the genitive too.
- Fractions from 2 to 10 read by name (pp. 360-361). The time reads the hour as a feminine ordinal, and the quarters,
  thirds and halves of the hour, with إلا before the next hour (pp. 361-362). The day period of an hour comes from
  the CLDR 49 day period rules of `ar` (`dayPeriods.json`). "The word “hour” (saaca) may or may not be mentioned,
  but the ordinal numeral is in the feminine form, agreeing with that noun": "fii l-saacat-i l-thaaminat-i", "at
  eight o'clock" (p. 361). So a whole hour after الساعة reads as the hour of a time.
- The CLDR 49 format names of the day periods of `ar` are ص and م (`ca-gregorian.json`, dayPeriods, format), and
  the short time pattern is "h:mm a". So ص and م after a time are its day period. م is also the CLDR 49 short
  symbol of the metre (`units.json`, length-meter), so an hour with no minutes takes ص or م only after الساعة.
- Percent: the number and في المئة (p. 347). "To express the concept of percent, the term fii l-mi'at-i or
  bi-l-mi'at-i is used", and the number takes the form with taa' marbuuTa before it: "yu-mlik-aani xamsat-a 'ashar-a
  fii l-mi'at-i min-a l-sharikat-i", "The two of them own 15 percent of the company" (p. 347). So a written percent
  word after the number, such as بالمئة, is no noun that the number counts: `ارتفع 5 بالمئة` reads خمسة, as `5%`
  does. CLDR 49 writes the long name of concentr-percent as "{0} بالمائة" (`units.json`), and مائة is an
  "alternative spelling of مِئَة" (English Wiktionary, مائة, revision 93330307).
  CLDR 49 writes the sign after the number in logical order (`#,##0%`),
  and a right-to-left line shows that sign to the left of the number, so a percentage typed as it looks, `%10`,
  reads the same. The decimal word is فاصلة (Wiktionary, فاصلة, sense 6), and the word of the minus sign is سالب
  (Arabic Wikipedia, عدد سالب, section التسمية).
- كم before an indefinite noun is the question word "how many" (pp. 402-403), not the kilometre. كم is also the
  question word "how much" (p. 402) before a question mark, as in `كامري 2024 كم؟`, so the number reads alone and
  كم stays as written. No source gives this rule: CLDR 49 writes the short and narrow symbol of length-kilometer as
  كم, and a question mark does not change the symbol there. Latin `km` reads the kilometre before a question mark.

The `units` and `currencies` tables give each noun in every count form, with the nominative and the oblique dual.
CLDR 49 does not: `units.json` writes the dual of length-kilometer as "{0} كيلومتر", writes mass-kilogram as
"{0} كيلوغرام" in every count, and `currencies.json` gives USD and SAR one name with no count forms. The count forms
of دولار, ريال and كيلوغرام come from Wiktionary. A speed counts the kilometre and adds في الساعة: "miJat-in
wa-sab'iina kiiluumitr-an fii l-saacat-i", "170 kilometers an hour" (p. 349), as the CLDR 49 long name of
speed-kilometer-per-hour, "{0} كيلومتر في الساعة", does.

The file claims no ordinal in plain text. A say-as ordinal (text2spoken design, section 17.5) reads through the
ordinal of ovos-number-parser in the default gender, the masculine: `3` reads "الثالث".

Ryding 2005 is Karin C. Ryding, *A Reference Grammar of Modern Standard Arabic*, Cambridge University Press. Wright
1896 is W. Wright, *A Grammar of the Arabic Language*, 3rd edition, volume 1.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.currencies import has_sign
from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category, primary_subtag
from text2spoken.core.recognizers import (SHARED, Cardinal as CoreCardinal, Measure as CoreMeasure, Money as CoreMoney,
                                         TimeClock, speak_lexicon)
from text2spoken.core.spans import Features, Span, SpanContext, clause_window, context_words
from text2spoken.core.spellers import OvosNumberSpeller, bounded_integer
from text2spoken.core.times import day_hour, twelve_hour
from text2spoken.core.tokens import Token, fold_digits, is_bounded, is_letter, one_digit_set
from text2spoken.errors import DeclinedReading
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

MASCULINE, FEMININE = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE
NOMINATIVE, OBLIQUE = "nominative", "oblique"

SERVES = ("aao", "abh", "abv", "acm", "acq", "acw", "acx", "adf", "aeb", "aec", "afb", "apc", "apd", "arb",
          "arq", "ars", "ary", "arz", "auz", "avl", "ayh", "ayl", "ayn", "ayp", "shu", "ssh")
"""The active members of the ISO 639-3 macrolanguage `ara` that write Arabic script. `acy` and `pga` write Latin
script (CLDR likely subtags), and `ajp` and `bbz` are retired codes."""

LECT_REGIONS = {
    "aao": "DZ",  # "aao": "aao-Arab-DZ"; Glottolog alge1240: DZ, EH, LY, MA, NE
    "abh": "TJ",  # "abh": "abh-Arab-TJ"; Glottolog taji1248: AF, TJ, UZ
    "abv": "BH",  # "abv": "abv-Arab-BH"; Glottolog baha1259: BH, OM
    "acm": "IQ",  # "acm": "acm-Arab-IQ"; Glottolog meso1252: IQ, IR, JO, SY, TR
    "acq": "YE",  # "acq": "acq-Arab-YE"; Glottolog taiz1242: ER, SA, YE
    "acw": "SA",  # "acw": "acw-Arab-SA"; Glottolog hija1235: SA, YE
    "acx": "OM",  # "acx": "acx-Arab-OM"; Glottolog oman1239: AE, OM
    "adf": "OM",  # "adf": "adf-Arab-OM"; Glottolog dhof1235: OM
    "aeb": "TN",  # "aeb": "aeb-Arab-TN"; Glottolog tuni1259: DZ, LY, TN
    "aec": "EG",  # "aec": "aec-Arab-EG"; Glottolog said1239: EG, SD
    "afb": "KW",  # "afb": "afb-Arab-KW"; Glottolog gulf1241: AE, BH, IQ, IR, KW, OM, QA, SA, YE
    "apc": "SY",  # "apc": "apc-Arab-SY"; Glottolog nort3139: IL, LB, SY, TR
    "apd": "SD",  # "apd": "apd-Arab-SD"; Glottolog suda1236: CF, EG, ER, ET, LY, SD, TD
    "arq": "DZ",  # "arq": "arq-Arab-DZ"; Glottolog alge1239: DZ, MA, TN
    "ars": "SA",  # "ars": "ars-Arab-SA"; Glottolog najd1235: AE, IL, IQ, JO, KW, LB, SA, SY, TR, YE
    "ary": "MA",  # "ary": "ary-Arab-MA"; Glottolog moro1292: DZ, EH, MA
    "arz": "EG",  # "arz": "arz-Arab-EG"; Glottolog egyp1253: EG, IL, LY
    "auz": "UZ",  # "auz": "auz-Arab-UZ"; Glottolog uzbe1248: UZ
    "avl": "EG",  # "avl": "avl-Arab-EG"; Glottolog east2690: EG, IL, JO, PS, SA
    "ayh": "YE",  # "ayh": "ayh-Arab-YE"; Glottolog hadr1236: SA, YE
    "ayl": "LY",  # "ayl": "ayl-Arab-LY"; Glottolog liby1240: EG, LY, NE
    "ayn": "YE",  # "ayn": "ayn-Arab-YE"; Glottolog sana1295: SA, YE
    "ayp": "IQ",  # "ayp": "ayp-Arab-IQ"; Glottolog nort3142: IQ, JO, SY, TR
    "shu": "TD",  # "shu": "shu-Arab-TD"; Glottolog chad1249: CM, NE, NG, TD
    "ssh": "AE",  # "ssh": "ssh-Arab-AE"; Glottolog shih1239: AE, OM
}
"""The region of each spoken lect: the line of CLDR 49 `likelySubtags.json` for the code, and the countries of the
Glottolog languoid of the code, which hold the region. A tag with no region, or with a region that the lect has no
variety for, reads this region."""

SYRIAC_MONTHS = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول",
                 "تشرين الثاني", "كانون الأول"]
MAGHREB_MONTHS = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر",
                  "ديسمبر"]

DAY_PERIOD_HOURS = (("night2", 1, 3), ("morning1", 3, 6), ("morning2", 6, 12), ("afternoon1", 12, 13),
                    ("afternoon2", 13, 18), ("evening1", 18, 24))
"""The CLDR day period rules of `ar` (supplemental dayPeriods.json): each period with its first hour and the hour
that ends it. The period `night1`, from 00:00 to 01:00, has the CLDR name "في المساء", which no source here
confirms for midnight, so a time in it declines."""

KILOMETRE = {"gender": "masculine", "one": "كيلومتر", "two": ["كيلومتران", "كيلومترين"], "few": "كيلومترات",
             "many": "كيلومترا", "other": "كيلومتر"}
KILOMETRE_PER_HOUR = {**KILOMETRE, "per": "في الساعة"}
KILOGRAM = {"gender": "masculine", "one": "كيلوغرام", "two": ["كيلوغرامان", "كيلوغرامين"], "few": "كيلوغرامات",
            "many": "كيلوغراما", "other": "كيلوغرام"}

CLDR_CURRENCIES = (
    ("AED", "د.إ.\u200f", "masculine", "درهم إماراتي", "درهمان إماراتيان", "دراهم إماراتية", "درهما إماراتيا"),
    ("BHD", "د.ب.\u200f", "masculine", "دينار بحريني", "ديناران بحرينيان", "دنانير بحرينية", "دينارا بحرينيا"),
    ("DZD", "د.ج.\u200f", "masculine", "دينار جزائري", "ديناران جزائريان", "دينارات جزائرية", "دينارا جزائريا"),
    ("EGP", "ج.م.\u200f", "masculine", "جنيه مصري", "جنيهان مصريان", "جنيهات مصرية", "جنيها مصريا"),
    ("IQD", "د.ع.\u200f", "masculine", "دينار عراقي", "ديناران عراقيان", "دنانير عراقية", "دينارا عراقيا"),
    ("IRR", "ر.إ.", "masculine", "ريال إيراني", "ريالان إيرانيان", "ريالات إيرانية", "ريالا إيرانيا"),
    ("JOD", "", "masculine", "دينار أردني", "ديناران أردنيان", "دنانير أردنية", "دينارا أردنيا"),
    ("KWD", "د.ك.\u200f", "masculine", "دينار كويتي", "ديناران كويتيان", "دنانير كويتية", "دينارا كويتيا"),
    ("LBP", "ل.ل.\u200f", "feminine", "ليرة لبنانية", "ليرتان لبنانيتان", "ليرات لبنانية", "ليرة لبنانية"),
    ("LYD", "د.ل.\u200f", "masculine", "دينار ليبي", "ديناران ليبيان", "دينارات ليبية", "دينارا ليبيا"),
    ("MAD", "د.م.\u200f", "masculine", "درهم مغربي", "درهمان مغربيان", "دراهم مغربية", "درهما مغربيا"),
    ("OMR", "ر.ع.\u200f", "masculine", "ريال عماني", "ريالان عمانيان", "ريالات عمانية", "ريالا عمانيا"),
    ("QAR", "ر.ق.\u200f", "masculine", "ريال قطري", "ريالان قطريان", "ريالات قطرية", "ريالا قطريا"),
    ("SDG", "ج.س.", "masculine", "جنيه سوداني", "جنيهان سودانيان", "جنيهات سودانية", "جنيها سودانيا"),
    ("SYP", "ل.س.\u200f", "feminine", "ليرة سورية", "ليرتان سوريتان", "ليرات سورية", "ليرة سورية"),
    ("TND", "د.ت.\u200f", "masculine", "دينار تونسي", "ديناران تونسيان", "دينارات تونسية", "دينارا تونسيا"),
    ("YER", "ر.ي.\u200f", "masculine", "ريال يمني", "ريالان يمنيان", "ريالات يمنية", "ريالا يمنيا"),
)
"""The currencies with a CLDR 49 `symbol` in Arabic letters in `cldr-numbers-full/main/ar/currencies.json`, with
the symbol as CLDR writes it, the gender of the noun and the count forms of the name: one (and other), the nominative
dual, few and many. Three CLDR symbols do not read, because running text uses them for something else. Lebanese
classified ads write the JOD symbol د.أ for a price in US dollars, as in `1,000 د. أ: تصميم … في لبنان`, so JOD holds
no symbol here and only its code reads. MRU, whose symbol أ.م. also starts the abbreviations of Lebanese law codes,
as in `المادة 579 أ.م.م`, and SDD, which Sudan stopped using in 2007 (CLDR 49 `currencyData.json`, region SD), stay
out."""


def _cldr_currency(code: str, symbol: str, gender: str, one: str, two: str, few: str, many: str) -> dict:
    """An entry of the `currencies` table. The ISO 4217 code reads, and so does the CLDR symbol with or without a
    space after its inner full stop. The trailing full stop of the symbol, and U+200F after it, stay as written, so
    the full stop of a sentence that ends in the symbol stays too. The oblique dual ends in -ayni where the
    nominative ends in -aani (Ryding 2005, p. 332)."""
    bare = symbol.rstrip(".\u200f")
    oblique = " ".join(word[:-2] + "ين" for word in two.split())
    symbols = [code, bare, bare.replace(".", ". ")] if bare else [code]
    return {"symbols": symbols, "gender": gender, "one": one, "two": [two, oblique], "few": few, "many": many,
            "other": one}


SCALE_DUALS = ("مئتان", "مئتين", "ألفان", "ألفين", "مليونان", "مليونين")

DATA = freeze({
    "number_marks": {"Arab": [{"decimal": "٫", "group": "٬"}],
                     "Latn": [{"decimal": ",", "group": "."}, {"decimal": ".", "group": ","}]},
    "defaults": {"date_order": "DMY", "clock": "12h", "decimal_mark": ".", "register": "formal"},
    "proclitics": ["ب", "بـ", "ل", "لـ", "و"],
    "prepositions": ["ب", "بـ", "ل", "لـ", "في", "من", "إلى", "على", "عن", "حتى", "منذ"],
    "semi_prepositions": ["بعد", "قبل", "نحو", "خلال", "طوال", "مع"],
    "year_nouns": {"عام": "masculine", "سنة": "feminine"},
    "feminine_plurals": ["مخطوطات", "قصائد", "مقابلات", "آبار", "مرات", "فرق", "ساعات", "سيارات", "دقائق",
                         "سنوات", "سنين", "ثوان", "ثواني", "ليال", "ليالي", "قطع", "نسخ", "دفعات", "سرعات",
                         "أسطوانات", "عجلات", "وسائد", "شاشات", "فئات", "رحلات", "غرف", "كلمات"],
    "afila_plurals": ["أسئلة", "أجهزة", "أنظمة", "أطعمة", "أندية", "أمثلة", "أشرطة", "أفدنة", "أعمدة", "أدوية", "أقنعة",
                      "ألوية", "أسلحة", "أجنحة", "أرصدة", "أنشطة", "أحزمة", "أرغفة", "أرصفة", "أحذية", "أبنية", "أغذية",
                      "أجوبة", "أوعية", "أروقة", "أوسمة", "أحصنة"],
    "rank_nouns": ["الطابق", "الفئة", "المرتبة", "القرن", "الدور", "الصف", "الجيل", "المركز", "الفصل", "الدرجة"],
    "label_nouns": ["رقم", "الرقم", "موديل", "موديلات"],
    "list_marks": ["-", ".", ")", "–"],
    "measure_nouns": ["أونصة", "بوصة", "ثانية", "درجة", "دقيقة", "دورة", "رشّة", "ساعة", "سعرة", "سنة", "شمعة", "عقدة",
                      "قامة", "قطرة", "قمحة", "ليلة", "ميكروثانية", "نقطة", "ياردة"],
    "sign_words": {"-": "سالب"},
    "leads": {"#": "رقم"},
    "decimal_word": "فاصلة",
    "fraction_names": {"2": ["نصف", "نصفان", "أنصاف"], "3": ["ثلث", "ثلثان", "أثلاث"],
                       "4": ["ربع", "ربعان", "أرباع"], "5": ["خمس", "خمسان", "أخماس"],
                       "6": ["سدس", "سدسان", "أسداس"], "7": ["سبع", "سبعان", "أسباع"],
                       "8": ["ثمن", "ثمنان", "أثمان"], "9": ["تسع", "تسعان", "أتساع"],
                       "10": ["عشر", "عشران", "أعشار"]},
    "construct_duals": list(SCALE_DUALS),
    "range_word": "إلى",
    "range_marks": ["-", "–"],
    "percent": {"signs": ["%", "٪"], "position": "either", "word": "في المئة"},
    "percent_words": ["في المئة", "في المائة", "بالمئة", "بالمائة"],
    "currencies": {
        "USD": {"symbols": ["$", "US$", "USD"], "gender": "masculine", "one": "دولار",
                "two": ["دولاران", "دولارين"], "few": "دولارات", "many": "دولارا", "other": "دولار"},
        "SAR": {"symbols": ["SAR"], "gender": "masculine", "one": "ريال سعودي",
                "two": ["ريالان سعوديان", "ريالين سعوديين"], "few": "ريالات سعودية", "many": "ريالا سعوديا",
                "other": "ريال سعودي"},
        "SAR-sign": {"symbols": ["ريال", "ر.س", "ر. س"], "gender": "masculine", "one": "ريال",
                     "two": ["ريالان", "ريالين"], "few": "ريالات", "many": "ريالا", "other": "ريال"},
        **{row[0]: _cldr_currency(*row) for row in CLDR_CURRENCIES},
    },
    "symbols_after_only": ["ريال"],
    "scales": {"مليون": "000000"},
    "units": {"كم": KILOMETRE, "km": KILOMETRE, "كم/س": KILOMETRE_PER_HOUR, "km/h": KILOMETRE_PER_HOUR,
              "كغم": KILOGRAM, "kg": KILOGRAM},
    "dimension_marks": ["×"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"}],
    "time_words": ["الساعة"],
    "day_periods": {"am": ["صباحًا", "صباحا", "ص"], "pm": ["مساءً", "مساء", "م"]},
    "short_periods": ["ص", "م"],
    "spoken_periods": {"morning1": "في الصباح", "morning2": "صباحا", "afternoon1": "ظهرا",
                       "afternoon2": "بعد الظهر", "evening1": "مساء", "night2": "ليلا"},
    "minute_phrases": {"0": "{hour}", "15": "{hour} والربع", "20": "{hour} والثلث", "30": "{hour} والنصف",
                       "40": "{next_hour} إلا ثلثا", "45": "{next_hour} إلا ربعا",
                       "other": "{hour} والدقيقة {minute}"},
    "months": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر",
               "ديسمبر"],
    "date_reading": {"full": "{day} من {month} {year}", "no_year": "{day} من {month}"},
    "hijri_months": ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
                     "رمضان", "شوال", "ذي القعدة", "ذي الحجة"],
    "era_marks": {"هـ": "هجري", "ه": "هجري", "م": "ميلادي"},
    "hijri_marks": ["هـ", "ه"],
    "symbols": {"%": "percent", "٪": "percent", "$": "money", "+": "expression", "=": "expression"},
})
"""Sources, by table. `number_marks`, `months`, `day_periods` and `spoken_periods`: CLDR 49 (numbers.json,
ca-gregorian.json, dayPeriods). `percent`: Ryding 2005, p. 347. `percent_words`: fii l-mi'at-i and bi-l-mi'at-i of
Ryding 2005, p. 347, the long name بالمائة of CLDR 49 concentr-percent (units.json), and each in both spellings of مئة
(English Wiktionary, مائة, revision 93330307). `prepositions`: Ryding 2005, pp. 366-367.
`hijri_months`: Arabic Wikipedia, تقويم هجري, the table of months, which gives ربيع الآخر and جمادى الآخرة; the
two months that start with ذو take the genitive ذي after من, as Arabic Wikipedia, ذو الحجة, writes it:
"العشر الأوائل من ذي الحجة". `semi_prepositions`: Ryding 2005, chapter 16, sections 3.4 bacd-a (p. 388), 3.18 maca (p. 393), 3.20 naHw-a and
3.21.1 qabl-a (p. 395), 3.25 Tiwaal-a (p. 397) and 3.31 xilaal-a (p. 398). `year_nouns`: Ryding 2005, pp. 351-353.
`feminine_plurals`: the counted plurals of Ryding 2005, pp. 335-336, دقائق of CLDR (units.json, duration-minute), and
سنوات, the plural of the feminine sana (pp. 352-353). ثوان is the few form of the feminine duration-second of CLDR
(units.json). Each other plural is counted by the short form of a number in an Arabic Wikipedia revision, and its
singular ends in taa' marbuuTa: سنين (سنة, oldid 72786001, "ثلاث سنين"), ثواني (ثانية, 72093480, "ثلاث ثواني"), ليال and
ليالي (ليلة, 72678607, "سبع ليال", and 75675456, "ثلاث ليالي"), قطع (قطعة, 76375538, "ست قطع"), نسخ (نسخة, 76989156,
"ثلاث نسخ"), دفعات (دفعة, 75774492, "أربع دفعات"), سرعات (سرعة, 72665705, "ثماني سرعات"), أسطوانات (أسطوانة, 76540398,
"ست أسطوانات"), عجلات (عجلة, 77054753, "أربع عجلات"), وسائد (وسادة, 75479234, "ست وسائد"), شاشات (شاشة, 74093250, "ثلاث
شاشات"), فئات (فئة, 68531917, "خمس فئات"), رحلات (رحلة, 75094475, "ثلاث رحلات"), غرف (غرفة, 76576561, "أربع غرف") and
كلمات (كلمة, 73435197, "خمس كلمات"). `afila_plurals`: the plural of each masculine noun in an English Wiktionary revision, which gives the plural of the entry: أسئلة (سؤال, 92009884), أجهزة (جهاز, 95648366), أنظمة (نظام, 95814058), أطعمة (طعام, 95461735), أندية (ناد, 93332440), أمثلة (مثال, 95375051), أشرطة (شريط, 93327209), أفدنة (فدان, 93328884), أعمدة (عمود, 92948489), أدوية (دواء, 92972104), أقنعة (قناع, 93329489), ألوية (لواء, 92915299), أسلحة (سلاح, 92980330), أجنحة (جناح, 95809883), أرصدة (رصيد, 93325997), أنشطة (نشاط, 93332662), أحزمة (حزام, 93324830), أرغفة (رغيف, 91190377), أرصفة (رصيف, 95798928), أحذية (حذاء, 95843289), أبنية (بناء, 95498261), أغذية (غذاء, 93328628), أجوبة (جواب, 93364138), أوعية (وعاء, 95648404), أروقة (رواق, 88967129), أوسمة (وسام, 88977656) and أحصنة (حصان, 93377187). Each entry reads `{{ar-noun|…|m|pl=…}}`. `label_nouns`: the noun raqm of Ryding 2005, p. 335, with and without the
article, and موديل with its plural موديلات, which no source names as a label noun. `list_marks`: the marks after a
list number at the start of a line; no source names them. `measure_nouns`: the long names of
CLDR 49 units.json (ar) that end in taa' marbuuTa; CLDR writes the few count of some of them in the singular, as "{0}
بوصة" of length-inch. `rank_nouns`: nouns that an ordinal follows (Ryding 2005, pp. 354-359). An Arabic
Wikipedia revision shows each noun before an agreeing ordinal: الدور (oldid 74639116, "الدور الخامس والثلاثين"), الصف
(74030867, "الصف الثالث والثلاثين"), الجيل (76361085, "الجيل السادس والسبعين"), المركز (73375269, "المركز التاسع
والتسعين"), الفصل (73569717, "الفصل السادس والتسعين") and الدرجة (76373966, "الدرجة الثالثة والأربعين"). `currencies`:
`SAR` reads the CLDR name ريال سعودي, and the sign ر.س (English Wikipedia, Saudi riyal, revision 1252604873) and the
word ريال read ريال. Each currency of `CLDR_CURRENCIES` reads its CLDR 49 `displayName` (`currencies.json` of `ar`),
and its count forms are the `displayName-count-*` names where CLDR gives them, for DZD, EGP, LYD, MAD and TND, with
the tanween mark left out. The genders and the other count forms come from the nouns of Wiktionary, درهم (revision
95817866, masculine, plural دراهم), دينار (95819933, masculine, plural دنانير), جنيه (95643228, masculine, plural
جنيهات), ريال (95819810, masculine, plural ريالات) and ليرة (91168060, feminine, plural ليرات), and from the
agreement of the adjective (Ryding 2005, pp. 242-243): a dual adjective after a dual noun, as safiinat-aani
kabiirat-aani, and a feminine singular adjective after a plural noun that names no person. So the dual of LBP and
SDG is ليرتان لبنانيتان and جنيهان سودانيان, where CLDR writes the singular. `fraction_names`: Ryding 2005,
pp. 360-361. `minute_phrases`: Ryding 2005, pp. 361-362.
`decimal_word`: Wiktionary, فاصلة, sense "decimal point". `sign_words`: Arabic Wikipedia, عدد سالب, section التسمية. The
count forms of `currencies` and `units`: Wiktionary دولار, ريال and كيلوغرام (revision 95591224: masculine, with the
sound feminine plural), CLDR units.json (length-kilometer, and the symbols كغم of mass-kilogram and كم/س of
speed-kilometer-per-hour), and the count rules of Ryding 2005, pp. 330-345. `symbols_after_only`: ريال is a counted
noun, which follows the number (Ryding 2005, p. 335). `short_periods`: the CLDR 49 format names of `day_periods`."""

VARIETIES = (
    Variety("ar-001"),
    *(Variety(f"ar-{region}") for region in ("AE", "BH", "DJ", "EG", "EH", "ER", "IL", "KM", "KW", "OM", "QA", "SA",
                                             "SD", "SO", "SS", "TD", "YE")),
    Variety("ar-DZ", freeze({"defaults": {"decimal_mark": ","}, "months": MAGHREB_MONTHS})),
    Variety("ar-TN", freeze({"defaults": {"decimal_mark": ","}, "months": MAGHREB_MONTHS})),
    Variety("ar-IQ", freeze({"months": SYRIAC_MONTHS})),
    Variety("ar-JO", freeze({"months": SYRIAC_MONTHS})),
    Variety("ar-PS", freeze({"months": SYRIAC_MONTHS})),
    Variety("ar-SY", freeze({"months": SYRIAC_MONTHS})),
    Variety("ar-LB", freeze({"defaults": {"decimal_mark": ","}, "months": SYRIAC_MONTHS})),
    Variety("ar-LY", freeze({"defaults": {"decimal_mark": ","}})),
    Variety("ar-MA", freeze({"defaults": {"decimal_mark": ","},
                             "months": ["يناير", "فبراير", "مارس", "أبريل", "ماي", "يونيو", "يوليوز", "غشت", "شتنبر",
                                        "أكتوبر", "نونبر", "دجنبر"]})),
    Variety("ar-MR", freeze({"defaults": {"decimal_mark": ","},
                             "months": ["يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو", "يوليو", "أغشت", "شتمبر",
                                        "أكتوبر", "نوفمبر", "دجمبر"]})),
)
"""The CLDR 49 locales of `ar`. A locale whose month names or Latin number marks differ from `ar` holds them. Each
other region reads as `ar-001`. The varieties with no data come first, because `closest_lang` gives a tie to the
first candidate."""

REGION_DATA = {variety.tag.split("-")[1]: variety.data for variety in VARIETIES}


def _lect_variety(code: str, region: str) -> Variety:
    """A spoken lect in its region: the month names and the number marks of the region, and the colloquial
    register (Ryding 2005, p. 166)."""
    data = REGION_DATA.get(region, FrozenMap())
    defaults = {**data.get("defaults", FrozenMap()), "register": "colloquial"}
    return Variety(f"{code}-{region}", freeze({**data, "defaults": defaults}))


LECT_VARIETIES = tuple(_lect_variety(code, region) for code, region in LECT_REGIONS.items())


class ArabicSpeller:
    """ovos-number-parser, with the code of the lect in the colloquial register for a lect of `LECT_REGIONS`, and
    with the tag `ar` for every other request: the formal register reads the literary words. A decimal reads the
    integer, the decimal word and the fraction digits as one number (Wiktionary, فاصلة), and a fraction reads its
    denominator by name, from 2 to 10 (Ryding 2005, pp. 360-361)."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    @staticmethod
    def _writer(request: Request) -> Request:
        code = primary_subtag(request.tag)
        lect = code in LECT_REGIONS and request.params.register == "colloquial"
        return replace(request, tag=code if lect else "ar")

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.cardinal(digits, features, self._writer(request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.ordinal(digits, features, self._writer(request))

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        if len(fraction) > 1 and fraction[0] == "0":
            raise DeclinedReading("no source gives the reading of a fraction part that starts with zero")
        whole = self.cardinal(integer or "0", features, request)
        return f"{whole} {request.data['decimal_word']} {self.cardinal(fraction, features, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        names = request.data["fraction_names"].get(str(bounded_integer(denominator)))
        top = bounded_integer(numerator)
        if names is None or top is None or top < 1:
            raise DeclinedReading(f"no fraction name for {numerator}/{denominator}")
        if top == 1:
            return names[0]
        if top == 2:
            return _dual(names[1], features.case)
        count = self.cardinal(numerator, Features(gender=MASCULINE, case=features.case), request)
        return f"{count} {names[2]}"


SPELLER = ArabicSpeller()


def _dual(nominative: str, case: str | None) -> str:
    """The oblique dual ends in -ayni where the nominative ends in -aani (Ryding 2005, p. 332)."""
    return nominative[:-2] + "ين" if case == OBLIQUE else nominative


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """A proclitic joins the first spoken word; the tatweel of `بـ` only joins it to a digit."""
    return prefix.rstrip("ـ") + spoken + suffix


def _is_arabic_word(word: str) -> bool:
    return all("\u0621" <= char <= "\u064a" for char in word)


def counted_noun(after: Sequence[str]) -> str | None:
    """The indefinite Arabic word right after the number, which the number counts (Ryding 2005, p. 335)."""
    if not after:
        return None
    word = after[0]
    return word if _is_arabic_word(word) and not word.startswith("ال") else None


def number_noun(span: Span, context: SpanContext) -> str | None:
    """The noun that the number counts: the word of `counted_noun`, but none after a label noun or the lead #, and
    none before a percent word, as in `5 بالمئة` (Ryding 2005, p. 347). A number that names a thing counts no noun
    (p. 335: raqm-u sittat-in). A number from 3 to 10 counts a plural (p. 335), so after a code in Latin letters, as
    in `MG 5 متوفرة`, a singular in taa' marbuuTa is no noun that it counts, unless it names a unit of
    `measure_nouns`, as in `Wusthof 7 بوصة`. A list number at the start of a line counts no noun, nor does a number
    before a definite word, as in `فاز 5 بالجائزة` (p. 335)."""
    request = context.request
    if span.fields.get("lead") or noun_before(context, request.data["label_nouns"]):
        return None
    after, percent_words = context.after, request.data["percent_words"]
    if after and (after[0] in percent_words or " ".join(after[:2]) in percent_words):
        return None
    noun = counted_noun(context.after)
    if (noun is not None and noun.endswith("ة") and noun not in request.data["measure_nouns"]
            and span.form is Form.CARDINAL and span.start in request.memo.get(_CODED, ())
            and plural_category(request, fold_digits(span.fields["digits"])) == "few"):
        return None
    if span.form is Form.CARDINAL and span.start in request.memo.get(_LISTED, ()):
        return None
    return None if noun is not None and DEFINITE.match(noun) else noun


def hour_after(before: Sequence[str], digits: str, after: Sequence[str], data: FrozenMap) -> bool:
    """Whether a whole hour right after الساعة reads as the hour of a time (Ryding 2005, p. 361). It does not before
    a noun that the number counts, as in حتى الساعة 10 شهداء (p. 335): و, إلى, a definite word, a day period or the end
    of the clause may follow the hour. A speed reads في الساعة after its unit, as in "… miJat-in wa-sab'iina
    kiiluumitr-an fii l-saacat-i" (p. 349). A number with a leading zero, and 1 or 2 before a noun that it counts
    (pp. 330 and 333), stay as written, so they stay as written after في الساعة too. This last rule is the inference
    of this file, with no source: it makes a second pass read the same text."""
    digits = fold_digits(digits)
    if not before or before[-1] not in data["time_words"] or int(digits) > 23 or (len(digits) > 1 and digits[0] == "0"):
        return False
    noun = counted_noun(after)
    if noun is None:
        return True
    if digits in ("1", "2") and len(before) > 1 and before[-2].removeprefix("و") == "في":
        return False
    periods = data["spoken_periods"].values()
    return (noun.startswith("وال") or noun in ("و", data["range_word"]) or noun in periods
            or " ".join(after[:2]) in periods or any(noun in forms for forms in data["day_periods"].values()))


def noun_gender(noun: str, data: FrozenMap) -> GrammaticalGender:
    """Feminine for a noun that ends in taa' marbuuTa (Ryding 2005, p. 121) or for a plural of the table: a plural
    in -aat also comes from masculine nouns (Wright 1896, vol. 1, section 303), so no rule reads it. A plural of
    `afila_plurals` ends in taa' marbuuTa and is masculine."""
    if noun in data["afila_plurals"]:
        return MASCULINE
    return FEMININE if noun.endswith("ة") or noun in data["feminine_plurals"] else MASCULINE


def _governs(word: str, data: FrozenMap) -> bool:
    """Whether a word right before a number is a preposition or a semi-preposition, whose object is genitive
    (Ryding 2005, p. 367)."""
    return word in data["prepositions"] or word in data["semi_prepositions"]


def _case(span: Span, context: SpanContext) -> str:
    """Oblique after a preposition, a semi-preposition, a year noun or the range word, else nominative. The colloquial
    register reads every number oblique: Ryding 2005, p. 343, note 11, gives the genitive-accusative for the spoken
    tens only, and the README lists the rest as a choice with no source."""
    request = context.request
    if context.hint is not None and context.hint.case is not None:
        return context.hint.case
    data = request.data
    before = context.before[-1] if context.before else ""
    if (request.params.register == "colloquial" or span.fields.get("prefix", "") in data["prepositions"]
            or _governs(before, data) or before in data["year_nouns"] or span.lead.strip() == data["range_word"]):
        return OBLIQUE
    return NOMINATIVE


def agreement(span: Span, context: SpanContext, gender: GrammaticalGender | None = None) -> Features:
    """The agreement order of design section 5.6: the hint, the noun that the form names, the year noun before the
    number, the counted noun after it, the params, the file."""
    request = context.request
    if context.hint is not None and context.hint.gender is not None:
        gender = context.hint.gender
    elif gender is None:
        before = context.before[-1] if context.before else ""
        noun = number_noun(span, context)
        if before in request.data["year_nouns"]:
            gender = GrammaticalGender(request.data["year_nouns"][before])
        elif noun is not None:
            gender = noun_gender(noun, request.data)
        else:
            gender = request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender
    return Features(gender=gender, case=_case(span, context))


def _before_noun(words: str, gender: GrammaticalGender, data: FrozenMap) -> str:
    """A number right before the noun that it counts. A dual drops its final nuun (Ryding 2005, p. 347:
    mi'at-aa fils-in), and eight before a feminine plural is ثماني (p. 336: thamaanii saa'aat-in)."""
    head, _, last = words.rpartition(" ")
    link = "و" if last.startswith("و") and last[1:] in data["construct_duals"] else ""
    if last[len(link):] in data["construct_duals"]:
        words = f"{head} {last[:-1]}".strip()
    return words + "ي" if gender == FEMININE and words.endswith("ثمان") else words


def _alone(words: str, digits: str) -> str:
    """A thousand or a million counted from 11 to 99 with no noun after it is an accusative tamyiz: 'alf-an
    (Ryding 2005, p. 350), and a million counts the same way (p. 353)."""
    value = bounded_integer(digits)
    for size, word in ((1_000, "ألف"), (1_000_000, "مليون")):
        if value and value % size == 0 and 11 <= value // size % 100 <= 99 and value // size < 1000 \
                and words.endswith(" " + word):
            return words + "ا"
    return words


def _signed(words: str, sign: str, request: Request) -> str:
    """The word of the sign before the number. A sign with no word in `sign_words`, such as `+`, declines the
    reading, so the span stays as written."""
    if not sign:
        return words
    if sign not in request.data["sign_words"]:
        raise DeclinedReading(f"no cited word for the sign {sign}")
    return f"{request.data['sign_words'][sign]} {words}"


def noun_before(context: SpanContext, nouns: Sequence[str]) -> tuple[str, str] | None:
    """The noun of `nouns` right before the number, as in الطابق 3, بالمرتبة 1 and للطابق 3, with its proclitic."""
    if not context.before:
        return None
    word = context.before[-1]
    if word.startswith("لل") and (noun := "ا" + word[1:]) in nouns:
        return "ل", noun
    for proclitic in ("", *context.request.data["proclitics"]):
        if word.startswith(proclitic) and word[len(proclitic):] in nouns:
            return proclitic, word[len(proclitic):]
    return None


def speak_rank(span: Span, context: SpanContext, proclitic: str, noun: str) -> str:
    """An ordinal follows the noun that it ranks and agrees with it in gender, case and definiteness (Ryding 2005,
    pp. 354 and 359: fii l-qarn-i l-Haadii wa-l-'ishriina)."""
    request = context.request
    hint = context.hint or Features()
    before = context.before[-2] if len(context.before) > 1 else ""
    oblique = (request.params.register == "colloquial" or proclitic in request.data["prepositions"]
               or _governs(before, request.data))
    features = Features(gender=hint.gender or noun_gender(noun, request.data),
                        case=hint.case or (OBLIQUE if oblique else NOMINATIVE))
    return SPELLER.ordinal(span.fields["digits"], features, request)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """One and two follow the noun that they count (Ryding 2005, pp. 330 and 333), so a digit 1 or 2 before a noun
    stays as written. A whole hour after الساعة reads as the hour of a time, as `hour_after` gives. An hour that the
    clock does not read, such as 13, stays as written whatever follows it, so that a second pass reads the same
    text. The first day of a range of days before a month, as 1 in من 1 إلى 7 مارس, is a date."""
    fields, request, before, after = span.fields, context.request, context.before, context.after
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        raise DeclinedReading("a number with a leading zero has no cited reading")
    if (not (fields["sign"] or fields["lead"]) and before and before[-1] in request.data["time_words"]
            and int(digits) <= 23):
        hour = clock(int(digits), 0, None, request)  # declines 0, 1 and 13, so they stay as written here
        if hour_after(before, digits, after, request.data):
            return hour
    if (len(after) > 2 and after[0] == request.data["range_word"] and not (fields["sign"] or fields["lead"])
            and (high := fold_digits(after[1])).isdigit() and 1 <= int(digits) < int(high) <= 31
            and any(name.split()[0] == after[2] for name in request.data["months"])):
        return SPELLER.ordinal(digits, Features(gender=MASCULINE, case=_case(span, context)), request)
    rank = noun_before(context, request.data["rank_nouns"])
    if rank is not None and not (fields["sign"] or fields["lead"]) and 1 <= int(digits) <= 99:
        return speak_rank(span, context, *rank)
    noun = number_noun(span, context)
    if noun is not None and digits in ("1", "2"):
        raise DeclinedReading("one and two follow the noun that they count")
    features = agreement(span, context)
    words = SPELLER.cardinal(digits, features, request)
    if noun is None:
        words = _alone(words, digits)
    else:
        words = _before_noun(words, features.gender, request.data)
    words = _signed(words, fields["sign"], request)
    if fields["lead"]:
        words = f"{request.data['leads'][fields['lead']]} {words}"
    return words


def _amount(amount: FrozenMap, features: Features, request: Request) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], features, request)
    else:
        words = SPELLER.cardinal(amount["integer"] or "0", features, request)
    return _signed(words, amount["sign"], request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, agreement(span, context), context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction before a noun is the first term of an iDaafa, so a dual drops its nuun (Ryding 2005, pp. 360-361:
    thulth-ay-i l-a'Daa'-i)."""
    fields = span.fields
    if fields["whole"]:
        raise DeclinedReading("no cited reading for a mixed number")
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], agreement(span, context), context.request)
    if bounded_integer(fields["numerator"]) == 2 and context.after and _is_arabic_word(context.after[0]):
        words = words[:-1]
    return _signed(words, fields["sign"], context.request)


def join_range(span: Span, following: Span, range_word: str) -> tuple[Span, Span]:
    """The range word leads the second span, so `_case` reads that span in the genitive (Ryding 2005, pp. 366-367)."""
    return replace(span, end=following.start, trail=" "), replace(following, lead=f"{range_word} ")


def speak_range(span: Span, context: SpanContext) -> str:
    """The second number follows إلى, a preposition, so it is genitive (Ryding 2005, pp. 366-367)."""
    request = context.request
    features = agreement(span, context)
    low = SPELLER.cardinal(span.fields["low"], features, request)
    high = SPELLER.cardinal(span.fields["high"], replace(features, case=OBLIQUE), request)
    return f"{low} {request.data['range_word']} {high}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """"xamsat-a 'ashar-a fii l-mi'at-i": the number and في المئة (Ryding 2005, p. 347)."""
    request = context.request
    features = agreement(span, context, MASCULINE)
    return f"{_amount(span.fields['amount'], features, request)} {request.data['percent']['word']}"


def counted(digits: str, forms: FrozenMap, features: Features, request: Request) -> str:
    """A whole number and the noun that it counts, by CLDR plural category. One is the noun and واحد after it, in the
    gender of the noun (Ryding 2005, p. 330). CLDR 49 units.json writes the noun alone for one only for some units,
    such as duration-minute "دقيقة", and length-kilometer keeps the number, "{0} كيلومتر", so the file does not take
    this form from CLDR. Two is the dual (p. 332). Then come the number and the genitive plural (few), the
    accusative singular (many) or the genitive singular (other) (Ryding 2005, pp. 334-345 and 348-349)."""
    value = bounded_integer(digits)
    category = plural_category(request, digits)
    if category == "one":
        one = SPELLER.cardinal("1", replace(features, gender=GrammaticalGender(forms["gender"])), request)
        return f"{forms['one']} {one}"
    if category == "two":
        return forms["two"][1 if features.case == OBLIQUE else 0]
    if category == "zero" or value is None or (value > 100 and value % 100 in (1, 2)):
        raise DeclinedReading(f"no cited reading counts a noun with {len(digits)} digits ending in 0, 1 or 2")
    gender = GrammaticalGender(forms["gender"])
    number = SPELLER.cardinal(digits, replace(features, gender=gender), request)
    return f"{_before_noun(number, gender, request.data)} {forms[category]}"


def speak_money(span: Span, context: SpanContext) -> str:
    """A scale word makes the million the counted noun of the amount, and the currency follows in the genitive
    singular (Ryding 2005, p. 353: thalaathat-a balaayiin-i duulaar-in)."""
    request = context.request
    fields = span.fields
    amount = fields["amount"]
    currency = request.data["currencies"][fields["currency"]]
    if amount["fraction"] or amount["sign"]:
        raise DeclinedReading("no cited reading for a signed amount or an amount with a fraction")
    features = agreement(span, context, GrammaticalGender(currency["gender"]))
    if fields["scale"]:
        digits = amount["integer"] + request.data["scales"][fields["scale"]]
        number = SPELLER.cardinal(digits, replace(features, gender=MASCULINE), request)
        return f"{_before_noun(number, MASCULINE, request.data)} {currency['other']}"
    return counted(amount["integer"], currency, features, request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amount = span.fields["amount"]
    if isinstance(amount, tuple) or amount["fraction"] or amount["sign"]:
        raise DeclinedReading("no cited reading for a range, a dimension, a sign or a fraction of a unit")
    if (span.fields["unit"] == "كم" and counted_noun(context.after)
            and context.after[0] not in request.data["prepositions"]):
        raise DeclinedReading("كم before an indefinite noun is the question word 'how many' (Ryding 2005, pp. 402-403)")
    forms = request.data["units"][span.fields["unit"]]
    words = counted(amount["integer"], forms, agreement(span, context, GrammaticalGender(forms["gender"])), request)
    return f"{words} {forms['per']}" if "per" in forms else words


def speak_date(span: Span, context: SpanContext) -> str:
    """The day is a masculine ordinal, then من and the month (Ryding 2005, pp. 357-358), and the year is genitive,
    as after the year noun that may stand before it (pp. 351-353)."""
    request = context.request
    fields = span.fields
    era = fields["era"]
    month = request.data["hijri_months" if era in request.data["hijri_marks"] else "months"][fields["month"] - 1]
    day = SPELLER.ordinal(str(fields["day"]), Features(gender=MASCULINE, case=_case(span, context)), request)
    if fields["year"] is None:
        return request.data["date_reading"]["no_year"].format(day=day, month=month)
    year = SPELLER.year(str(fields["year"]), Features(gender=MASCULINE, case=OBLIQUE), request)
    spoken = request.data["date_reading"]["full"].format(day=day, month=month, year=year)
    return f"{spoken} {request.data['era_marks'][era]}" if era else spoken


def _day_period(hour: int, request: Request) -> str:
    for period, first, end in DAY_PERIOD_HOURS:
        if first <= hour < end:
            return request.data["spoken_periods"][period]
    raise DeclinedReading("no cited name for the day period from midnight to one")


def _clock_ordinal(digits: str, request: Request) -> str:
    """A feminine ordinal that agrees with saa'a or daqiiqa (Ryding 2005, p. 361), oblique in the colloquial
    register, as every other ordinal is."""
    case = OBLIQUE if request.params.register == "colloquial" else None
    return SPELLER.ordinal(digits, Features(gender=FEMININE, case=case), request)


def _hour(face: int, request: Request) -> str:
    """The hour is a feminine ordinal that agrees with saa'a (Ryding 2005, p. 361). For one o'clock the sources
    here give no form, so it declines."""
    if face == 1:
        raise DeclinedReading("no cited form for one o'clock")
    return _clock_ordinal(str(face), request)


def speak_time(span: Span, context: SpanContext) -> str:
    fields = span.fields
    if fields["second"] is not None:
        raise DeclinedReading("no cited reading for seconds")
    return clock(fields["hour"], fields["minute"], fields["period"], context.request)


def clock(written_hour: int, minute: int, period: str | None, request: Request) -> str:
    """Quarters, thirds and halves of the hour, with إلا before the next hour for 40 and 45 minutes, and other
    minutes as a feminine ordinal after والدقيقة (Ryding 2005, pp. 361-362). A written day period, or an hour
    from 13 to 23, reads the CLDR day period of the hour."""
    hour = day_hour(written_hour, period)
    phrases = request.data["minute_phrases"]
    template = phrases.get(str(minute), phrases["other"])
    next_hour = _hour(twelve_hour(hour + 1), request) if "{next_hour}" in template else ""
    words = template.format(hour=_hour(twelve_hour(hour), request) if "{hour}" in template else "",
                            next_hour=next_hour,
                            minute=_clock_ordinal(str(minute), request) if "{minute}" in template else "")
    if hour == 0 or period is not None or hour >= 13:
        words += " " + _day_period(hour, request)
    return words


@dataclass(frozen=True)
class Clock(TimeClock):
    """The core time, where an hour with no minutes before ص or م needs الساعة, as `hour_after` gives: `المسافة 7 م`
    is the metre."""

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for span in super()._times(text, tokens, request):
            written = text[span.start:span.end]
            if not (written.endswith(data["short_periods"]) and written[:-1].strip().isdigit()):
                yield span
                continue
            before = clause_window(text, context_words(tokens), span.start, span.end, -1, 2)
            if hour_after(before, written[:-1].strip(), (written[-1],), data):
                yield span


@dataclass(frozen=True)
class Money(CoreMoney):
    """The money of the core. The word ريال is a counted noun, which follows the number (Ryding 2005, p. 335), so
    `ريال 5` stays as written. The reading of an amount ends in ريال, so a digit after it would read on a second
    pass. A symbol joined by a full stop to another letter is part of a longer abbreviation, as ج.م in ج.م.ع, and a
    symbol joined by a slash to a Latin letter is part of a currency pair, as USD in EUR/USD, so neither reads.
    `speak_money` gives no reading for an amount with a fraction, so next to a symbol of letters such an amount reads
    as a number and the symbol stays as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        after_only = request.data["symbols_after_only"]
        for span in super().find(text, tokens, request):
            symbol = span.fields["written_symbol"]
            written = text[span.start:span.end]
            first = written.startswith(span.fields["prefix"] + symbol)
            edge = text[max(0, span.start - 2):span.start][::-1] if first else text[span.end:span.end + 2]
            mark, letter = edge[:1], edge[1:2]
            joined = is_letter(letter) and (mark == "." or mark == "/" and letter.isascii())
            if joined or (span.fields["amount"]["fraction"] and not has_sign(symbol)):
                continue
            first_digit = next(index for index, char in enumerate(written) if char.isdigit())
            yield replace(span, keep=True) if symbol in after_only and symbol in written[:first_digit] else span


_CODED = "ar_coded"
"""The key of `Request.memo` that holds the starts of the cardinal spans that a code in Latin letters comes right
before, as `Cardinal` finds them."""
_LISTED = "ar_listed"
"""The key of `Request.memo` that holds the starts of the cardinal spans that number an item of a list."""
DEFINITE = re.compile("(?:[وف]?[بكل]?ال|[وف]?لل)[ء-ي]{3}")
"""A word with the article after a proclitic: بالجائزة, للائحة, والسيارة, وبالمدينة. Three letters after the article
keep the nouns وكالة and وكالات out."""


@dataclass(frozen=True)
class Cardinal(CoreCardinal):
    """The cardinals of the core. A span right after a code in Latin letters and one space or a hyphen, as in `MG 5`
    and `CX-5`, puts its start into `Request.memo` under `_CODED`, which `number_noun` reads. The code starts the
    text or follows a space or `(`. A span that starts a line, with a mark of `list_marks` and a space or the end of
    the text after it, as in `4- وطبيعة`, puts its start under `_LISTED`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            end = first = span.start - 1
            if end > 0 and text[end] in " -":
                while first and text[first - 1].isascii() and text[first - 1].isalpha():
                    first -= 1
            if first < end and (first == 0 or text[first - 1].isspace() or text[first - 1] == "("):
                request.memo.setdefault(_CODED, set()).add(span.start)
            line_start = text.rfind("\n", 0, span.start) + 1
            if (not text[line_start:span.start].strip() and text[span.end:span.end + 1] in request.data["list_marks"]
                    and not text[span.end + 1:span.end + 2].strip()):
                request.memo.setdefault(_LISTED, set()).add(span.start)
            yield span


@dataclass(frozen=True)
class Measure(CoreMeasure):
    """The measures of the core. كم before a question mark is the question word "how much" (Ryding 2005, p. 402),
    as in `كامري 2024 كم؟`, so the number reads alone and كم stays as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            if not (span.fields["unit"] == "كم" and text[span.end:].lstrip().startswith(("؟", "?"))):
                yield span


@dataclass(frozen=True)
class EraDate:
    """`15/9/1447هـ`, `1447-12-10 هـ` and `5/3/2026م`: a numeric date, day first with slashes or year first with
    hyphens, and an era mark of `era_marks` right after it or after one space. A Hijri month has 29 or 30 days."""
    name: str = "date_era"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = "|".join(sorted(request.data["era_marks"], key=len, reverse=True))
        pattern = re.compile(f"(?:([0-9]{{1,2}})/([0-9]{{1,2}})/([0-9]{{3,4}})|([0-9]{{3,4}})-([0-9]{{1,2}})-([0-9]{{1,2}}))"
                             f" ?({marks})")
        for match in pattern.finditer(fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or not one_digit_set(text[start:end]):
                continue
            if match.group(1):
                day, month, year, order = int(match.group(1)), int(match.group(2)), int(match.group(3)), "DMY"
            else:
                year, month, day, order = int(match.group(4)), int(match.group(5)), int(match.group(6)), "YMD"
            hijri = match.group(7) in request.data["hijri_marks"]
            if not (1 <= month <= 12 and 1 <= day <= 30) if hijri else not is_valid(year, month, day):
                continue
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": order,
                                  "month_written": "digits", "era": match.group(7), "prefix": "", "suffix": ""}),
                       recognizer=self.name)


@dataclass(frozen=True)
class DateNamed:
    """`12 مارس 2024` and `12 مارس`: the CLDR long date `d MMMM y`, with the month names of the variety."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months = request.data["months"]
        names = "|".join(re.escape(m) for m in sorted(months, key=len, reverse=True))
        pattern = re.compile(f"([0-9][0-9]?) ({names})(?: ([0-9][0-9][0-9][0-9]))?")
        symbols = request.data["symbols"]
        for match in pattern.finditer(fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or (start and text[start - 1] in symbols) \
                    or not one_digit_set(text[start:end]):
                continue
            day, month = int(match.group(1)), months.index(match.group(2)) + 1
            year = int(match.group(3)) if match.group(3) else None
            if not is_valid(year, month, day):
                continue
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": "DMY",
                                  "month_written": "name", "era": "", "prefix": "", "suffix": ""}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="ar",
    serves=SERVES,
    cldr_aliases=(),
    varieties=VARIETIES + LECT_VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], EraDate(), DateNamed(), SHARED["date_numeric"], Clock(), Money(),
                 SHARED["kept_money"], SHARED["percent"], Measure(), SHARED["fraction"], SHARED["range"],
                 SHARED["decimal"], Cardinal()),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER, Form.ORDINAL: SPELLER},
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    attach=attach,
    join_range=join_range,
    options={
        "date_order": frozenset({"DMY", "MDY"}),
        "clock": frozenset({"12h"}),
        "decimal_mark": frozenset({".", ","}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "register": frozenset({"formal", "colloquial"}),
    },
    not_applicable=frozenset({"minute_style", "scale", "phone_regions"}),
)
