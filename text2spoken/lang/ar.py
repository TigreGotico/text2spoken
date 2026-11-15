"""Modern Standard Arabic: `ar`, its CLDR regional varieties, and the Arabic varieties of ISO 639-3.

The output is Modern Standard Arabic in Arabic script with no diacritics; a diacritizer runs after normalisation.
`SERVES` holds the active members of the ISO 639-3 macrolanguage `ara` (iso639-3.sil.org, macrolanguage table) that
write Arabic script; the CLDR 49 likely subtags give Latin script to `acy` and `pga`. A regional tag reads the month
names and the number marks of its CLDR 49 locale (`numbers.json`, `ca-gregorian.json`), and no regional words:
`arz-EG` and `ar-EG` read as `ar`. Number words come from ovos-number-parser with the tag `ar`, so a dialect tag
never selects its dialect words.

The rules and their sources:

- Agreement (Ryding 2005, chapter 15). One and two follow the noun that they count (pp. 330-332). From 3 to 10 a
  number takes the gender opposite to its noun (p. 334), and eight before a feminine plural is ثماني (p. 336). From
  11 to 99 the noun follows in the accusative singular (pp. 339-345). A noun that ends in taa' marbuuTa is feminine
  (p. 121), and the plurals in -aat of masculine nouns (Wright 1896, vol. 1, section 303) make the feminine plurals
  a table.
- Case. A number after a preposition (pp. 366-367) or a year noun (pp. 351-353) is genitive, and the colloquial
  register has no case endings (p. 343, note 11). With no diacritics, the genitive and the accusative of a number
  are one written form, the oblique form of ovos-number-parser, and the oblique dual ends in -ayni (p. 332).
- Hundreds, thousands and millions. A dual before its counted noun drops its nuun (p. 347), a thousand or a million
  counted from 11 to 99 with no noun is an accusative tamyiz (pp. 350 and 353), and a scale word makes the million
  the counted noun of an amount (p. 353).
- Ordinals follow the noun that they rank and agree with it (pp. 354-359). A date reads the day as a masculine
  ordinal, then من and the month (pp. 357-358).
- Fractions from 2 to 10 read by name (pp. 360-361). The time reads the hour as a feminine ordinal, and the
  quarters, thirds and halves of the hour, with إلا before the next hour (pp. 361-362). The day period of an hour
  comes from the CLDR 49 day period rules of `ar` (`dayPeriods.json`).
- Percent: the number and في المئة (p. 347). The decimal word is فاصلة (Wiktionary, فاصلة, sense 6), and the word of
  the minus sign is سالب (Arabic Wikipedia, عدد سالب, section التسمية).
- كم before an indefinite noun is the question word "how many" (pp. 402-403), not the kilometre.

The `units` and `currencies` tables give each noun in every count form, with the nominative and the oblique dual.
CLDR 49 does not: `units.json` writes the dual of length-kilometer as "{0} كيلومتر", and `currencies.json` gives
USD and SAR one name with no count forms. The count forms of دولار and ريال come from Wiktionary.

Ryding 2005 is Karin C. Ryding, *A Reference Grammar of Modern Standard Arabic*, Cambridge University Press. Wright
1896 is W. Wright, *A Grammar of the Arabic Language*, 3rd edition, volume 1.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import SHARED, Money as CoreMoney, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import OvosNumberSpeller, bounded_integer
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import Token, fold_digits, is_bounded, one_digit_set
from text2spoken.errors import DeclinedReading
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

MASCULINE, FEMININE = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE
NOMINATIVE, OBLIQUE = "nominative", "oblique"

SERVES = ("aao", "abh", "abv", "acm", "acq", "acw", "acx", "adf", "aeb", "aec", "afb", "apd", "arb", "arq",
          "ars", "ary", "arz", "auz", "avl", "ayh", "ayl", "ayn", "ayp", "shu", "ssh")
"""The active members of the ISO 639-3 macrolanguage `ara` that write Arabic script. `acy` and `pga` write Latin
script (CLDR likely subtags), and `ajp` and `bbz` are retired codes. `apc` (Levantine) is left out: a Levantine
voice reads its own number words, and a Standard Arabic reading here would replace them."""

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

SCALE_DUALS = ("مئتان", "مئتين", "ألفان", "ألفين", "مليونان", "مليونين")

DATA = freeze({
    "number_marks": {"Arab": [{"decimal": "٫", "group": "٬"}],
                     "Latn": [{"decimal": ",", "group": "."}, {"decimal": ".", "group": ","}]},
    "defaults": {"date_order": "DMY", "clock": "12h", "decimal_mark": ".", "register": "formal"},
    "proclitics": ["ب", "بـ", "ل", "لـ", "و"],
    "prepositions": ["ب", "بـ", "ل", "لـ", "في", "من", "إلى", "على", "عن", "حتى", "منذ"],
    "year_nouns": {"عام": "masculine", "سنة": "feminine"},
    "feminine_plurals": ["مخطوطات", "قصائد", "مقابلات", "آبار", "مرات", "فرق", "ساعات", "سيارات", "دقائق",
                         "سنوات"],
    "rank_nouns": ["الطابق", "الفئة", "المرتبة", "القرن"],
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
    "percent": {"signs": ["%", "٪"], "position": "after", "word": "في المئة"},
    "currencies": {
        "USD": {"symbols": ["$", "US$"], "gender": "masculine", "one": "دولار", "two": ["دولاران", "دولارين"],
                "few": "دولارات", "many": "دولارا", "other": "دولار"},
        "SAR": {"symbols": ["SAR"], "gender": "masculine", "one": "ريال سعودي",
                "two": ["ريالان سعوديان", "ريالين سعوديين"], "few": "ريالات سعودية", "many": "ريالا سعوديا",
                "other": "ريال سعودي"},
        "SAR-sign": {"symbols": ["ريال", "ر.س"], "gender": "masculine", "one": "ريال", "two": ["ريالان", "ريالين"],
                     "few": "ريالات", "many": "ريالا", "other": "ريال"},
    },
    "symbols_after_only": ["ريال"],
    "scales": {"مليون": "000000"},
    "units": {unit: KILOMETRE for unit in ("كم", "km")},
    "dimension_marks": ["×"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"}],
    "time_words": ["الساعة"],
    "day_periods": {"am": ["صباحًا", "صباحا"], "pm": ["مساءً", "مساء"]},
    "spoken_periods": {"morning1": "في الصباح", "morning2": "صباحا", "afternoon1": "ظهرا",
                       "afternoon2": "بعد الظهر", "evening1": "مساء", "night2": "ليلا"},
    "minute_phrases": {"0": "{hour}", "15": "{hour} والربع", "20": "{hour} والثلث", "30": "{hour} والنصف",
                       "40": "{next_hour} إلا ثلثا", "45": "{next_hour} إلا ربعا",
                       "other": "{hour} والدقيقة {minute}"},
    "months": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر",
               "ديسمبر"],
    "date_reading": {"full": "{day} من {month} {year}", "no_year": "{day} من {month}"},
    "symbols": {"%": "percent", "٪": "percent", "$": "money", "+": "expression", "=": "expression"},
})
"""Sources, by table. `number_marks`, `months`, `day_periods` and `spoken_periods`: CLDR 49 (numbers.json,
ca-gregorian.json, dayPeriods). `percent`: Ryding 2005, p. 347. `prepositions`: Ryding 2005, pp. 366-367.
`year_nouns`: Ryding 2005, pp. 351-353. `feminine_plurals`: the counted plurals of Ryding 2005, pp. 335-336, دقائق of
CLDR (units.json, duration-minute), and سنوات, the plural of the feminine sana (pp. 352-353). `rank_nouns`: nouns
that an ordinal follows (Ryding 2005, pp. 354-359). `currencies`: `SAR` reads the CLDR name ريال سعودي, and the sign
ر.س (English Wikipedia, Saudi riyal, revision 1252604873) and the word ريال read ريال. `fraction_names`: Ryding 2005,
pp. 360-361. `minute_phrases`: Ryding 2005, pp. 361-362. `decimal_word`: Wiktionary, فاصلة, sense "decimal point".
`sign_words`: Arabic Wikipedia, عدد سالب, section التسمية. The count forms of `currencies` and `units`: Wiktionary
دولار and ريال, CLDR units.json (length-kilometer), and the count rules of Ryding 2005, pp. 330-345.
`symbols_after_only`: ريال is a counted noun, which follows the number (Ryding 2005, p. 335)."""

VARIETIES = (
    Variety("ar-001"),
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
"""The CLDR locales whose month names or Latin number marks differ from `ar`. Each other region reads as `ar-001`."""


class ArabicSpeller:
    """ovos-number-parser, always with the tag `ar`, so that a dialect tag such as `arz` reads Modern Standard
    Arabic. A decimal reads the integer, the decimal word and the fraction digits as one number (Wiktionary, فاصلة),
    and a fraction reads its denominator by name, from 2 to 10 (Ryding 2005, pp. 360-361)."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    @staticmethod
    def _msa(request: Request) -> Request:
        return replace(request, tag="ar")

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.cardinal(digits, features, self._msa(request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.ordinal(digits, features, self._msa(request))

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


def counted_noun(context: SpanContext) -> str | None:
    """The indefinite Arabic word right after the number, which the number counts (Ryding 2005, p. 335)."""
    if not context.after:
        return None
    word = context.after[0]
    return word if _is_arabic_word(word) and not word.startswith("ال") else None


def noun_gender(noun: str, data: FrozenMap) -> GrammaticalGender:
    """Feminine for a noun that ends in taa' marbuuTa (Ryding 2005, p. 121) or for a plural of the table: a plural
    in -aat also comes from masculine nouns (Wright 1896, vol. 1, section 303), so no rule reads it."""
    return FEMININE if noun.endswith("ة") or noun in data["feminine_plurals"] else MASCULINE


def _case(span: Span, context: SpanContext) -> str:
    """Oblique after a preposition or a year noun, and everywhere in the colloquial register, which has no case
    endings (Ryding 2005, p. 343, note 11); else nominative."""
    request = context.request
    if context.hint is not None and context.hint.case is not None:
        return context.hint.case
    data = request.data
    before = context.before[-1] if context.before else ""
    if (request.params.register == "colloquial" or span.fields.get("prefix", "") in data["prepositions"]
            or before in data["prepositions"] or before in data["year_nouns"]):
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
        noun = counted_noun(context)
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


def rank_noun(context: SpanContext) -> tuple[str, str] | None:
    """The rank noun right before the number, as in الطابق 3 and بالمرتبة 1, with the proclitic that it carries."""
    if not context.before:
        return None
    word, nouns = context.before[-1], context.request.data["rank_nouns"]
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
               or before in request.data["prepositions"])
    features = Features(gender=hint.gender or noun_gender(noun, request.data),
                        case=hint.case or (OBLIQUE if oblique else NOMINATIVE))
    return SPELLER.ordinal(span.fields["digits"], features, request)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """One and two follow the noun that they count (Ryding 2005, pp. 330-332), so a digit 1 or 2 before a noun stays
    as written."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        raise DeclinedReading("a number with a leading zero has no cited reading")
    rank = rank_noun(context)
    if rank is not None and not (fields["sign"] or fields["lead"]) and 1 <= int(digits) <= 99:
        return speak_rank(span, context, *rank)
    noun = counted_noun(context)
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
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], agreement(span, context), context.request)
    if bounded_integer(fields["numerator"]) == 2 and context.after and _is_arabic_word(context.after[0]):
        words = words[:-1]
    return _signed(words, fields["sign"], context.request)


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
    """A whole number and the noun that it counts, by CLDR plural category: the noun alone for one, the dual for
    two, then the number and the genitive plural (few), the accusative singular (many) or the genitive singular
    (other) (CLDR units.json; Ryding 2005, pp. 330-345 and 348-349)."""
    value = bounded_integer(digits)
    category = plural_category(request, digits)
    if category == "one":
        return forms["one"]
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
    if span.fields["unit"] == "كم" and counted_noun(context) and context.after[0] not in request.data["prepositions"]:
        raise DeclinedReading("كم before an indefinite noun is the question word 'how many' (Ryding 2005, pp. 402-403)")
    forms = request.data["units"][span.fields["unit"]]
    return counted(amount["integer"], forms, agreement(span, context, GrammaticalGender(forms["gender"])), request)


def speak_date(span: Span, context: SpanContext) -> str:
    """The day is a masculine ordinal, then من and the month (Ryding 2005, pp. 357-358), and the year is genitive,
    as after the year noun that may stand before it (pp. 351-353)."""
    request = context.request
    fields = span.fields
    month = request.data["months"][fields["month"] - 1]
    day = SPELLER.ordinal(str(fields["day"]), Features(gender=MASCULINE, case=_case(span, context)), request)
    if fields["year"] is None:
        return request.data["date_reading"]["no_year"].format(day=day, month=month)
    year = SPELLER.year(str(fields["year"]), Features(gender=MASCULINE, case=OBLIQUE), request)
    return request.data["date_reading"]["full"].format(day=day, month=month, year=year)


def _day_period(hour: int, request: Request) -> str:
    for period, first, end in DAY_PERIOD_HOURS:
        if first <= hour < end:
            return request.data["spoken_periods"][period]
    raise DeclinedReading("no cited name for the day period from midnight to one")


def _hour(face: int, request: Request) -> str:
    """The hour is a feminine ordinal that agrees with saa'a (Ryding 2005, p. 361). For one o'clock the sources
    here give no form, so it declines."""
    if face == 1:
        raise DeclinedReading("no cited form for one o'clock")
    return SPELLER.ordinal(str(face), Features(gender=FEMININE), request)


def speak_time(span: Span, context: SpanContext) -> str:
    """Quarters, thirds and halves of the hour, with إلا before the next hour for 40 and 45 minutes, and other
    minutes as a feminine ordinal after والدقيقة (Ryding 2005, pp. 361-362). A written day period, or an hour
    from 13 to 23, reads the CLDR day period of the hour."""
    request = context.request
    fields = span.fields
    hour, minute = fields["hour"], fields["minute"]
    if fields["second"] is not None:
        raise DeclinedReading("no cited reading for seconds")
    if fields["period"] == "pm" and hour < 12:
        hour += 12
    elif fields["period"] == "am" and hour == 12:
        hour = 0
    phrases = request.data["minute_phrases"]
    template = phrases.get(str(minute), phrases["other"])
    next_hour = _hour(twelve_hour(hour + 1), request) if "{next_hour}" in template else ""
    words = template.format(hour=_hour(twelve_hour(hour), request) if "{hour}" in template else "",
                            next_hour=next_hour,
                            minute=SPELLER.ordinal(str(minute), Features(gender=FEMININE), request)
                            if "{minute}" in template else "")
    if hour == 0 or fields["period"] is not None or hour >= 13:
        words += " " + _day_period(hour, request)
    return words


@dataclass(frozen=True)
class Money(CoreMoney):
    """The money of the core. The word ريال is a counted noun, which follows the number (Ryding 2005, p. 335), so
    `ريال 5` stays as written. The reading of an amount ends in ريال, so a digit after it would read on a second
    pass."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        after_only = request.data["symbols_after_only"]
        for span in super().find(text, tokens, request):
            symbol = span.fields["written_symbol"]
            written = text[span.start:span.end]
            first_digit = next(index for index, char in enumerate(written) if char.isdigit())
            yield replace(span, keep=True) if symbol in after_only and symbol in written[:first_digit] else span


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
                                  "month_written": "name", "prefix": "", "suffix": ""}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="ar",
    serves=SERVES,
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], DateNamed(), SHARED["date_numeric"], SHARED["time_clock"], Money(),
                 SHARED["percent"], SHARED["measure"], SHARED["fraction"], SHARED["range"], SHARED["decimal"],
                 SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    attach=attach,
    options={
        "date_order": frozenset({"DMY", "MDY"}),
        "clock": frozenset({"12h"}),
        "decimal_mark": frozenset({".", ","}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "register": frozenset({"formal", "colloquial"}),
    },
    not_applicable=frozenset({"minute_style", "scale", "phone_regions"}),
)
