"""German: de-DE, the default variety, de-AT and de-CH.

Number words come from CLDR RBNF. The cardinal rule sets of `de` carry the endings of the indefinite article,
so `1` reads "ein", "eine", "einen", "einem", "einer" or "eines" by the gender of the counted noun and the case
that a preposition before it governs, and "eins" when no noun follows. The ordinal rule sets carry the adjective
endings -e, -en, -er, -es and -em. The design page `text2spoken-design.md`, section 5.4, gives the measured
reason for each speller.

The amtliche Regelwerk of the Rat für deutsche Rechtschreibung (2018 edition) is the rule source. Its § 25 E2
lets Switzerland always write ss for ß, so de-CH reads RBNF `de_CH`, which writes "dreissig", and its tables write
ss. CLDR gives the Austrian month name "Jänner" and the Swiss number marks.

`Expression` and `Abbreviation` come from `en.py`. They read only the data tables of the language.
"""
from __future__ import annotations

import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import PHONE_PLANS, SHARED, Telephone, join_ranges, numbers_in, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext, Word, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import DigitSpeller, RbnfSpeller, bounded_integer
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import Token, fold_digits, is_bounded, next_visible, one_digit_set
from text2spoken.errors import DeclinedReading
from text2spoken.lang.en import Abbreviation, Expression
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

M, F, N = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE, GrammaticalGender.NEUTER

MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember"]
"""CLDR `de`, ca-gregorian, months, format, wide."""
MONTHS_AT = ["Jänner", *MONTHS[1:]]
"""CLDR `de-AT`, ca-gregorian, months, format, wide."""
_MONTH = "(" + "|".join(dict.fromkeys(MONTHS + MONTHS_AT)) + ")"
_SIGNS = "-−+"

UNITS = {
    "kg": {"one": "Kilogramm", "other": "Kilogramm", "gender": "neuter"},
    "g": {"one": "Gramm", "other": "Gramm", "gender": "neuter"},
    "mg": {"one": "Milligramm", "other": "Milligramm", "gender": "neuter"},
    "km": {"one": "Kilometer", "other": "Kilometer", "gender": "masculine"},
    "m": {"one": "Meter", "other": "Meter", "gender": "masculine"},
    "cm": {"one": "Zentimeter", "other": "Zentimeter", "gender": "masculine"},
    "mm": {"one": "Millimeter", "other": "Millimeter", "gender": "masculine"},
    "km/h": {"one": "Kilometer pro Stunde", "other": "Kilometer pro Stunde", "gender": "masculine"},
    "m/s": {"one": "Meter pro Sekunde", "other": "Meter pro Sekunde", "gender": "masculine"},
    "l": {"one": "Liter", "other": "Liter", "gender": "masculine"},
    "ml": {"one": "Milliliter", "other": "Milliliter", "gender": "masculine"},
    "°C": {"one": "Grad Celsius", "other": "Grad Celsius", "gender": "neuter"},
    "°F": {"one": "Grad Fahrenheit", "other": "Grad Fahrenheit", "gender": "neuter"},
    "MB": {"one": "Megabyte", "other": "Megabyte", "gender": "neuter"},
}
"""Regelwerk § 102 (1.1): `km/h (= Kilometer pro Stunde)`. Duden, "Grad": "20 Grad Celsius (20 °C)", and the noun
stays unchanged after a number."""

DATA = freeze({
    # The default of `decimal_mark` in "defaults" selects the entry, so a dropped default reads the first one.
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}, {"decimal": ",", "group": "."}]},
    "defaults": {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ",",
                 "scale": "long"},
    "sign_words": {"-": "minus", "+": "plus"},
    "decimal_word": "Komma",
    "digit_words": ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun"],
    "leads": {"#": "Nummer", "-": ""},
    "half": "halb",
    "idioms": {"24/7": "vierundzwanzig sieben"},
    "range_word": "bis",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"},
                    {"mark": ".", "seconds": False, "needs": "evidence"}],
    "time_suffixes": [" Uhr", " Uhr"],
    "hour_word": "Uhr",
    "time_words": ["um", "gegen"],
    "dimension_marks": ["x", "×"],
    "dimension_word": "mal",
    "operators": {"+": "plus", "−": "minus", "×": "mal", "÷": "geteilt durch", "=": "gleich"},
    "months": MONTHS,
    "month_numbers": {name: index % 12 + 1 for index, name in enumerate(MONTHS + MONTHS_AT)},
    "year_words": ["Jahr", "Jahre", "Jahres", "anno", "Anno"],
    "currencies": {
        "EUR": {"symbols": ["€", "EUR"], "one": "Euro", "other": "Euro", "gender": "masculine",
                "minor": {"one": "Cent", "other": "Cent"}},
        "USD": {"symbols": ["$", "US$", "USD"], "one": "Dollar", "other": "Dollar", "gender": "masculine",
                "minor": {"one": "Cent", "other": "Cent"}},
        "GBP": {"symbols": ["£", "GBP"], "one": "Pfund", "other": "Pfund", "gender": "neuter",
                "minor": {"one": "Penny", "other": "Pence"}},
        "CHF": {"symbols": ["CHF"], "one": "Franken", "other": "Franken", "gender": "masculine",
                "minor": {"one": "Rappen", "other": "Rappen"}},
    },
    "scales": {"Mio.": "Million", "Mrd.": "Milliarde"},
    "scale_plurals": {"Million": "Millionen", "Milliarde": "Milliarden"},
    "percent": {"signs": ["%"], "position": "after", "word": "Prozent", "gender": "neuter"},
    "units": UNITS,
    "phone_words": ["tel", "telefon", "telefonnummer", "rufnummer", "handy", "mobil", "fax", "notruf"],
    "short_codes": ["110", "112", "117", "118", "122", "133", "144"],
    "list_links": ["und", "oder"],
    "phone_shapes": ["0[1-9][0-9]{1,4} [0-9]+-[0-9]+"],
    "phone_unit_shapes": ["(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "color_words": ["Farbe", "Farben", "Farbcode"],
    "titles": {"Dr.": "Doktor", "Prof.": "Professor", "Hr.": "Herr", "Hrn.": "Herrn", "Fr.": "Frau"},
    "abbreviations": {"z. B.": "zum Beispiel", "d. h.": "das heißt", "usw.": "und so weiter",
                      "bzw.": "beziehungsweise", "u. a.": "unter anderem", "Jh.": "Jahrhundert", "Tel.": "Telefon",
                      "Bd.": "Band", "Jg.": "Jahrgang", "ca.": "circa", "etc.": "et cetera"},
    "sentence_final": ["usw.", "etc."],
    "number_abbreviations": {"Nr.": "Nummer"},
    "symbols": {"%": "percent", "$": "money", "£": "money", "€": "money", "°": "measure", "×": "measure"},
    "dative_prepositions": ["aus", "bei", "mit", "nach", "seit", "von", "zu", "gegenüber", "außer"],
    "accusative_prepositions": ["durch", "für", "gegen", "ohne", "um"],
    "genitive_prepositions": ["wegen", "während", "trotz", "statt", "anstatt", "innerhalb", "außerhalb"],
    "two_way_prepositions": ["in", "an", "auf", "über", "unter", "vor", "hinter", "neben", "zwischen"],
    "temporal_prepositions": ["in", "an", "vor"],
    "time_nouns": ["sekunde", "minute", "stunde", "tag", "woche", "monat", "jahr", "jahrzehnt", "jahrhundert",
                   "nacht", "moment", "augenblick"],
    "accusative_verbs": ["kostet", "kosten", "kostete", "kosteten"],
    "determiners": {
        "der": {"definite": True, "case": "nominative", "gender": "masculine"},
        "die": {"definite": True, "case": "nominative", "gender": "feminine"},
        "das": {"definite": True, "case": "nominative", "gender": "neuter"},
        "den": {"definite": True, "case": "accusative", "gender": "masculine"},
        "dem": {"definite": True, "case": "dative"},
        "des": {"definite": True, "case": "genitive"},
        "am": {"definite": True, "case": "dative"},
        "im": {"definite": True, "case": "dative"},
        "vom": {"definite": True, "case": "dative"},
        "zum": {"definite": True, "case": "dative"},
        "beim": {"definite": True, "case": "dative"},
        "zur": {"definite": True, "case": "dative", "gender": "feminine"},
        "ins": {"definite": True, "case": "accusative", "gender": "neuter"},
        "ein": {"definite": False, "case": "nominative"},
        "eine": {"definite": False, "case": "nominative", "gender": "feminine"},
        "einen": {"definite": False, "case": "accusative", "gender": "masculine"},
        "einem": {"definite": False, "case": "dative"},
        "einer": {"definite": False, "case": "dative", "gender": "feminine"},
        "eines": {"definite": False, "case": "genitive"},
    },
    # en.wikipedia, "Grammatical gender in German": 90% of nouns in -e are feminine, with the exceptions that it names
    # and that the whole-word table holds, and 90% of nouns with the prefix Ge- are neuter. A frame is the prefix
    # Ge-, a consonant and a vowel before the final -e, so "Geste" and "Geige" have no prefix. de.wiktionary gives
    # "der Kaffee" and "der Tee", which end their compounds.
    "noun_genders": {"ei": "neuter",
                     **dict.fromkeys(("auge", "ende", "erbe", "finale", "image", "interesse", "prestige", "regime"),
                                     "neuter"),
                     **dict.fromkeys(("charme", "käse", "buchstabe", "friede", "funke", "gedanke", "glaube", "haufe",
                                      "name", "same", "wille", "affe", "bote", "hase", "junge", "löwe", "gehilfe"),
                                     "masculine"),
                     **dict.fromkeys(("gebärde", "gemeinde", "geschichte"), "feminine")},
    "noun_frames": [["ge[^aeiouäöüy]+[aeiouäöüy].*e", "neuter"]],
    "noun_endings": [["ung", "feminine"], ["heit", "feminine"], ["keit", "feminine"], ["schaft", "feminine"],
                     ["ion", "feminine"], ["tät", "feminine"], ["ei", "feminine"], ["e", "feminine"], ["kaffee", "masculine"],
                     ["erin", "feminine"], ["frau", "feminine"], ["nacht", "feminine"], ["zeit", "feminine"],
                     ["person", "feminine"],
                     ["chen", "neuter"], ["lein", "neuter"], ["kind", "neuter"], ["jahr", "neuter"],
                     ["haus", "neuter"], ["mal", "neuter"], ["buch", "neuter"], ["prozent", "neuter"],
                     ["ling", "masculine"], ["ismus", "masculine"], ["tag", "masculine"], ["monat", "masculine"],
                     ["mann", "masculine"], ["platz", "masculine"], ["versuch", "masculine"],
                     ["euro", "masculine"], ["tee", "masculine"]],
})

_SS = str.maketrans({"ß": "ss"})


def _swiss(value):
    """The value with ss for each ß, at every depth (Regelwerk § 25 E2)."""
    if isinstance(value, str):
        return value.translate(_SS)
    if isinstance(value, FrozenMap):
        return FrozenMap({key: _swiss(item) for key, item in value.items()})
    if isinstance(value, tuple):
        return tuple(_swiss(item) for item in value)
    return value


VARIETIES = (
    Variety("de-DE"),
    Variety("de-AT", freeze({"months": MONTHS_AT})),
    Variety("de-CH", freeze({
        "number_marks": {"Latn": [{"decimal": ".", "group": "'"}, {"decimal": ",", "group": "'"}]},
        "defaults": {"decimal_mark": "."},
        "currencies": {"CHF": {"symbols": ["CHF", "Fr."]}},
        **{key: _swiss(DATA[key]) for key in ("abbreviations", "dative_prepositions", "genitive_prepositions")},
    })),
)

_ORDINAL_SETS = {"e": "spellout-ordinal", "en": "spellout-ordinal-n", "er": "spellout-ordinal-r",
                 "es": "spellout-ordinal-s", "em": "spellout-ordinal-m"}

_ENDINGS = {
    # (definite, case): ending by gender; definite True is weak, False mixed, None strong (no article).
    (True, "nominative"): {M: "e", F: "e", N: "e"},
    (True, "accusative"): {M: "en", F: "e", N: "e"},
    (True, "dative"): {M: "en", F: "en", N: "en"},
    (True, "genitive"): {M: "en", F: "en", N: "en"},
    (False, "nominative"): {M: "er", F: "e", N: "es"},
    (False, "accusative"): {M: "en", F: "e", N: "es"},
    (False, "dative"): {M: "en", F: "en", N: "en"},
    (False, "genitive"): {M: "en", F: "en", N: "en"},
    (None, "nominative"): {M: "er", F: "e", N: "es"},
    (None, "accusative"): {M: "en", F: "e", N: "es"},
    (None, "dative"): {M: "em", F: "er", N: "em"},
    (None, "genitive"): {M: "en", F: "er", N: "en"},
}
"""The adjective endings of an ordinal after a definite article (weak), after "ein" (mixed) and with no article
(strong), by case and gender."""


class GermanSpeller:
    """RBNF integers: the counting form "eins" with no features, the article endings by gender and case, and the
    adjective endings of an ordinal; decimals read digit by digit after "Komma"."""

    def __init__(self):
        cardinal = {Features(): "spellout-numbering"}
        for gender, nominative, dative, genitive, accusative in (
                (M, "spellout-cardinal-masculine", "spellout-cardinal-m", "spellout-cardinal-s",
                 "spellout-cardinal-n"),
                (F, "spellout-cardinal-feminine", "spellout-cardinal-r", "spellout-cardinal-r",
                 "spellout-cardinal-feminine"),
                (N, "spellout-cardinal-neuter", "spellout-cardinal-m", "spellout-cardinal-s",
                 "spellout-cardinal-neuter")):
            cardinal[Features(gender=gender)] = nominative
            for case, name in (("nominative", nominative), ("accusative", accusative), ("dative", dative),
                               ("genitive", genitive)):
                cardinal[Features(gender=gender, case=case)] = name
        self.rbnf = RbnfSpeller(cardinal=cardinal, ordinal={Features(): "spellout-ordinal"})
        self.ordinal_sets = {ending: RbnfSpeller(cardinal={Features(): name}, ordinal={Features(): name})
                             for ending, name in _ORDINAL_SETS.items()}

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf.cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """The ending follows `features.definite`: True after a definite article, False after "ein", None with no
        article. RBNF writes "zwei Millionenste" where the Regelwerk, § 36 (1.6), writes "der zweimillionste
        Besucher", so an ordinal from one million up declines."""
        value = bounded_integer(digits)
        if value is None or value >= 1_000_000:
            raise DeclinedReading("no German ordinal rule reads one million or more")
        ending = _ENDINGS[(features.definite, features.case or "nominative")][features.gender or M]
        return self.ordinal_sets[ending].ordinal(digits, Features(), request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf.year(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", Features(), request)
        return f"{whole} {request.data['decimal_word']} {_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """A fraction is a neuter noun of the ordinal stem and -tel or -stel: "ein Drittel", "drei Viertel",
        "ein Hundertstel" (Regelwerk § 56 E5). One half reads "ein halb"."""
        top = self.cardinal(numerator, Features(gender=N), request)
        if bounded_integer(denominator) == 2:
            return f"{top} {request.data['half']}"
        stem = self.ordinal(denominator, Features(definite=True), request)
        if bounded_integer(denominator) == 100:
            stem = stem.removeprefix("ein")
        return f"{top} {stem[0].upper()}{stem[1:]}l"


SPELLER = GermanSpeller()


def _digits(digits: str, request: Request) -> str:
    return DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)


def _counted(digits: str, request: Request) -> str:
    return SPELLER.cardinal(digits, Features(), request)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _case(before: Sequence[str], data, noun: str | None = None) -> str | None:
    """The case that the word right before the number governs: a preposition that governs one case, a form of
    "kosten", which takes the price in the accusative (de.wiktionary, "kosten" [1]), or "in", "an" and "vor"
    before a noun of time, which take the dative (de.wikipedia, "Präposition", Zeitlich; de.wiktionary, "vor" [1]).
    "in" and "an" before another noun also say where to, with the accusative, so they give no case there."""
    if not before:
        return None
    word = before[-1].lower()
    if word in data["dative_prepositions"]:
        return "dative"
    if word in data["accusative_prepositions"] or word in data["accusative_verbs"]:
        return "accusative"
    time_noun = noun is not None and noun.lower().endswith(tuple(data["time_nouns"]))
    if word in data["temporal_prepositions"] and time_noun:
        return "dative"
    return None


def noun_gender(word: str, data) -> GrammaticalGender | None:
    """The gender of a noun from the whole-word table, then from a frame of the whole word, then from its ending,
    the longest first. A compound takes the gender of its last part, so "Kaffeetasse" ends in "e" and "Lehrjahr"
    in "jahr"."""
    lower = word.lower()
    if lower in data["noun_genders"]:
        return GrammaticalGender(data["noun_genders"][lower])
    for frame, gender in data["noun_frames"]:
        if re.fullmatch(frame, lower):
            return GrammaticalGender(gender)
    for ending, gender in sorted(data["noun_endings"], key=lambda entry: len(entry[0]), reverse=True):
        if lower.endswith(ending):
            return GrammaticalGender(gender)
    return None


def _noun_after(after: Sequence[str]) -> str | None:
    """The noun that the number counts: the first capitalised word after it, past lowercase adjectives with an
    inflection ending, as in "1 große Tasse"."""
    for word in after:
        if word[:1].isupper():
            return word
        if not (word.islower() and word.endswith(("e", "en", "er", "es", "em"))):
            return None
    return None


def _features(context: SpanContext, gender: GrammaticalGender | None = None) -> Features:
    """The agreement of design section 5.6: the hint, then the gender of the counted noun or of the unit, then the
    params and the file. With no noun after it, a number is counted: "eins". The word right before the number
    gives the case. A noun with no known gender takes only the dative, where the masculine and the neuter of the
    default share "einem"."""
    if context.hint is not None:
        return context.hint
    data = context.request.data
    noun = None
    if gender is None:
        noun = _noun_after(context.after)
        if noun is None:
            return Features()
        gender = noun_gender(noun, data)
    case = _case(context.before, data, noun)
    if gender is None:
        gender = context.request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender
        case = case if case == "dative" else None
    return Features(gender=gender, case=case)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A leading zero, which only a lead admits, reads digit by digit; a lead reads its word and the number is
    counted: "Nummer eins"."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = _digits(digits, request)
    elif fields["lead"]:
        words = _counted(digits, request)
    else:
        words = SPELLER.cardinal(digits, _features(context), request)
    words = _signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def _amount(amount: FrozenMap, request: Request, features: Features) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], features, request)
    else:
        words = SPELLER.cardinal(amount["integer"] or "0", features, request)
    return _signed(words, amount["sign"], request)


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


def _unit_features(context: SpanContext, gender: str) -> Features:
    return _features(context, GrammaticalGender(gender))


def _determiner(context: SpanContext) -> FrozenMap | None:
    if not context.before:
        return None
    return context.request.data["determiners"].get(context.before[-1].lower())


def _ordinal_features(context: SpanContext, gender: GrammaticalGender | None) -> Features:
    """The declension of an ordinal from the determiner right before it. "der" after a preposition is the
    feminine dative, as in "in der 3. Woche", or the feminine genitive, as in "wegen der 3. Mahnung"."""
    if context.hint is not None:
        return context.hint
    determiner = _determiner(context)
    if determiner is None:
        return Features(gender=gender or M)
    case = determiner["case"]
    written_gender = determiner.get("gender")
    data = context.request.data
    prepositions = {*data["dative_prepositions"], *data["accusative_prepositions"], *data["two_way_prepositions"]}
    if context.before[-1].lower() == "der" and len(context.before) > 1:
        if context.before[-2].lower() in prepositions:
            case, written_gender = "dative", "feminine"
        elif context.before[-2].lower() in data["genitive_prepositions"]:
            case, written_gender = "genitive", "feminine"
    if gender is None and written_gender is not None:
        gender = GrammaticalGender(written_gender)
    return Features(gender=gender or M, case=case, definite=determiner["definite"])


def speak_ordinal(span: Span, context: SpanContext) -> str:
    noun = _noun_after(context.after)
    gender = noun_gender(noun, context.request.data) if noun else None
    return SPELLER.ordinal(span.fields["digits"], _ordinal_features(context, gender), context.request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, context.request, Features())


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields = span.fields
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request)
    return _signed(words, fields["sign"], context.request)


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    low, high = _counted(span.fields["low"], request), _counted(span.fields["high"], request)
    return f"{low} {request.data['range_word']} {high}"


def _signed_operand(operand: str, request: Request) -> str:
    sign = {"−": "-"}.get(operand[0], operand[0]) if operand[0] in _SIGNS else ""
    return _signed(_counted(operand.lstrip(_SIGNS), request), sign, request)


def speak_expression(span: Span, context: SpanContext) -> str:
    """Duden, "plus": "fünf plus drei [ist] gleich acht"."""
    request = context.request
    operands = span.fields["operands"]
    words = [_signed_operand(operands[0], request)]
    for operator, operand in zip(span.fields["operators"], operands[1:]):
        words += [request.data["operators"][operator], _signed_operand(operand, request)]
    return " ".join(words)


def speak_date(span: Span, context: SpanContext) -> str:
    """The day is an ordinal that agrees with the masculine "Tag": "der siebzehnte Oktober" (Regelwerk § 36
    (1.6)), "am dritten Mai", and "zwölfter März" with no article. A determiner of another gender belongs to
    another noun, so it does not decide."""
    request = context.request
    fields = span.fields
    month = request.data["months"][fields["month"] - 1]
    year = SPELLER.year(str(fields["year"]), Features(), request) if fields["year"] is not None else None
    if fields["day"] is None:
        return f"{month} {year}"
    determiner = _determiner(context)
    if determiner is not None and determiner.get("gender", "masculine") != "masculine":
        features = Features(gender=M)
    else:
        features = _ordinal_features(context, M)
    words = [SPELLER.ordinal(str(fields["day"]), features, request), month]
    return " ".join(words + ([year] if year is not None else []))


def speak_time(span: Span, context: SpanContext) -> str:
    """Duden, "Uhr": "6:30 Uhr (gesprochen sechs Uhr dreißig)", "elf Uhr sieben", "es ist ein Uhr, aber es ist
    eins". A seconds field declines."""
    request = context.request
    fields = span.fields
    hour, minute = fields["hour"], fields["minute"]
    if fields["second"] is not None:
        raise DeclinedReading("no German rule reads the seconds of a clock time")
    words = f"{SPELLER.cardinal(str(hour), Features(gender=N), request)} {request.data['hour_word']}"
    return f"{words} {_counted(str(minute), request)}" if minute else words


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """German declares no case endings, so the one suffix is the " Uhr" of a time, which `speak_time` reads after
    the hour."""
    return prefix + spoken


def speak_money(span: Span, context: SpanContext) -> str:
    """Two decimals are the minor unit: "zwei Euro fünfzig". A scale word stands between the amount and the
    currency: "zwei Millionen Franken" (Regelwerk § 101: "Mio. (= Million(en))")."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = request.data["currencies"][fields["currency"]]
    gender = _unit_features(context, currency["gender"])
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        trimmed = FrozenMap({**amount, "fraction": fraction.rstrip("0")})
        if trimmed["fraction"] or bounded_integer(integer) != 1:
            scale = request.data["scale_plurals"][scale]
        words = f"{_amount(trimmed, request, Features(gender=F))} {scale} {currency['other']}"
    elif len(fraction) == 2:
        major = f"{SPELLER.cardinal(integer, gender, request)} {currency[plural_category(request, integer)]}"
        minor_digits = str(int(fraction))
        if int(fraction) == 0:
            words = major
        elif bounded_integer(integer) == 0:
            minor = currency["minor"][plural_category(request, minor_digits)]
            words = f"{SPELLER.cardinal(minor_digits, gender, request)} {minor}"
        else:
            words = f"{major} {_counted(minor_digits, request)}"
    else:
        words = f"{_amount(amount, request, gender)} {currency[plural_category(request, _written(amount))]}"
    return _signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]]
    features = _unit_features(context, unit["gender"])
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    joined = f" {link} ".join(_amount(a, request, features) for a in amounts)
    return f"{joined} {unit[plural_category(request, _written(amounts[-1]))]}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """Duden, "Prozent": "5 Prozent oder 5 %", and the noun stays unchanged after a number."""
    percent = context.request.data["percent"]
    features = _unit_features(context, percent["gender"])
    return f"{_amount(span.fields['amount'], context.request, features)} {percent['word']}"


def speak_telephone(span: Span, context: SpanContext) -> str:
    request = context.request
    groups = [_digits(group, request) for group in span.fields["groups"]]
    if span.fields["country_code"]:
        groups.insert(0, f"{request.data['sign_words']['+']} {_digits(span.fields['country_code'], request)}")
    return " ".join(groups)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    data = context.request.data
    key = span.fields["key"]
    for table in ("titles", "abbreviations", "number_abbreviations"):
        if data[table].get(key) is not None:
            return data[table][key]
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


def speak_idiom(span: Span, context: SpanContext) -> str:
    return context.request.data["idioms"][span.fields["key"]]


def speak_year(span: Span, context: SpanContext) -> str:
    """Regelwerk § 36 (1.6): "neunzehnhundertneunundachtzig"."""
    return SPELLER.year(span.fields["digits"], Features(), context.request)


def speak_color(span: Span, context: SpanContext) -> str:
    """The German palettes of ovos-color-parser hold catalogue names, so no table is seeded (design section 12),
    and a colour spells its digits as the text writes them."""
    request = context.request
    return " ".join(_digits(c, request) if c.isdigit() else c.upper() for c in span.fields["hex"])


def _swiss_verbalizer(verbalizer):
    """de-CH writes ss for ß in every reading (Regelwerk § 25 E2)."""
    def speak(span: Span, context: SpanContext) -> str:
        spoken = verbalizer(span, context)
        return spoken.translate(_SS) if context.request.variety.tag == "de-CH" else spoken
    return speak


class GermanTelephone(Telephone):
    """The shared telephone recognizer, where a phone word up to three words back also names a run with the shape
    of a phone number, as in `Das Telefon hat die Nummer 030 1234567.` Two years that a dash joins have no phone
    shape (`no_phone_shapes`), so `Das Telefon war 1990-2000 grau.` reads a range of years."""

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        index = bisect_right(words, start, key=lambda word: word.end)
        return range(index - len(clause_window(text, words, start, end, -1, limit=3, breaks=breaks)), index)

    def names_back(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
                   shaped: bool, short_code: bool, request: Request) -> bool:
        return shaped


@dataclass(frozen=True)
class Money:
    """The shared money recognizer. A scale abbreviation at the end of a sentence, as in `CHF 2 Mio.`, carries the
    one full stop that also ends the sentence (Regelwerk § 103), so the span keeps it as its trail."""
    name: str = "money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in SHARED["money"].find(text, tokens, request):
            following = next_visible(text, span.end)
            if text[span.end - 1] == "." and not span.trail and (following == "" or following.isupper()):
                span = replace(span, trail=".")
            yield span


@dataclass(frozen=True)
class Time:
    """The shared clock recognizer. A clock mark that is also the decimal mark of the request, the full stop in
    de-CH (CLDR `de_CH`, decimal "."), needs the time suffix "Uhr", because a time word such as "um" also comes
    before an amount: `um 14.30 Uhr` is a time, and `um 1.15 Franken` is an amount.

    The range word joins a clock time to a time with "Uhr", which is the evidence of both, as in
    `von 9:00 bis 17:00 Uhr`. "von" and "bis" are no time words, because they also come before a ratio, as in
    `ein Maßstab von 1:25`."""
    name: str = "time_clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        yield from self._joined(text, data)
        decimal_mark = request.params.decimal_mark or data.get("defaults", FrozenMap()).get("decimal_mark", "")
        for span in SHARED["time_clock"].find(text, tokens, request):
            if span.fields["suffix"] or not decimal_mark or decimal_mark not in text[span.start:span.end]:
                yield span

    def _joined(self, text: str, data: FrozenMap) -> Iterator[Span]:
        marks = "".join(re.escape(clock["mark"]) for clock in data.get("clock_marks", ()))
        suffixes = "|".join(re.escape(suffix) for suffix in data.get("time_suffixes", ()))
        if not (marks and suffixes and data.get("range_word")):
            return
        joined = re.compile(f"([0-9][0-9]?)[{marks}]([0-9][0-9]) {re.escape(data['range_word'])} "
                            f"([0-9][0-9]?)(?:[{marks}]([0-9][0-9]))?(?:{suffixes})")
        for match in joined.finditer(fold_digits(text)):
            start, end = match.span()
            fields = clock_fields(match.group(1), match.group(2), None)
            if (fields is not None and clock_fields(match.group(3), match.group(4) or "00", None) is not None
                    and is_bounded(text, start, end) and one_digit_set(text[start:end])):
                yield Span(start, match.end(2), Form.TIME,
                           FrozenMap({"hour": fields[0], "minute": fields[1], "second": None, "period": None,
                                      "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Fraction:
    """The shared fraction recognizer. One half before a noun is the adjective "halb", which declines, as in "eine
    halbe Million" (de.wiktionary, "halb" [1]), and the file gives no declined reading, so `1/2 Pizza` stays as
    written. A noun is a capitalised word of letters that no abbreviation of the file spells, so no other form
    reads it and a second pass sees the same noun."""
    name: str = "fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        abbreviations = {*data.get("titles", ()), *data.get("abbreviations", ()), *data.get("number_abbreviations", ()),
                         *data.get("scales", ()),
                         *(symbol for currency in data.get("currencies", FrozenMap()).values()
                           for symbol in currency.get("symbols", ()))}
        for span in SHARED["fraction"].find(text, tokens, request):
            start = stop = span.end + 1
            while stop < len(text) and text[stop].isalpha():
                stop += 1
            word = text[start:stop]
            noun = (text[span.end:start].isspace() and word[:1].isupper() and word[1:].islower()
                    and is_bounded(text, start, stop) and word + text[stop:stop + 1] not in abbreviations)
            yield replace(span, keep=True) if noun and bounded_integer(span.fields["denominator"]) == 2 else span


@dataclass(frozen=True)
class TitleAbbreviation(Abbreviation):
    """The abbreviations of `en.py`, where a title reads before a capitalised name. A title also reads before `#`,
    because the lead and the colour read as capitalised words, "Nummer" and "F", and a second pass would read the
    title before them."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        yield from super().find(text, tokens, request)
        for key in request.data.get("titles", FrozenMap()):
            position = text.find(key)
            while position != -1:
                end = position + len(key)
                if is_bounded(text, position, end) and next_visible(text, end) == "#":
                    yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}), recognizer=self.name)
                position = text.find(key, end)


@dataclass(frozen=True)
class Ordinal:
    """A number and a full stop that mark an ordinal (Regelwerk § 104: "der 2. Weltkrieg"), after a determiner of
    the `determiners` table, as in `am 3. Tag` and `der 2. Platz`. At the end of a sentence the one full stop also
    ends it (§ 105), so the span keeps it as its trail.

    With no determiner, a full stop and more text after the number do not tell an ordinal, as in `1. FC Köln`,
    from the end of a sentence, as in `Er ist 3. Sie ist 4.`, so the number stays as written."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        determiners = request.data["determiners"]
        words = context_words(tokens)
        breaks = clause_breaks(text)
        for number in numbers_in(text, request):
            stop = number.end
            if (number.sign or number.fraction is not None or not text.startswith(".", stop)
                    or not is_bounded(text, number.start, stop + 1)
                    or (stop + 1 < len(text) and text[stop + 1].isdigit())):
                continue
            fields = FrozenMap({"digits": number.integer, "marker": ".", "prefix": "", "suffix": "",
                                "script": number.script})
            before = clause_window(text, words, number.start, number.end, -1, limit=1, breaks=breaks)
            following = next_visible(text, stop + 1)
            if before and before[0].lower() in determiners:
                yield Span(number.start, stop + 1, Form.ORDINAL, fields, trail="" if following else ".",
                           recognizer=self.name)
            elif following:
                yield Span(number.start, stop + 1, Form.ORDINAL, fields, recognizer=self.name, keep=True)


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 after a word of the `year_words` table, as in `im Jahr 1989`, and two such years
    that a range mark joins, the lower one first, as in `1939-1945`."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._years(text, tokens, request), text, request)

    def _years(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        year_words = frozenset(request.data["year_words"])
        marks = frozenset(request.data["range_marks"])
        words = context_words(tokens)
        breaks = clause_breaks(text)
        numbers = [n for n in numbers_in(text, request) if not n.sign and n.fraction is None
                   and n.end - n.start == 4 and 1000 <= int(n.integer) <= 2099 and is_bounded(text, n.start, n.end)]
        claimed = set()
        for first, second in zip(numbers, numbers[1:]):
            if text[first.end:second.start] in marks and int(first.integer) < int(second.integer):
                claimed |= {first, second}
        for number in numbers:
            before = clause_window(text, words, number.start, number.end, -1, limit=1, breaks=breaks)
            if number in claimed or (before and before[0] in year_words):
                yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": number.integer, "suffix": ""}),
                           recognizer=self.name)


@dataclass(frozen=True)
class DateNamed:
    """`12. März 2024`, `am 3. Mai`, `März 2024`: a date with a month name (CLDR `de`, dateFormats long,
    `d. MMMM y`)."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        patterns = request.data["patterns"]
        month_numbers = request.data["month_numbers"]
        folded = fold_digits(text)
        for key in ("date_day_month", "date_month_year"):
            for match in re.finditer(patterns[key], folded):
                start, end = match.span()
                if not is_bounded(text, start, end) or not one_digit_set(text[start:end]):
                    continue
                if key == "date_month_year":
                    day, month_name, year = None, match.group(1), match.group(2)
                else:
                    day, month_name, year = match.group(1), match.group(2), match.group(3)
                month = month_numbers[month_name]
                year_value = int(year) if year is not None else None
                if day is not None and not is_valid(year_value, month, int(day)):
                    continue
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": year_value, "month": month, "day": int(day) if day else None,
                                      "written_order": "DMY", "month_written": "name", "prefix": "",
                                      "suffix": ""}), recognizer=self.name)


DATA = freeze({**DATA, "patterns": {
    "expression": "[-−+]?[0-9]+(?: ?[+−×÷=] ?[-−+]*[0-9]+)+",
    "date_day_month": "([0-9][0-9]?)[.] " + _MONTH + "(?: ([0-9][0-9][0-9][0-9]))?",
    "date_month_year": _MONTH + " ([0-9][0-9][0-9][0-9])",
}})

_VERBALIZERS = {
    Form.COLOR: speak_color, Form.IDIOM: speak_idiom, Form.DATE: speak_date, Form.TIME: speak_time,
    Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
    Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
    Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal, Form.ABBREVIATION: speak_abbreviation,
    Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal, Form.YEAR: speak_year,
}

LANGUAGE = LanguageSpec(
    code="de",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["color"], SHARED["idiom"], DateNamed(), SHARED["date_numeric"],
                 Time(), GermanTelephone(), Money(), SHARED["percent"], SHARED["measure"],
                 Year(), Expression(), Fraction(), SHARED["range"], Ordinal(), TitleAbbreviation(),
                 SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon,
                 **{form: _swiss_verbalizer(verbalizer) for form, verbalizer in _VERBALIZERS.items()}},
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER,
              Form.YEAR: SPELLER},
    attach=attach,
    genders=frozenset({M, F, N}),
    default_gender=M,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"24h"}),
        "minute_style": frozenset({"number"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long"}),
        "default_gender": frozenset({"masculine", "feminine", "neuter"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"register"}),
)
