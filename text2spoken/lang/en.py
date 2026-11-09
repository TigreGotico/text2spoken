"""English: en-GB, the default variety, and en-US.

Number words come from CLDR RBNF. American English writes no "and" in the whole part of a number, and
British English writes "one hundred and one" (Wikipedia, "English numerals"), so each variety names its rule
set. The design page `text2spoken-design.md`, section 5.4, gives the measured reason for each speller.
"""
from __future__ import annotations

import logging
import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.numbers import Number
from text2spoken.core.recognizers import (PHONE_PLANS, SHARED, Telephone, _edge, join_ranges, numbers_in,
                                          speak_cardinal, speak_lexicon)
from text2spoken.core.spans import Features, Span, SpanContext, Word, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import DigitSpeller, RbnfSpeller
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import Token, fold_digits, is_bounded, is_letter, next_visible, one_digit_set
from text2spoken.params import FrozenMap, Form, freeze

LOG = logging.getLogger("text2spoken")

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
_MONTH = "(" + "|".join(MONTHS) + ")"
_ORDINAL_MARK = "(?:st|nd|rd|th)"
_TRAILING_GROUP = re.compile("[0-9]{1,2}(?:[.][0-9]{2})?")

COLORS = {
    "000000": "black", "0000cd": "medium blue", "0000ff": "blue", "006400": "dark green", "008000": "green",
    "008080": "teal", "008b8b": "dark cyan", "00bfff": "deep sky blue", "00ced1": "dark turquoise",
    "00fa9a": "medium spring green", "00ff00": "lime", "00ff7f": "spring green", "00ffff": "cyan",
    "191970": "midnight blue", "1e90ff": "dodger blue", "20b2aa": "light sea green", "228b22": "forest green",
    "2e8b57": "sea green", "2f4f4f": "dark slate gray", "32cd32": "lime green", "3cb371": "medium sea green",
    "40e0d0": "turquoise", "4169e1": "royal blue", "4682b4": "steel blue", "483d8b": "dark slate blue",
    "48d1cc": "medium turquoise", "4b0082": "indigo", "556b2f": "dark olive green", "5f9ea0": "cadet blue",
    "6495ed": "cornflower blue", "66cdaa": "medium aquamarine", "696969": "dim gray", "6a5acd": "slate blue",
    "6b8e23": "olive drab", "708090": "slate gray", "778899": "light slate gray", "7b68ee": "medium slate blue",
    "7cfc00": "lawn green", "7fff00": "chartreuse", "7fffd4": "aquamarine", "800000": "maroon", "800080": "purple",
    "808000": "olive", "808080": "gray", "87ceeb": "sky blue", "87cefa": "light sky blue", "8a2be2": "blue-violet",
    "8b0000": "dark red", "8b008b": "dark magenta", "8b4513": "saddle brown", "8fbc8b": "dark sea green",
    "90ee90": "light green", "9370db": "medium purple", "9400d3": "dark violet", "9932cc": "dark orchid",
    "9acd32": "yellow-green", "a0522d": "sienna", "a52a2a": "brown", "add8e6": "light blue",
    "b0c4de": "light steel blue", "b0e0e6": "powder blue", "b22222": "firebrick", "b8860b": "dark goldenrod",
    "ba55d3": "medium orchid", "bc8f8f": "rosy brown", "bdb76b": "dark khaki", "c0c0c0": "silver",
    "cd5c5c": "indian red", "d2691e": "chocolate", "d2b48c": "tan", "d3d3d3": "light gray", "d8bfd8": "thistle",
    "da70d6": "orchid", "daa520": "goldenrod", "dc143c": "crimson", "dcdcdc": "gainsboro", "dda0dd": "plum",
    "deb887": "burlywood", "e0ffff": "light cyan", "e6e6fa": "lavender", "e9967a": "dark salmon", "ee82ee": "violet",
    "f08080": "light coral", "f0e68c": "khaki", "f0f8ff": "alice blue", "f0ffff": "azure", "f4a460": "sandy brown",
    "f5deb3": "wheat", "f5f5dc": "beige", "f5fffa": "mint cream", "f8f8ff": "ghost white", "fa8072": "salmon",
    "faebd7": "antique white", "faf0e6": "linen", "fafad2": "light goldenrod yellow", "fdf5e6": "old lace",
    "ff0000": "red", "ff00ff": "magenta", "ff1493": "deep pink", "ff6347": "tomato", "ff69b4": "hot pink",
    "ff7f50": "coral", "ff8c00": "dark orange", "ffa07a": "light salmon", "ffa500": "orange", "ffb6c1": "light pink",
    "ffc0cb": "pink", "ffd700": "gold", "ffdab9": "peach puff", "ffdead": "navajo white", "ffe4b5": "moccasin",
    "ffe4c4": "bisque", "ffe4e1": "misty rose", "ffebcd": "blanched almond", "ffefd5": "papaya whip",
    "fff0f5": "lavender blush", "fff5ee": "seashell", "fff8dc": "cornsilk", "fffacd": "lemon chiffon",
    "fffaf0": "floral white", "fffafa": "snow", "ffff00": "yellow", "ffffe0": "light yellow", "fffff0": "ivory",
    "ffffff": "white",
}
"""Seeded by `scripts/seed_colors.py en` from the ovos-color-parser palette `en-US/dot-net-colors.json`."""

UNITS_GB = {
    "kg": {"one": "kilogram", "other": "kilograms"},
    "g": {"one": "gram", "other": "grams"},
    "mg": {"one": "milligram", "other": "milligrams"},
    "km": {"one": "kilometre", "other": "kilometres"},
    "m": {"one": "metre", "other": "metres"},
    "cm": {"one": "centimetre", "other": "centimetres"},
    "mm": {"one": "millimetre", "other": "millimetres"},
    "km/h": {"one": "kilometre per hour", "other": "kilometres per hour"},
    "m/s": {"one": "metre per second", "other": "metres per second"},
    "mph": {"one": "mile per hour", "other": "miles per hour"},
    "ml": {"one": "millilitre", "other": "millilitres"},
    "°C": {"one": "degree Celsius", "other": "degrees Celsius"},
    "°F": {"one": "degree Fahrenheit", "other": "degrees Fahrenheit"},
    "MHz": {"one": "megahertz", "other": "megahertz"},
    "GHz": {"one": "gigahertz", "other": "gigahertz"},
    "MB": {"one": "megabyte", "other": "megabytes"},
}

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}, {"decimal": ",", "group": "."}]},
    "defaults": {"date_order": "DMY", "clock": "12h", "minute_style": "number", "decimal_mark": ".",
                 "scale": "short"},
    "sign_words": {"-": "minus", "+": "plus"},
    "decimal_word": "point",
    "digit_words": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "leads": {"#": "number", "-": ""},
    "fraction_names": {"2": ["half", "halves"], "4": ["quarter", "quarters"]},
    "idioms": {"24/7": "twenty-four seven", "50/50": "fifty-fifty"},
    "range_word": "to",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"},
                    {"mark": ".", "seconds": False, "needs": "day_period"}],
    "dimension_marks": ["x", "×"],
    "dimension_word": "by",
    "operators": {"+": "plus", "−": "minus", "×": "times", "÷": "divided by", "=": "equals"},
    "time_words": ["at", "from", "until", "till", "since", "before", "after", "around"],
    "year_words": ["in", "since", "until", "till", "during", "circa", "year"],
    "year_links": ["and", "or", "to"],
    "function_words": ["a", "an", "the", "and", "or", "but", "so", "then", "to", "in", "on", "at", "by",
                       "for", "from", "with", "as", "after", "before", "until", "since", "when", "while", "where",
                       "he", "she", "it", "we", "they", "you", "his", "her", "its", "our", "their", "this",
                       "that", "there", "was", "were", "is", "are", "had", "has", "have", "many", "some", "all",
                       "now", "immediately", "today", "tonight"],
    "day_periods": {"am": ["am", "a.m.", "AM", "A.M."], "pm": ["pm", "p.m.", "PM", "P.M."]},
    "spoken_periods": {"am": "AM", "pm": "PM"},
    "minute_phrases": {"0": "{hour} o'clock", "15": "quarter past {hour}", "30": "half past {hour}",
                       "45": "quarter to {next_hour}"},
    "months": MONTHS,
    "numeric_date_reading": {"full": "the {day} of {month} {year}", "no_year": "the {day} of {month}"},
    "currencies": {
        "USD": {"symbols": ["$", "US$"], "one": "dollar", "other": "dollars",
                "minor": {"one": "cent", "other": "cents"}},
        "GBP": {"symbols": ["£"], "one": "pound", "other": "pounds", "minor": {"one": "penny", "other": "pence"}},
        "EUR": {"symbols": ["€"], "one": "euro", "other": "euros", "minor": {"one": "cent", "other": "cents"}},
        "JPY": {"symbols": ["¥"], "one": "yen", "other": "yen", "minor": {"one": "sen", "other": "sen"}},
    },
    "scales": {"thousand": "thousand", "million": "million", "billion": "billion", "trillion": "trillion",
               "k": "thousand", "m": "million", "bn": "billion"},
    "percent": {"signs": ["%"], "position": "after", "word": "per cent"},
    "units": UNITS_GB,
    "phone_words": ["phone", "telephone", "tel", "call", "dial", "ring", "text", "mobile", "cell", "fax"],
    "short_codes": ["000", "101", "111", "112", "211", "311", "411", "511", "611", "711", "811", "911", "988", "999"],
    "list_links": ["and", "or"],
    "phone_shapes": ["[(][2-9][0-9]{2}[)] [2-9][0-9]{2}[- ][0-9]{4}", "[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}"],
    "phone_unit_shapes": ["(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "color_words": ["color", "colour", "colors", "colours"],
    "colors": COLORS,
    "titles": {"Dr.": "Doctor", "Mr.": "Mister", "Mrs.": "Missus", "Prof.": "Professor",
               "Dr": "Doctor", "Mr": "Mister", "Mrs": "Missus"},
    "abbreviations": {"etc.": "et cetera", "e.g.": "for example", "i.e.": "that is", "vs.": "versus"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"No.": "number"},
    "symbols": {"%": "percent", "$": "money", "£": "money", "€": "money", "¥": "money", "°": "measure",
                "×": "measure"},
    "ordinal_marks": ["st", "nd", "rd", "th"],
    "patterns": {
        "expression": "[-−]?[0-9]+(?: ?[+−×÷=] ?[0-9]+)+",
        "date_month_day": _MONTH + " ([0-9][0-9]?)" + _ORDINAL_MARK + "?(?:,? ([0-9][0-9][0-9][0-9]))?",
        "date_day_month": "([0-9][0-9]?)" + _ORDINAL_MARK + "? (?:of )?" + _MONTH + "(?:,? ([0-9][0-9][0-9][0-9]))?",
        "date_month_year": _MONTH + " ([0-9][0-9][0-9][0-9])",
    },
})

VARIETIES = (
    Variety("en-GB", freeze({"colors": {code: name.replace("gray", "grey") for code, name in COLORS.items()
                                        if "gray" in name}})),
    Variety("en-US", freeze({
        "defaults": {"date_order": "MDY"},
        "numeric_date_reading": {"full": "{month} {day} {year}", "no_year": "{month} {day}"},
        "percent": {"word": "percent"},
        "titles": {"Dr": None, "Mr": None, "Mrs": None},
        "units": {unit: {category: word.replace("metre", "meter").replace("litre", "liter")
                         for category, word in forms.items()} for unit, forms in UNITS_GB.items()},
    })),
)


def ordinal_suffix(number: int) -> str:
    """The written suffix of an English ordinal: "th" when the tens digit is 1, else by the last digit."""
    if number // 10 % 10 == 1:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


class EnglishSpeller:
    """RBNF integers with the rule sets of each variety, decimals read digit by digit after "point"."""

    def __init__(self):
        self.rbnf = {
            "en-GB": RbnfSpeller(cardinal={Features(): "spellout-cardinal-verbose"},
                                 ordinal={Features(): "spellout-ordinal-verbose"}),
            "en-US": RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"}),
        }

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf[request.variety.tag].cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf[request.variety.tag].ordinal(digits, features, request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        """`spellout-numbering-year`, except that a year it reads with "thousand" reads as the cardinal of the
        variety: "two thousand (and) one" for 2001 (Wikipedia, "English numerals", Dates)."""
        words = self.rbnf[request.variety.tag].year(digits, features, request)
        return self.cardinal(digits, features, request) if "thousand" in words else words

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", features, request)
        return f"{whole} {request.data['decimal_word']} {_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """One-half, two-thirds, three-quarters, one one-hundredth (Wikipedia, "English numerals")."""
        top = self.cardinal(numerator, features, request)
        plural = int(numerator) != 1
        names = request.data["fraction_names"].get(str(int(denominator)))
        if names is not None:
            bottom = names[plural]
        else:
            bottom = self.ordinal(denominator, features, request).replace(" ", "-") + ("s" if plural else "")
        simple = " " not in top and "-" not in top and "-" not in bottom
        return f"{top}-{bottom}" if simple else f"{top} {bottom}"


SPELLER = EnglishSpeller()


def _digits(digits: str, request: Request) -> str:
    return DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)


def _cardinal(digits: str, request: Request) -> str:
    return SPELLER.cardinal(digits, Features(), request)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _amount(amount: FrozenMap, request: Request) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    else:
        words = _cardinal(amount["integer"], request)
    return _signed(words, amount["sign"], request)


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


def speak_ordinal(span: Span, context: SpanContext) -> str:
    return SPELLER.ordinal(span.fields["digits"], Features(), context.request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields = span.fields
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request)
    return _signed(words, fields["sign"], context.request)


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    return f"{_cardinal(span.fields['low'], request)} {request.data['range_word']} {_cardinal(span.fields['high'], request)}"


def speak_expression(span: Span, context: SpanContext) -> str:
    """The first operand may carry a sign, as in `-2+3=1`: "minus two plus three equals one"."""
    request = context.request
    first = span.fields["operands"][0]
    words = [_signed(_cardinal(first.lstrip("-−"), request), "-" if first[0] in "-−" else "", request)]
    for operator, operand in zip(span.fields["operators"], span.fields["operands"][1:]):
        words += [request.data["operators"][operator], _cardinal(operand, request)]
    return " ".join(words)


def speak_date(span: Span, context: SpanContext) -> str:
    request = context.request
    fields = span.fields
    month = request.data["months"][fields["month"] - 1]
    year = SPELLER.year(str(fields["year"]), Features(), request) if fields["year"] is not None else None
    if fields["day"] is None:
        return f"{month} {year}"
    day = SPELLER.ordinal(str(fields["day"]), Features(), request)
    if fields["month_written"] == "name":
        template = "{month} {day} {year}" if fields["written_order"] == "MDY" else "the {day} of {month} {year}"
    else:
        template = request.data["numeric_date_reading"]["full"]
    if year is None:
        template = template.replace(" {year}", "")
    return template.format(month=month, day=day, year=year)


def speak_time(span: Span, context: SpanContext) -> str:
    """The 12-hour reading says the day period that the text writes, or that hours 0 and 13 to 23 imply
    (Wikipedia, "12-hour clock"). Minutes 1 to 9 read "oh one" to "oh nine"."""
    request = context.request
    params = request.params
    fields = span.fields
    hour, minute, second = fields["hour"], fields["minute"], fields["second"]
    period = fields["period"]
    if period is None and params.clock == "12h" and (hour == 0 or hour >= 13):
        period = "pm" if hour >= 13 else "am"
    twelve = fields["period"] is not None or params.clock == "12h"
    face = twelve_hour(hour) if twelve else hour
    next_face = twelve_hour(hour + 1) if twelve else (hour + 1) % 24
    phrase = request.data["minute_phrases"].get(str(minute))
    if params.minute_style == "phrase" and phrase is not None and second is None:
        words = phrase.format(hour=_cardinal(str(face), request), next_hour=_cardinal(str(next_face), request))
    elif minute == 0 and second is None:
        if not twelve:
            words = f"{_cardinal(str(face), request)} hundred"
        elif period is not None:
            words = _cardinal(str(face), request)
        else:
            words = request.data["minute_phrases"]["0"].format(hour=_cardinal(str(face), request))
    else:
        minutes = f"oh {_cardinal(str(minute), request)}" if minute < 10 else _cardinal(str(minute), request)
        words = f"{_cardinal(str(face), request)} {minutes}"
    if second is not None:
        unit = "second" if plural_category(request, str(second)) == "one" else "seconds"
        words += f" and {_cardinal(str(second), request)} {unit}"
    if period is not None:
        words += " " + request.data["spoken_periods"][period]
    return words


def speak_money(span: Span, context: SpanContext) -> str:
    """A scale word comes between the amount and the plural currency name: "two million dollars"."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = request.data["currencies"][fields["currency"]]
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        amount = FrozenMap({**amount, "fraction": (fraction or "").rstrip("0")})
        words = f"{_amount(amount, request)} {request.data['scales'][fields['scale']]} {currency['other']}"
    elif len(fraction) == 2:
        major = f"{_cardinal(integer, request)} {currency[plural_category(request, integer)]}"
        minor_digits = str(int(fraction))
        minor = f"{_cardinal(minor_digits, request)} {currency['minor'][plural_category(request, minor_digits)]}"
        if int(fraction) == 0:
            words = major
        else:
            words = minor if int(integer) == 0 else f"{major} and {minor}"
    else:
        words = f"{_amount(amount, request)} {currency[plural_category(request, _written(amount))]}"
    return _signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]][plural_category(request, _written(amounts[-1]))]
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    joined = f" {link} ".join(_amount(a, request) for a in amounts)
    return f"{joined} {unit}"


def speak_percent(span: Span, context: SpanContext) -> str:
    request = context.request
    return f"{_amount(span.fields['amount'], request)} {request.data['percent']['word']}"


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
    """The short end of a year range, `45` in `1939-45`, holds the whole year and reads without the century when
    the year reading starts with it: "nineteen thirty-nine to forty-five", "twenty ten to twelve"."""
    request = context.request
    digits = span.fields["digits"]
    words = SPELLER.year(digits, Features(), request)
    century = _cardinal(digits[:2], request) + " "
    if span.end - span.start == 2 and words.startswith(century):
        return words[len(century):]
    return words


def speak_color(span: Span, context: SpanContext) -> str:
    """A colour with no name spells its digits as the text writes them (section 12)."""
    request = context.request
    name = request.data["colors"].get(span.fields["rgb"])
    if span.fields["alpha"] is not None:
        LOG.warning("unread alpha %r of colour #%s for %s", span.fields["alpha"], span.fields["rgb"], request.tag)
    if name is not None:
        return name
    return " ".join(_digits(c, request) if c.isdigit() else c.upper() for c in span.fields["hex"])


def _hour_follows(text: str, end: int, day_periods: Sequence[str], function_words: frozenset[str]) -> bool:
    """Whether a space and a day period, or a space and a lowercase word that is no function word, follow
    text[:end], as `8 am` and `24 hours a day` follow a phone number."""
    if not text.startswith(" ", end):
        return False
    if any(text.startswith(period, end + 1) and is_bounded(text, end + 1, end + 1 + len(period))
           for period in day_periods):
        return True
    stop = end + 1
    while stop < len(text) and is_letter(text[stop]):
        stop += 1
    word = text[end + 1:stop]
    return word.islower() and word not in function_words


class EnglishTelephone(Telephone):
    """The shared telephone recognizer with the English conventions of design section 4.3.

    A phone word also names a run up to three words back, where a function word does not count, when the run has
    the shape of a phone number, as in `Call us on 0800 123 456.` The same window names a short code of
    `short_codes` that ends its clause or that a function word follows, as in `Call the police on 999 now.`, and
    not the count in `The phone rang 101 times.`

    The `phone_unit_shapes` of `en` make space-separated groups of which the first starts with `0`, perhaps in
    brackets, read digit by digit as one unit, as in `020 7946 0018` and `(0161) 496 0000`. Its
    `phone_kept_shapes` keep thousands that spaces group, as in `10 000`, as written, and its `no_phone_shapes`
    take the phone shape from two years that a dash joins.

    A last group of one or two digits is the hour or a count, not a phone group, when the run ends inside a word,
    when a full stop and two digits complete it, or when a space and a day period or a lowercase word that is no
    function word follow it, so `Call 0800 123 456 8 am to 8 pm.` and `Ring 0800 123 456 24 hours a day.` read
    the number and the hour."""

    def trimmed(self, text: str, start: int, written: str, request: Request) -> str:
        function_words = frozenset(request.data.get("function_words", ()))
        day_periods = [period for periods in request.data.get("day_periods", {}).values() for period in periods]
        cut, after = written.rfind(" "), start + len(written)
        if cut != -1 and _TRAILING_GROUP.fullmatch(written, cut + 1) and (
                "." in written[cut:] or not _edge(text, start, after)
                or _hour_follows(text, after, day_periods, function_words)):
            return written[:cut]
        return written

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        """Three content words back, within eight words of the clause."""
        function_words = frozenset(request.data.get("function_words", ()))
        index = bisect_right(words, start, key=lambda word: word.end)
        before = clause_window(text, words, start, end, -1, limit=8, breaks=breaks)
        counted = [i for i in range(index - len(before), index) if words[i].text.lower() not in function_words]
        return range(counted[-3] if len(counted) >= 3 else index - len(before), index)

    def names_back(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
                   shaped: bool, short_code: bool, request: Request) -> bool:
        if shaped:
            return True
        if not short_code:
            return False
        function_words = frozenset(request.data.get("function_words", ()))
        following = clause_window(text, words, start, end, 1, limit=1, breaks=breaks)
        return all(word.lower() in function_words for word in following)


@dataclass(frozen=True)
class Ordinal:
    """`1st`, `22nd`, `113th`, `1,000th`: a whole number with the suffix that it takes."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        for number in numbers_in(text, request):
            marker = text[number.end:number.end + 2]
            if (number.sign or number.fraction is not None or marker not in marks
                    or ordinal_suffix(int(number.integer[-2:])) != marker
                    or not is_bounded(text, number.start, number.end + 2)):
                continue
            yield Span(number.start, number.end + 2, Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 (section 4.2): after a year word, as in `In 1984`; two years that a range mark
    joins, the lower one first, as in `1939-1945`, or a year and a higher two-digit end after a year word, as in
    `during 1939-45`; and a number that a link joins to a year, as in `In 1066 and 1215`. A comma alone links
    only inside a list that a link word ends, as in `In 1066, 1215 and 1415`.

    A count read as a year is wrong, so the follower of a linked list decides for all its years, and a range is
    one link of a list. A lowercase word that is not in `function_words` blocks them, as in `in 1234 steps`, and
    so do a unit of the units table in any case, an operator and a dimension mark, as in `in 2048 MB` and
    `in 1920 × 1080`."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._years(text, tokens, request), text, request)

    def _years(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        year_words = frozenset(data["year_words"])
        function_words = frozenset(data["function_words"])
        marks = frozenset(data["range_marks"])
        units = frozenset(unit.lower() for unit in data["units"])
        signs = frozenset(data["operators"]) | frozenset(data["dimension_marks"]) | {"*", "/"}
        word_link = re.compile(",? (?:" + "|".join(map(re.escape, data["year_links"])) + ") ")
        words = context_words(tokens)
        breaks = clause_breaks(text)
        numbers = [n for n in numbers_in(text, request) if not n.sign and n.fraction is None
                   and n.end - n.start in (2, 4) and is_bounded(text, n.start, n.end)]

        def year(number: Number) -> bool:
            return number.end - number.start == 4 and 1000 <= int(number.integer) <= 2099

        def after_year_word(number: Number) -> bool:
            before = clause_window(text, words, number.start, number.end, -1, limit=1, breaks=breaks)
            return bool(before) and before[0].lower() in year_words

        def free(end: int) -> bool:
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
            if start in (end, len(text)):
                return True
            stop = start
            while stop < len(text) and not text[stop].isspace():
                stop += 1
            follower = text[start:stop].rstrip(".,;:!?)")
            if (text[start] in signs and not is_letter(text[start])) or follower.lower() in units:
                return False
            stop = start
            while stop < len(text) and is_letter(text[stop]):
                stop += 1
            word = text[start:stop]
            return not word.islower() or word in function_words

        claimed = {}
        partners = {}
        for first, second in zip(numbers, numbers[1:]):
            if not (year(first) and text[first.end:second.start] in marks):
                continue
            if year(second) and int(first.integer) < int(second.integer):
                claimed |= {first: first.integer, second: second.integer}
                partners |= {first: second, second: first}
            elif (second.end - second.start == 2 and int(first.integer) % 100 < int(second.integer)
                  and after_year_word(first)):
                claimed |= {first: first.integer, second: first.integer[:2] + second.integer}
                partners |= {first: second, second: first}
        chains: list[list[Number]] = []
        for number in numbers:
            if not (year(number) or number in claimed):
                continue
            gap = text[chains[-1][-1].end:number.start] if chains else ""
            if chains and (gap == ", " or word_link.fullmatch(gap) or partners.get(number) is chains[-1][-1]):
                chains[-1].append(number)
            elif number in claimed or after_year_word(number):
                chains.append([number])
        for chain in chains:
            while len(chain) > 1 and text[chain[-2].end:chain[-1].start] == ", ":
                chain.pop()
            if free(chain[-1].end):
                claimed |= {number: number.integer for number in chain if number not in claimed}
            else:
                for number in chain:
                    claimed.pop(number, None)
        for number, digits in claimed.items():
            yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": digits, "suffix": ""}),
                       recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, `No.` before a number, and the abbreviations of the table."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        tables = (("titles", str.isupper), ("number_abbreviations", str.isdigit), ("abbreviations", lambda _: True))
        final = frozenset(data["sentence_final"])
        for table, follows in tables:
            for key in sorted((k for k, v in data[table].items() if v is not None), key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    if is_bounded(text, position, end) and follows(following):
                        sentence_end = key in final and (following == "" or following.isupper())
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}),
                                   trail="." if sentence_end else "", recognizer=self.name)
                    position = text.find(key, end)


@dataclass(frozen=True)
class Expression:
    """`5+3`, `2 × 2 = 4`, `-2+3=1`: operators between integers, with no letter on either side. The first
    integer may carry a minus sign.

    An operator right after the last integer stays with the expression, so `1+1 × 10%` keeps `1+1 ×` as
    written: the percentage claims `10`, and a second pass finds `1+1 × ten` with the same open operator."""
    name: str = "expression"
    form: Form = Form.EXPRESSION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        operators = "".join(request.data["operators"])
        open_operator = re.compile(f" ?[{re.escape(operators)}]")
        for match in re.finditer(request.data["patterns"]["expression"], fold_digits(text)):
            start, end = match.span()
            if (not (is_bounded(text, start, end) and one_digit_set(text[start:end]))
                    or open_operator.match(text, end)):
                continue
            written = match.group().replace(" ", "")
            operands = tuple(re.split("[" + operators + "]", written))
            signs = tuple(c for c in written if c in operators)
            yield Span(start, end, Form.EXPRESSION, FrozenMap({"operands": operands, "operators": signs}),
                       recognizer=self.name)


@dataclass(frozen=True)
class DateNamed:
    """`March 12, 2024`, `12th of March 2024`, `March 2024`: a date with a month name."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        patterns = request.data["patterns"]
        symbols = request.data["symbols"]
        folded = fold_digits(text)
        for key, order in (("date_month_day", "MDY"), ("date_day_month", "DMY"), ("date_month_year", "MY")):
            for match in re.finditer(patterns[key], folded):
                start, end = match.span()
                if (not is_bounded(text, start, end) or (start and text[start - 1] in symbols)
                        or not one_digit_set(text[start:end])):
                    continue
                if order == "MY":
                    month_name, day, year = match.group(1), None, match.group(2)
                elif order == "MDY":
                    month_name, day, year = match.group(1), match.group(2), match.group(3)
                else:
                    day, month_name, year = match.group(1), match.group(2), match.group(3)
                written_day = match.group()[match.start(1 if order == "DMY" else 2) - start:]
                if day is not None and written_day[len(day):len(day) + 2] in ("st", "nd", "rd", "th") \
                        and written_day[len(day):len(day) + 2] != ordinal_suffix(int(day)):
                    continue
                month = request.data["months"].index(month_name) + 1
                year_value = int(year) if year is not None else None
                if day is not None and not is_valid(year_value, month, int(day)):
                    continue
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": year_value, "month": month, "day": int(day) if day else None,
                                      "written_order": "DMY" if order == "DMY" else "MDY", "month_written": "name",
                                      "prefix": "", "suffix": ""}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="en",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["color"], SHARED["idiom"], DateNamed(), SHARED["date_numeric"],
                 SHARED["time_clock"], EnglishTelephone(), SHARED["money"], SHARED["percent"], SHARED["measure"],
                 Year(), Expression(), SHARED["fraction"], SHARED["range"], Ordinal(), Abbreviation(),
                 SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.COLOR: speak_color, Form.IDIOM: speak_idiom, Form.DATE: speak_date,
        Form.TIME: speak_time, Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction, Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal,
        Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
        Form.YEAR: speak_year,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER,
              Form.YEAR: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"12h", "24h"}),
        "minute_style": frozenset({"number", "phrase"}),
        "decimal_mark": frozenset({".", ","}),
        "scale": frozenset({"short"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"default_gender", "register"}),
)
