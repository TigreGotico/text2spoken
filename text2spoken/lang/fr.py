"""French: fr-FR, the default variety, fr-CA and fr-CH. Every other `fr-*` tag reads as fr-FR.

Number words come from CLDR RBNF, by the CLDR locale of the tag, so `fr-BE` and `fr-CH` say "septante" and
"nonante", `fr-CH` says "huitante" (CLDR lists it for Switzerland), and every other region says "soixante-dix",
"quatre-vingts" and "quatre-vingt-dix". The file writes the traditional spelling "vingt et un" and "soixante et
onze" where CLDR hyphenates, and it builds the ordinals from the cardinals, because the CLDR ordinal rules give
"quatre-vingt-et-unième" and "cent-et-unième" (Académie française, "Les nombres").

Agreement. A number that ends in 1 says "un" or "une" with its noun: "vingt et un kilos", "vingt et une heures".
The gender of a number comes, in this order, from the hint of the caller, from the noun after the number when
it is in the table `feminine_nouns`, from `default_gender`, and from the file, which is masculine. A unit and a
currency carry their own gender.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import SHARED, TimeClock, numbers_in, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import DigitSpeller, RbnfSpeller
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import (Token, fold_digits, is_bounded, is_digit, is_letter, is_word_char, next_visible,
                                     one_digit_set)
from text2spoken.params import Form, FrozenMap, GrammaticalGender, freeze

FEMININE, MASCULINE = GrammaticalGender.FEMININE, GrammaticalGender.MASCULINE
SPACES = " \u00a0\u202f"
"""The space, the no-break space and the narrow no-break space: the gaps that French typography puts between a
number and its unit or symbol, and between the groups of a number."""
GROUP = SPACES + "'\u2019"
"""The group marks of a number: the spaces above, and the apostrophe that Switzerland writes, as in `1'000`."""
_SPACE = "[" + SPACES + "]"

MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
          "novembre", "décembre"]
_MONTH = "(" + "|".join(f"[{m[0].upper()}{m[0]}]{m[1:]}" for m in MONTHS) + ")"
_YEAR = "([0-9][0-9][0-9][0-9])"
_DAY = "([0-9][0-9]?)(er)?"

_FEMININE_SINGULAR = (
    "heure", "minute", "seconde", "semaine", "année", "journée", "soirée", "matinée", "nuit", "fois", "personne",
    "page", "ligne", "porte", "chambre", "place", "pièce", "voiture", "maison", "rue", "ville", "chose",
    "question", "réponse", "version", "photo", "image", "tâche", "alarme", "notification", "minuterie", "pomme",
    "bouteille", "tasse", "cuillère", "unité", "feuille", "fenêtre", "lampe", "chaîne", "chanson", "playlist",
    "étape", "table", "famille", "fille", "femme", "dame", "bière", "carte", "touche", "marche",
)
FEMININE_NOUNS = tuple(w for noun in _FEMININE_SINGULAR
                       for w in ((noun,) if noun == "fois" else (noun, noun + "s")))


def _unit(one: str, gender: str = "masculine", other: str | None = None, many: str | None = None) -> dict:
    """A unit: its name for one, for other numbers and after "million", and its gender. The name after a million
    takes "de", or "d'" before a vowel or a mute h: "un million d'euros", "deux millions de kilomètres"."""
    other = other or one + "s"
    de = "d'" if other[0] in "aeiouyéèêàâîôûh" and not other.startswith(("hertz", "huit")) else "de "
    return {"one": one, "other": other, "many": many or de + other, "gender": gender}


UNITS = {
    "kg": _unit("kilogramme"), "g": _unit("gramme"), "mg": _unit("milligramme"), "km": _unit("kilomètre"),
    "m": _unit("mètre"), "cm": _unit("centimètre"), "mm": _unit("millimètre"),
    "km/h": _unit("kilomètre par heure", other="kilomètres par heure", many="de kilomètres par heure"),
    "m/s": _unit("mètre par seconde", other="mètres par seconde", many="de mètres par seconde"),
    "tr/min": _unit("tour par minute", other="tours par minute", many="de tours par minute"),
    "l": _unit("litre"), "L": _unit("litre"), "ml": _unit("millilitre"), "mL": _unit("millilitre"),
    "cl": _unit("centilitre"), "cL": _unit("centilitre"), "dl": _unit("décilitre"), "dL": _unit("décilitre"),
    "m²": _unit("mètre carré", other="mètres carrés", many="de mètres carrés"),
    "km²": _unit("kilomètre carré", other="kilomètres carrés", many="de kilomètres carrés"),
    "m³": _unit("mètre cube", other="mètres cubes", many="de mètres cubes"),
    "ha": _unit("hectare"),
    "h": _unit("heure", "feminine"), "min": _unit("minute", "feminine"), "s": _unit("seconde", "feminine"),
    "°C": _unit("degré Celsius", other="degrés Celsius", many="de degrés Celsius"),
    "°F": _unit("degré Fahrenheit", other="degrés Fahrenheit", many="de degrés Fahrenheit"),
    "°": _unit("degré"),
    "Hz": _unit("hertz", other="hertz"), "kHz": _unit("kilohertz", other="kilohertz"),
    "MHz": _unit("mégahertz", other="mégahertz"), "GHz": _unit("gigahertz", other="gigahertz"),
    "kW": _unit("kilowatt"), "MW": _unit("mégawatt"), "Wh": _unit("wattheure"), "kWh": _unit("kilowattheure"),
    "hPa": _unit("hectopascal"), "kPa": _unit("kilopascal"), "kcal": _unit("kilocalorie", "feminine"),
    "ko": _unit("kilooctet"), "Ko": _unit("kilooctet"), "Mo": _unit("mégaoctet"), "Go": _unit("gigaoctet"),
    "To": _unit("téraoctet"),
}


def _currency(symbols: list[str], one: str, gender: str, minor: str, minor_gender: str = "masculine",
              other: str | None = None, minor_other: str | None = None) -> dict:
    major = _unit(one, gender, other)
    cents = _unit(minor, minor_gender, minor_other)
    return {"symbols": symbols, **major, "minor": cents}


EURO = _currency(["€"], "euro", "masculine", "centime")
DOLLAR = _currency(["$", "US$"], "dollar", "masculine", "cent")
POUND = _currency(["£"], "livre", "feminine", "penny", "masculine", minor_other="pence")
FRANC = _currency(["CHF"], "franc suisse", "masculine", "centime", other="francs suisses")
CANADIAN = _currency(["CA$", "C$"], "dollar canadien", "masculine", "cent", other="dollars canadiens")
CANADIAN["many"] = "de dollars canadiens"
FRANC["many"] = "de francs suisses"
POUND["minor"]["many"] = "de pence"

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".,", "group": GROUP}, {"decimal": ",.", "group": GROUP}]},
    "defaults": {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ",",
                 "scale": "long", "register": "formal"},
    "sign_words": {"-": "moins", "+": "plus"},
    "decimal_word": "virgule",
    "digit_words": ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"],
    "leads": {"#": "numéro", "-": ""},
    "idioms": {"24h/24": "vingt-quatre heures sur vingt-quatre", "24 h/24": "vingt-quatre heures sur vingt-quatre",
               "7j/7": "sept jours sur sept", "7 j/7": "sept jours sur sept", "50/50": "cinquante-cinquante"},
    "range_word": "à",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"}],
    "dimension_marks": ["x", "×"],
    "dimension_word": "par",
    "time_words": ["à", "vers", "dès", "avant", "après", "jusqu'à", "depuis", "pour", "est"],
    "day_periods": {},
    "day_part_words": {"morning": "du matin", "afternoon": "de l'après-midi", "evening": "du soir"},
    "minute_phrases": {"15": "et quart", "30": "et demie", "45": "moins le quart"},
    "months": MONTHS,
    "scales": {},
    "currencies": {"EUR": EURO, "USD": DOLLAR, "GBP": POUND, "CHF": FRANC, "CAD": CANADIAN},
    "percent": {"signs": ["%"], "position": "after", "word": "pour cent"},
    "units": UNITS,
    "symbols": {"%": "percent", "$": "money", "£": "money", "€": "money"},
    "titles": {"M.": "Monsieur", "MM.": "Messieurs", "Mme": "Madame", "Mmes": "Mesdames", "Mlle": "Mademoiselle",
               "Mlles": "Mesdemoiselles", "Dr": "Docteur", "Dr.": "Docteur", "Pr": "Professeur",
               "Pr.": "Professeur", "Mgr": "Monseigneur", "St": "Saint", "St.": "Saint", "Ste": "Sainte",
               "Ste.": "Sainte"},
    "name_particles": ["le", "la", "de", "du", "des", "d'", "l'"],
    "abbreviations": {"etc.": "et cetera", "c.-à-d.": "c'est-à-dire", "p. ex.": "par exemple"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"n°": "numéro", "N°": "numéro", "nº": "numéro", "Nº": "numéro"},
    "ordinal_marks": {
        "masculine": ["er"], "feminine": ["re", "ère", "ere"], "masculine_plural": ["ers"],
        "feminine_plural": ["res", "ères", "eres"], "other": ["e", "ème", "eme"],
        "other_plural": ["es", "èmes", "emes"],
        "second": ["nd", "d"], "second_feminine": ["nde", "de"], "second_plural": ["nds", "ds"],
        "second_feminine_plural": ["ndes", "des"],
    },
    "feminine_nouns": FEMININE_NOUNS,
    "patterns": {
        "date_day_month": _DAY + _SPACE + _MONTH + "(?:" + _SPACE + _YEAR + ")?",
        "date_month_year": _MONTH + _SPACE + _YEAR,
        "clock_hour": "([0-9][0-9]?)" + _SPACE + "?[hH](?:" + _SPACE + "?([0-9][0-9]))?",
    },
})

VARIETIES = (
    Variety("fr-FR"),
    Variety("fr-CA", freeze({
        "currencies": {
            "USD": {"symbols": ["US$"], "one": "dollar américain", "other": "dollars américains",
                    "many": "de dollars américains"},
            "CAD": {**{k: v for k, v in DOLLAR.items() if k != "symbols"}, "symbols": ["$", "CA$", "C$"],
                    "colloquial": {"one": "piastre", "other": "piastres", "many": "de piastres",
                                   "gender": "feminine", "minor": {"one": "cenne", "other": "cennes",
                                                                   "many": "de cennes", "gender": "feminine"}}},
        },
    })),
    Variety("fr-CH", freeze({"currencies": {"CHF": {"symbols": ["CHF", "Fr.", "fr."]}}})),
)


def _clock_edge(text: str, start: int, end: int) -> bool:
    """Whether no digit, and no mark of a number before a digit, continues text[start:end]. A dash does not
    continue it, so `9h-17h` is a range of two times."""
    before = start == 0 or not (is_digit(text[start - 1])
                                or (text[start - 1] in "/:.," and start > 1 and is_digit(text[start - 2])))
    after = end == len(text) or not (is_digit(text[end])
                                     or (text[end] in "/:.," and end + 1 < len(text) and is_digit(text[end + 1])))
    return before and after


SCALE_NOUNS = frozenset({"million", "millions", "milliard", "milliards", "billion", "billions", "billiard", "billiards",
                         "trillion", "trillions"})
"""The nouns that count a scale of a thousand: a number before them takes the plural of "cent" and "vingt"."""
MULTIPLIERS = frozenset({"deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"})


UNIT_STARTS = frozenset({"un", "une", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze",
                         "douze", "treize", "quatorze", "quinze", "seize"})


def _spell(words: str) -> str:
    """The traditional spelling of CLDR's cardinal, with the agreement rules that CLDR misses.

    "vingt et un", not "vingt-et-un". "Cent" and "quatre-vingt" take an "s" before a noun that counts millions, as
    in "deux cents millions" and "quatre-vingts millions", where CLDR gives "deux cent millions" and, for France,
    "quatre-vingt millions". "Quatre-vingt" takes none before "mille", and a hyphen before a unit, as in
    "quatre-vingt-un", where the CLDR rules of Belgium give "quatre-vingts mille" and "quatre-vingt un"
    (Académie française, "Les nombres")."""
    parts = words.replace("-et-", " et ").split(" ")
    out: list[str] = []
    for index, word in enumerate(parts):
        following = parts[index + 1] if index + 1 < len(parts) else ""
        if word == "quatre-vingts" and following == "mille":
            word = "quatre-vingt"
        if following in SCALE_NOUNS and (word == "quatre-vingt" or (
                word == "cent" and index and parts[index - 1] in MULTIPLIERS)):
            word += "s"
        if out and out[-1] == "quatre-vingt" and word.split("-")[0] in UNIT_STARTS:
            out[-1] += "-" + word
        else:
            out.append(word)
    return " ".join(out)


class FrenchSpeller:
    """RBNF cardinals with the masculine and the feminine rule sets, ordinals built from the cardinals, and decimals
    that read the digits after the comma as one number when there are one or two of them."""

    def __init__(self):
        cardinal = {Features(): "spellout-cardinal-masculine",
                    Features(gender=FEMININE): "spellout-cardinal-feminine"}
        self.rbnf = RbnfSpeller(cardinal=cardinal, ordinal={Features(): "spellout-ordinal-masculine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return _spell(self.rbnf.cardinal(digits, features, request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """The ordinal of a cardinal: "premier", "deuxième", "vingt et unième", "quatre-vingt-unième", "centième",
        "millionième". A last word that ends in "e" loses it, "cinq" takes "u" and "neuf" turns to "neuv"."""
        words = self.cardinal(digits, Features(), request)
        if words in ("un million", "un milliard"):
            words = words[3:]
        if words == "un":
            return "première" if features.gender is GrammaticalGender.FEMININE else "premier"
        head, _, last = words.rpartition(" ")
        prefix, _, last = last.rpartition("-")
        last = last or prefix
        if prefix and last == prefix:
            prefix = ""
        for plural in ("cents", "vingts", "millions", "milliards"):
            if last == plural:
                last = last[:-1]
        if last == "cinq":
            last = "cinqu"
        elif last == "neuf":
            last = "neuv"
        elif last.endswith("e"):
            last = last[:-1]
        ordinal = f"{prefix}-{last}ième" if prefix else f"{last}ième"
        return f"{head} {ordinal}" if head else ordinal

    def year(self, digits: str, features: Features, request: Request) -> str:
        """A year reads as a cardinal, and "cent" stays singular at its end: "mille neuf cent"."""
        words = self.cardinal(digits, Features(), request)
        return words[:-1] if words.endswith("cents") else words

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """"trois virgule cinq", "trois virgule quatorze", "trois virgule zéro cinq". A fraction of three digits or
        more reads digit by digit, as in "trois virgule un quatre un"."""
        whole = self.cardinal(integer or "0", Features(), request)
        if len(fraction) <= 2:
            rest = fraction.lstrip("0")
            zeros = ["zéro"] * (len(fraction) - len(rest))
            tail = " ".join([*zeros, *([self.cardinal(rest, Features(), request)] if rest else [])])
        else:
            tail = DigitSpeller(request.data["digit_words"]).cardinal(fraction, Features(), request)
        return f"{whole} {request.data['decimal_word']} {tail}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """"un demi", "deux tiers", "trois quarts", "cinq huitièmes", "un centième"."""
        top = self.cardinal(numerator, Features(), request)
        plural = numerator.lstrip("0") != "1"
        names = {"2": ("demi", "demis"), "3": ("tiers", "tiers"), "4": ("quart", "quarts")}.get(
            denominator.lstrip("0"))
        if names is not None:
            return f"{top} {names[plural]}"
        return f"{top} {self.ordinal(denominator, Features(), request)}{'s' if plural else ''}"


SPELLER = FrenchSpeller()


@lru_cache(maxsize=8)
def _feminine(nouns: tuple[str, ...]) -> frozenset[str]:
    return frozenset(nouns)


def _gender(context: SpanContext, noun: bool = True) -> GrammaticalGender:
    """The agreement order: the hint, the noun after the number, `default_gender`, then the file."""
    if context.hint is not None and context.hint.gender is not None:
        return context.hint.gender
    if noun and context.after and context.after[0].lower() in _feminine(context.request.data["feminine_nouns"]):
        return FEMININE
    return context.request.params.default_gender.get(LANGUAGE.code) or MASCULINE


def _cardinal(digits: str, request: Request, gender: GrammaticalGender | None = None) -> str:
    return SPELLER.cardinal(digits, Features(gender=gender), request)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _amount(amount: FrozenMap, request: Request, gender: GrammaticalGender | None = None) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    else:
        words = _cardinal(amount["integer"], request, gender)
    return _signed(words, amount["sign"], request)


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


def _name(record: FrozenMap, request: Request, written: str) -> str:
    """The unit or currency name for a written number: one for 0 and 1, "de ..." for a million."""
    return record.get(plural_category(request, written), record["other"])


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal with the gender of the agreement order. Digits with a leading zero, which only a lead admits,
    read one by one."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)
    else:
        words = _cardinal(digits, request, _gender(context))
    if fields["sign"]:
        words = f"{request.data['sign_words'][fields['sign']]} {words}"
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields = span.fields
    return _signed(SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request),
                   fields["sign"], context.request)


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    gender = _gender(context)
    return (f"{_cardinal(span.fields['low'], request, gender)} {request.data['range_word']} "
            f"{_cardinal(span.fields['high'], request, gender)}")


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """"1er" is "premier", "1re" and "1ère" "première", "2e" "deuxième", "2es" "deuxièmes", "2nd" "second"."""
    marker, digits = span.fields["marker"], span.fields["digits"]
    marks = context.request.data["ordinal_marks"]
    kind = next(key for key, spellings in marks.items() if marker in spellings)
    plural = kind.endswith("plural")
    if kind.startswith("second"):
        return "second" + ("e" if "feminine" in kind else "") + ("s" if plural else "")
    words = SPELLER.ordinal(digits, Features(gender=FEMININE if kind.startswith("feminine") else MASCULINE),
                            context.request)
    return words + ("s" if plural else "")


def speak_date(span: Span, context: SpanContext) -> str:
    """"10 novembre 2026" and "10/11/2026" read "dix novembre deux mille vingt-six", and the first of a month
    reads "premier"."""
    request, fields = context.request, span.fields
    month = request.data["months"][fields["month"] - 1]
    words = []
    if fields["day"] is not None:
        words.append("premier" if fields["day"] == 1 else _cardinal(str(fields["day"]), request))
    words.append(month)
    if fields["year"] is not None:
        words.append(SPELLER.year(str(fields["year"]), Features(), request))
    return " ".join(words)


def _hour_words(hour: int, request: Request) -> str:
    return f"{_cardinal(str(hour), request, FEMININE)} {'heure' if hour < 2 else 'heures'}"


def _day_part(hour: int, request: Request) -> str:
    parts = request.data["day_part_words"]
    return parts["morning"] if hour < 12 else parts["afternoon"] if hour < 18 else parts["evening"]


def speak_time(span: Span, context: SpanContext) -> str:
    """"14 h 30" is "quatorze heures trente", and "7 h 05" "sept heures cinq". Hour 12 reads "midi" and hour 0 or 24
    reads "minuit" when a time word comes before it, as in `à 12 h`, on the 12-hour clock and in the phrase style,
    so `12 h` stays "douze heures" after "pendant". The phrase style, which `register="colloquial"` also
    selects, says "et quart", "et demie" and "moins le quart". The 12-hour clock adds "du matin", "de
    l'après-midi" or "du soir" (Académie française, "L'heure")."""
    request, params, fields = context.request, context.request.params, span.fields
    hour, minute, second = fields["hour"], fields["minute"], fields["second"]
    twelve = params.clock == "12h"
    phrase = params.minute_style == "phrase" or params.register == "colloquial"
    quarter = phrase and second is None and minute in (15, 30, 45)
    cue = bool(context.before) and context.before[-1].lower() in request.data["time_words"]
    named_ok = cue or twelve or quarter

    def noon_or_midnight(h: int) -> str | None:
        if named_ok and h == 12:
            return "midi"
        return "minuit" if named_ok and h in (0, 24) else None

    def face(h: int) -> str:
        return noon_or_midnight(h) or _hour_words(twelve_hour(h % 24) if twelve else h, request)

    if quarter:
        later = hour + 1 if minute == 45 else hour
        named = noon_or_midnight(later) is not None
        words = face(later) + " " + (" ".join(request.data["minute_phrases"][str(minute)].split()))
        if minute == 30 and named:
            words = face(later) + " et demi"
    else:
        words = face(hour)
        named = noon_or_midnight(hour) is not None
        if second is not None:
            unit = "minute" if minute < 2 else "minutes"
            words += f" {_cardinal(str(minute), request, FEMININE)} {unit}"
        elif minute:
            words += " " + _cardinal(str(minute), request, FEMININE)
    if second is not None:
        words += f" et {_cardinal(str(second), request, FEMININE)} {'seconde' if second < 2 else 'secondes'}"
    if twelve and not named:
        words += " " + _day_part(hour, request)
    return words


def speak_money(span: Span, context: SpanContext) -> str:
    """"3,50 €" is "trois euros cinquante", "0,50 €" "cinquante centimes", "0,01 €" "un centime", "12,5 €"
    "douze euros cinquante" and "1 000 000 €" "un million d'euros". A currency with a `colloquial` entry says
    "piastres" in the colloquial register."""
    request, fields = context.request, span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = request.data["currencies"][fields["currency"]]
    if request.params.register == "colloquial" and "colloquial" in currency:
        currency = currency["colloquial"]
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if len(fraction) == 1:
        fraction += "0"

    def gender(record: FrozenMap) -> GrammaticalGender:
        return GrammaticalGender(record["gender"])

    if len(fraction) == 2:
        minor_digits = str(int(fraction))
        major = f"{_cardinal(integer, request, gender(currency))} {_name(currency, request, integer)}"
        minor_record = currency["minor"]
        minor = _cardinal(minor_digits, request, gender(minor_record))
        if int(fraction) == 0:
            words = major
        elif int(integer) == 0:
            words = f"{minor} {_name(minor_record, request, minor_digits)}"
        else:
            words = f"{major} {minor}"
    else:
        words = f"{_amount(amount, request, gender(currency))} {_name(currency, request, _written(amount))}"
    return _signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]]
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    joined = f" {link} ".join(_amount(a, request, GrammaticalGender(unit["gender"])) for a in amounts)
    return f"{joined} {_name(unit, request, _written(amounts[-1]))}"


def speak_percent(span: Span, context: SpanContext) -> str:
    request = context.request
    return f"{_amount(span.fields['amount'], request)} {request.data['percent']['word']}"


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    data = context.request.data
    key = span.fields["key"]
    for table in ("titles", "abbreviations", "number_abbreviations"):
        if data[table].get(key) is not None:
            return data[table][key]
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


def speak_idiom(span: Span, context: SpanContext) -> str:
    return context.request.data["idioms"][span.fields["key"]]


@dataclass(frozen=True)
class FrenchTime(TimeClock):
    """`14h30`, `14 h 30`, `14 h 30`, `21 h`, `7h` and `14:30`.

    The `clock_marks` table gives the colon form, which needs a time word before it, as in `à 14:30`, as in the
    shared recognizer. The letter `h` is evidence enough: `21 h` is "vingt et une heures" as a time and as a
    duration. A time that cannot be one, such as `25 h 99`, `12 h 60` or `24 h 30`, stays as written with a
    warning. An hour above 24 with no minutes, as in `100 h`, is a duration for the measure reader, and so is an
    hour and minutes that `min` or `s` follows, as in `1 h 30 min`."""

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        yield from super()._times(text, tokens, request)
        pattern = re.compile(request.data["patterns"]["clock_hour"])
        folded = fold_digits(text)
        for match in pattern.finditer(folded):
            start, end = match.span()
            if (not _clock_edge(text, start, end) or (start and text[start - 1].isalnum())
                    or not one_digit_set(text[start:end]) or (end < len(text) and text[end].isalnum())):
                continue
            hour = int(match.group(1))
            minute = None if match.group(2) is None else int(match.group(2))
            rest = text[end:].lstrip(SPACES)
            if next((w for w in ("min", "s") if rest.startswith(w) and is_bounded(rest, 0, len(w))), None):
                continue
            valid = hour <= 24 and (minute is None or (minute <= 59 and (hour < 24 or minute == 0)))
            if not valid and minute is None:
                continue
            yield Span(start, end, Form.TIME,
                       FrozenMap({"hour": hour, "minute": minute or 0, "second": None, "period": None,
                                  "suffix": ""}), recognizer=self.name, keep=not valid)


@dataclass(frozen=True)
class Ordinal:
    """`1er`, `1re`, `1ère`, `2e`, `3ème`, `21e`, `4es`, `2nd`, `2nde`: a whole number that a marker follows with no
    space. `er`, `re` and `ère` mark 1 only, `nd` and `nde` mark 2 only, and `e` and `ème` mark any other number."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        spellings = sorted(((m, kind) for kind, ms in marks.items() for m in ms), key=lambda p: len(p[0]), reverse=True)
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None:
                continue
            value = number.integer.lstrip("0")
            for marker, kind in spellings:
                end = number.end + len(marker)
                if not text.startswith(marker, number.end) or not is_bounded(text, number.start, end):
                    continue
                first = kind.startswith(("masculine", "feminine"))
                second = kind.startswith("second")
                plain = not (first or second)
                if (first and value != "1") or (second and value != "2") or (plain and value in ("", "1")):
                    continue
                yield Span(number.start, end, Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)
                break


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, a saint before a capitalised name or after a hyphen, `n°` before a number,
    and the abbreviations of the table. A title that an initial follows, as in `M. J. Dupont`, stays as written."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        final = frozenset(data["sentence_final"])
        particles = tuple(data["name_particles"])
        for table in ("titles", "number_abbreviations", "abbreviations"):
            for key in sorted((k for k, v in data[table].items() if v is not None), key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    trail = ""
                    if position and is_word_char(text[position - 1]):
                        ok = False
                    elif table == "titles":
                        ok = self._name_follows(text, end, particles)
                    elif table == "number_abbreviations":
                        ok = following.isdigit()
                        trail = " " if text[end:end + 1].isdigit() else ""
                    else:
                        ok = is_bounded(text, position, end)
                        if key in final and (following in ("", ".") or following.isupper()):
                            trail = "."
                    if ok:
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}), trail=trail,
                                   recognizer=self.name)
                    position = text.find(key, end)

    @staticmethod
    def _name_follows(text: str, end: int, particles: tuple[str, ...]) -> bool:
        """Whether a capitalised word, or a particle and more text, or a hyphen and a capital, follows text[:end]."""
        if end < len(text) and is_letter(text[end]):
            return False
        if text.startswith("-", end) and text[end + 1:end + 2].isupper():
            return True
        index = end
        while index < len(text) and text[index] in SPACES:
            index += 1
        if index >= len(text):
            return False
        stop = index
        while stop < len(text) and (is_letter(text[stop]) or text[stop] == "'"):
            stop += 1
        word = text[index:stop]
        elided = word[:word.find("'") + 1] if "'" in word else word
        if word.lower() in particles or elided.lower() in particles:
            return stop < len(text)
        return text[index].isupper() and not (len(word) == 1 and text.startswith(".", stop))


@dataclass(frozen=True)
class DateNamed:
    """`10 novembre 2026`, `1er novembre`, `10 novembre`, `novembre 2026`: a date with a month name."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        patterns, symbols = request.data["patterns"], request.data["symbols"]
        folded = fold_digits(text)
        for key in ("date_day_month", "date_month_year"):
            for match in re.finditer(patterns[key], folded):
                start, end = match.span()
                if (not is_bounded(text, start, end) or (start and text[start - 1] in symbols)
                        or not one_digit_set(text[start:end])):
                    continue
                if key == "date_day_month":
                    day, ordinal, month_name, year = match.groups()
                    if ordinal and day != "1":
                        continue
                else:
                    day, month_name, year = None, match.group(1), match.group(2)
                month = [m.lower() for m in request.data["months"]].index(month_name.lower()) + 1
                year_value = int(year) if year is not None else None
                if day is not None and not is_valid(year_value, month, int(day)):
                    continue
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": year_value, "month": month, "day": int(day) if day else None,
                                      "written_order": "DMY", "month_written": "name", "prefix": "",
                                      "suffix": ""}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="fr",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["idiom"], DateNamed(), SHARED["date_numeric"], FrenchTime(),
                 SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["fraction"], SHARED["range"],
                 Ordinal(), Abbreviation(), SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.IDIOM: speak_idiom, Form.DATE: speak_date, Form.TIME: speak_time,
        Form.MONEY: speak_money, Form.PERCENT: speak_percent, Form.MEASURE: speak_measure,
        Form.FRACTION: speak_fraction, Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal,
        Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER,
              Form.YEAR: SPELLER},
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY"}),
        "clock": frozenset({"24h", "12h"}),
        "minute_style": frozenset({"number", "phrase"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long"}),
        "register": frozenset({"formal", "colloquial"}),
        "default_gender": frozenset({"masculine", "feminine"}),
    },
    not_applicable=frozenset({"phone_regions"}),
)
