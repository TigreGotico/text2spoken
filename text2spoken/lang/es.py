"""Spanish: es-ES, the default variety, es-419, es-MX, es-AR and es-US.

Number words come from ovos-number-parser, as the speller table of design section 5.4 names it. The file adds
the agreement that the speller does not give: `uno` takes the apocope `un` before a masculine noun, and the
feminine `una` and `-ientas` before a feminine noun (Diccionario panhispánico de dudas, DPD, entry «uno», 2.2 and
2.3). It writes its own fractions, because ovos-number-parser reads `1/21` as "uno vigésimo primero" where the DPD
entry «fraccionarios» gives "un veintiunavo". It writes its own decimals, because the speller reads a float and
drops the written zero of `2,50`, and because the DLE entry «coma» (1.b) reads the decimal part as a number:
"trescientos veinticinco coma ochenta y cinco".

The varieties differ in the decimal mark (DPD «punto», 4.4), the currency of `$` (DPD, appendix 4), the reading
of the first day of the month (DPD «primero», 3) and of a whole percentage (DPD «ciento», 3).
"""
from __future__ import annotations

import re
import unicodedata
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import PHONE_PLANS, SHARED, Telephone, numbers_in, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext, Word, clause_window
from text2spoken.core.spellers import DigitSpeller, OvosNumberSpeller, bounded_integer
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import Token, is_bounded, is_word_char, next_visible
from text2spoken.lang.en import Expression
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

M, F = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
          "noviembre", "diciembre"]
"""Month names with a lowercase initial (DPD «fecha», 2.a)."""

_INITIAL = re.compile("[A-ZÁÉÍÓÚÑ][.] $")
_SCALE_NOUN = re.compile(".*(?:llón|llones|llardo|llardos)$")

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}, {"decimal": ",", "group": "."}]},
    "defaults": {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ",",
                 "scale": "long"},
    "sign_words": {"-": "menos", "+": "más"},
    "decimal_words": {",": "coma", ".": "punto"},
    "digit_words": ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"],
    "leads": {"#": "número", "-": ""},
    "fraction_names": {"2": "medio", "3": "tercio", "4": "cuarto", "5": "quinto", "6": "sexto", "7": "séptimo",
                       "8": "octavo", "9": "noveno", "10": "décimo", "100": "centésimo"},
    "range_word": "a",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"},
                    {"mark": ".", "seconds": False, "needs": "evidence"},
                    {"mark": "h", "seconds": False, "needs": "none"}],
    "time_words": ["la", "las"],
    "time_symbols": [" h", "h"],
    "day_periods": {"am": ["a. m.", "a.m."], "pm": ["p. m.", "p.m."]},
    "day_period_words": {"madrugada": "de la madrugada", "mañana": "de la mañana", "mediodía": "del mediodía",
                         "tarde": "de la tarde", "noche": "de la noche"},
    "minute_phrases": {"0": "en punto", "15": "y cuarto", "30": "y media", "45": "menos cuarto"},
    "months": MONTHS,
    "first_of_month": "cardinal",
    "currencies": {
        "EUR": {"symbols": ["€"], "one": "euro", "other": "euros", "many": "de euros", "gender": "masculine",
                "minor": {"one": "céntimo", "other": "céntimos"}},
        "USD": {"symbols": ["$", "US$"], "one": "dólar", "other": "dólares", "many": "de dólares",
                "gender": "masculine", "minor": {"one": "centavo", "other": "centavos"}},
        "GBP": {"symbols": ["£"], "one": "libra", "other": "libras", "many": "de libras", "gender": "feminine",
                "minor": {"one": "penique", "other": "peniques"}},
    },
    "scales": {"millones": "millones", "millón": "millón"},
    "percent": {"signs": ["%"], "position": "after", "word": "por ciento", "whole": "cien por cien"},
    "units": {
        "kg": {"one": "kilogramo", "other": "kilogramos", "many": "de kilogramos", "gender": "masculine"},
        "g": {"one": "gramo", "other": "gramos", "many": "de gramos", "gender": "masculine"},
        "t": {"one": "tonelada", "other": "toneladas", "many": "de toneladas", "gender": "feminine"},
        "km": {"one": "kilómetro", "other": "kilómetros", "many": "de kilómetros", "gender": "masculine"},
        "m": {"one": "metro", "other": "metros", "many": "de metros", "gender": "masculine"},
        "cm": {"one": "centímetro", "other": "centímetros", "many": "de centímetros", "gender": "masculine"},
        "mm": {"one": "milímetro", "other": "milímetros", "many": "de milímetros", "gender": "masculine"},
        "l": {"one": "litro", "other": "litros", "many": "de litros", "gender": "masculine"},
        "L": {"one": "litro", "other": "litros", "many": "de litros", "gender": "masculine"},
        "km/h": {"one": "kilómetro por hora", "other": "kilómetros por hora", "many": "de kilómetros por hora",
                 "gender": "masculine"},
        "h": {"one": "hora", "other": "horas", "many": "de horas", "gender": "feminine"},
        "min": {"one": "minuto", "other": "minutos", "many": "de minutos", "gender": "masculine"},
        "°C": {"one": "grado Celsius", "other": "grados Celsius", "many": "de grados Celsius",
               "gender": "masculine"},
        "ºC": {"one": "grado Celsius", "other": "grados Celsius", "many": "de grados Celsius",
               "gender": "masculine"},
        "°F": {"one": "grado Fahrenheit", "other": "grados Fahrenheit", "many": "de grados Fahrenheit",
               "gender": "masculine"},
        "Hz": {"one": "hercio", "other": "hercios", "many": "de hercios", "gender": "masculine"},
    },
    "dimension_marks": ["x", "×"],
    "dimension_word": "por",
    "operators": {"+": "más", "−": "menos", "×": "por", "÷": "entre", "=": "igual a"},
    "phone_words": ["teléfono", "tel", "tfno", "móvil", "celular", "llama", "llame", "llamá", "llamar", "marca",
                    "marque", "fax"],
    "phone_links": ["al", "el"],
    "short_codes": ["061", "062", "091", "092", "112", "911"],
    "list_links": ["y", "o"],
    "phone_shapes": ["6[0-9]{2} [0-9]{3} [0-9]{3}", "7[1-9][0-9] [0-9]{3} [0-9]{3}"],
    "phone_unit_shapes": ["(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "titles": {"Sr.": "señor", "Sra.": "señora", "Srta.": "señorita", "Dr.": "doctor", "Dra.": "doctora",
               "D.": "don", "D.ª": "doña", "Dña.": "doña", "Prof.": "profesor", "Prof.ª": "profesora",
               "Lic.": "licenciado", "Ing.": "ingeniero", "Gral.": "general", "Mons.": "monseñor"},
    "abbreviations": {"etc.": "etcétera", "p. ej.": "por ejemplo", "Ud.": "usted", "Uds.": "ustedes",
                      "Vd.": "usted", "Vds.": "ustedes", "pág.": "página", "págs.": "páginas", "art.": "artículo",
                      "cap.": "capítulo", "vol.": "volumen", "tel.": "teléfono", "admón.": "administración",
                      "avda.": "avenida", "Avda.": "avenida"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"n.º": "número", "N.º": "número", "núm.": "número", "nro.": "número"},
    "symbols": {"%": "percent", "$": "money", "€": "money", "£": "money", "°": "measure", "×": "measure"},
    "ordinal_marks": {"ª": "feminine", ".º": "masculine", ".ª": "feminine", ".er": "apocope",
                      ".ᵉʳ": "apocope", "er": "apocope", ".os": "masculine plural", ".as": "feminine plural"},
    "function_words": ["a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde", "durante", "en", "entre",
                       "hacia", "hasta", "para", "por", "según", "sin", "sobre", "tras", "y", "e", "o", "u", "ni",
                       "que", "pero", "sino", "porque", "como", "cuando", "si", "el", "la", "los", "las", "lo",
                       "un", "una", "unos", "unas", "se", "me", "te", "nos", "le", "les", "su", "sus", "mi", "mis",
                       "es", "son", "era", "eran", "fue", "fueron", "hay", "había", "hubo", "ha", "han", "hace",
                       "hacía", "ya", "no", "más", "menos", "muy", "también", "hoy", "ayer", "mañana", "ahora",
                       "después", "antes", "luego", "aquí", "allí", "entonces", "casi", "solo"],
    "year_words": ["en", "año", "desde", "hasta", "del"],
    "noun_gender": {"día": "masculine", "días": "masculine", "mapa": "masculine", "mapas": "masculine",
                    "problema": "masculine", "problemas": "masculine", "sistema": "masculine",
                    "sistemas": "masculine", "tema": "masculine", "temas": "masculine", "programa": "masculine",
                    "programas": "masculine", "idioma": "masculine", "idiomas": "masculine",
                    "planeta": "masculine", "planetas": "masculine", "avión": "masculine",
                    "aviones": "masculine", "camión": "masculine", "camiones": "masculine",
                    "mano": "feminine", "manos": "feminine", "foto": "feminine", "fotos": "feminine",
                    "noche": "feminine", "noches": "feminine", "calle": "feminine", "calles": "feminine",
                    "clase": "feminine", "clases": "feminine", "parte": "feminine", "partes": "feminine",
                    "vez": "feminine", "veces": "feminine", "ley": "feminine", "leyes": "feminine",
                    "mujer": "feminine", "mujeres": "feminine", "flor": "feminine", "flores": "feminine",
                    "imagen": "feminine", "imágenes": "feminine", "red": "feminine", "redes": "feminine"},
    "gender_suffixes": {"a": "feminine", "as": "feminine", "ción": "feminine", "ciones": "feminine",
                        "sión": "feminine", "siones": "feminine", "ión": "feminine", "iones": "feminine",
                        "dad": "feminine", "dades": "feminine", "tad": "feminine", "tades": "feminine",
                        "tud": "feminine", "tudes": "feminine", "umbre": "feminine", "umbres": "feminine"},
    "tonic_a": ["agua", "águila", "ala", "alma", "arma", "área", "aula", "hacha", "hambre", "hada"],
    "patterns": {"expression": "[-−+]?[0-9]+(?: ?[+−×÷=] ?[-−+]*[0-9]+)+"},
})

AMERICA = {"first_of_month": "ordinal", "percent": {"whole": "ciento por ciento"}}
"""What every American variety changes: `primero` for the first day of the month (DPD «primero», 3), and `ciento
por ciento` for a whole percentage (DPD «ciento», 3). The euro cent is `céntimo` in every variety (DPD «euro», 3)."""

VARIETIES = (
    Variety("es-ES"),
    Variety("es-419", freeze({**AMERICA, "currencies": {"USD": {"symbols": ["US$"]}}})),
    Variety("es-MX", freeze({**AMERICA, "defaults": {"decimal_mark": "."}, "currencies": {
        "USD": {"symbols": ["US$"]},
        "MXN": {"symbols": ["$"], "one": "peso", "other": "pesos", "many": "de pesos", "gender": "masculine",
                "minor": {"one": "centavo", "other": "centavos"}}}})),
    Variety("es-AR", freeze({**AMERICA, "currencies": {
        "USD": {"symbols": ["US$"]},
        "ARS": {"symbols": ["$"], "one": "peso", "other": "pesos", "many": "de pesos", "gender": "masculine",
                "minor": {"one": "centavo", "other": "centavos"}}}})),
    Variety("es-US", freeze({**AMERICA, "defaults": {"decimal_mark": "."}})),
)
"""`$` is the peso of Argentina, Chile, Mexico and Uruguay, and the dollar of the United States, Puerto Rico and
Ecuador (DPD, appendix 4). `es-419` covers both, so `$` stays as written there, and `US$` reads as the dollar."""


def feminine(words: str) -> str:
    """The feminine of a cardinal before a feminine noun: `una`, `veintiuna` and `-ientas` below the last
    `millón`, which is a masculine noun (DPD «uno», 2.3: "setecientas mil toneladas", "veintiuna toneladas")."""
    tokens = words.split()
    last_scale = max((i for i, token in enumerate(tokens) if _SCALE_NOUN.fullmatch(token)), default=-1)
    for i in range(last_scale + 1, len(tokens)):
        if tokens[i].endswith("ientos"):
            tokens[i] = tokens[i][:-2] + "as"
    if last_scale < len(tokens) - 1:
        tokens[-1] = {"uno": "una", "veintiuno": "veintiuna"}.get(tokens[-1], tokens[-1])
    return " ".join(tokens)


def apocope(words: str) -> str:
    """`un` and `veintiún` before a noun (DPD «uno», 2.2: "Tengo veintiún años")."""
    *head, last = words.split()
    last = {"uno": "un", "una": "un", "veintiuno": "veintiún", "veintiuna": "veintiún"}.get(last, last)
    return " ".join([*head, last])


def _plain(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


class SpanishSpeller:
    """ovos-number-parser cardinals and ordinals, with the agreement, decimals and fractions of this file."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({M: "masculine", F: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        words = self.ovos.cardinal(digits, Features(), request)
        return feminine(words) if features.gender is F else words

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.ordinal(digits, Features(gender=features.gender or M), request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, Features(), request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimal part reads as a number, after one `cero` for each leading zero (DLE «coma», 1.b)."""
        rest = fraction.lstrip("0")
        parts = ["cero"] * (len(fraction) - len(rest)) + ([self.cardinal(rest, Features(), request)] if rest else [])
        mark = request.data["decimal_words"][request.params.decimal_mark or request.data["defaults"]["decimal_mark"]]
        return " ".join([self.cardinal(integer or "0", Features(), request), mark, *parts])

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """The numerator as a cardinal and the denominator as a fraction noun, which is masculine (DPD
        «fraccionarios», 1 and 3: "un tercio", "dos tercios", "veintiunavo")."""
        top = apocope(self.cardinal(numerator, Features(), request))
        value = bounded_integer(denominator)
        bottom = request.data["fraction_names"].get(str(value)) if value is not None else None
        if bottom is None:
            bottom = self._avo(denominator, request)
        return f"{top} {bottom if bounded_integer(numerator) == 1 else bottom + 's'}"

    def _avo(self, denominator: str, request: Request) -> str:
        """The cardinal in one word with the suffix -avo: a final `a` merges with it, any other vowel stays, and
        `y` becomes `i` (DPD «fraccionarios», 4 and 5: "cincuentavo", "onceavo", "cincuentaiseisavo")."""
        stem = _plain(self.cardinal(denominator, Features(), request)).replace(" y ", "i").replace(" ", "")
        stem = stem[:-1] if stem.endswith("a") else stem[:-1] if stem.endswith("uno") else stem
        return stem + "avo"


SPELLER = SpanishSpeller()


def noun_gender(word: str, data) -> GrammaticalGender | None:
    """The gender of a noun from the exception table, else from its ending."""
    lower = word.lower()
    if lower in data["noun_gender"]:
        return GrammaticalGender(data["noun_gender"][lower])
    for suffix in sorted(data["gender_suffixes"], key=len, reverse=True):
        if lower.endswith(suffix):
            return GrammaticalGender(data["gender_suffixes"][suffix])
    return None


@dataclass(frozen=True)
class Agreement:
    gender: GrammaticalGender | None
    noun: str | None

    def read(self, digits: str, request: Request) -> str:
        """The cardinal before its noun: feminine, or the apocope before a masculine noun or before a feminine
        noun with a stressed /a/ (DPD «uno», 2.2 and 2.3). With no noun, the full form (DPD «ciento», 3)."""
        tonic = self.noun is not None and self.noun.lower() in request.data["tonic_a"]
        words = SPELLER.cardinal(digits, Features(gender=F if self.gender is F and not tonic else None), request)
        return apocope(words) if self.noun is not None and (self.gender is not F or tonic) else words


def _is_year(span: Span, before: Sequence[str], data) -> bool:
    digits = span.fields.get("digits", "")
    return (span.end - span.start == 4 and len(digits) == 4 and 1000 <= int(digits) <= 2099
            and bool(before) and before[-1].lower() in data["year_words"])


def agreement(span: Span, context: SpanContext) -> Agreement:
    """The hint, else the noun after the number, else the default gender of the params (design section 5.6). A
    capitalised word is a name and no counted noun, and a year after a year word counts nothing. A number other
    than 1 counts a plural noun, so a word with no final `s` after it, such as the verb in `200 pesa`, is no
    counted noun."""
    data = context.request.data
    first = context.after[0] if context.after else ""
    noun = first if first[:1].islower() and first.isalpha() and first not in data["function_words"] else None
    counted = span.fields.get("digits") or span.fields.get("high") or span.fields["numerator"]
    if noun is not None and (_is_year(span, context.before, data)
                             or (bounded_integer(counted) != 1 and not noun.endswith("s"))):
        noun = None
    if context.hint is not None and context.hint.gender is not None:
        return Agreement(context.hint.gender, noun)
    if noun is not None:
        return Agreement(noun_gender(noun, data) or M, noun)
    return Agreement(context.request.params.default_gender.get(LANGUAGE.code), None)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _plain_cardinal(digits: str, request: Request) -> str:
    return SPELLER.cardinal(digits, Features(), request)


def _amount(amount: FrozenMap, request: Request, agree: Agreement | None = None) -> str:
    """A decimal or a whole amount; a whole amount agrees with its noun."""
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    elif agree is not None:
        words = agree.read(amount["integer"] or "0", request)
    else:
        words = _plain_cardinal(amount["integer"] or "0", request)
    return _signed(words, amount["sign"], request)


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A lead word of "" stands for a space; digits with a leading zero, which only a lead admits, read one by
    one, and a number after a lead names a label, so it takes no agreement."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if fields["lead"]:
        if len(digits) > 1 and digits[0] == "0":
            words = DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)
        else:
            words = _plain_cardinal(digits, request)
        lead = request.data["leads"][fields["lead"]]
        return f"{lead} {words}" if lead else f" {words}"
    return _signed(agreement(span, context).read(digits, request), fields["sign"], request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, context.request)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """The marker gives the gender and the number: `1.º`, `1.ª`, `1.os`. `1.er` and a masculine singular ordinal
    before its noun take the apocope `primer` and `tercer` (DPD «primero», 1.a; «tercero», 1.a)."""
    request = context.request
    kind = request.data["ordinal_marks"][span.fields["marker"]]
    gender = F if kind.startswith("feminine") else M
    words = SPELLER.ordinal(span.fields["digits"], Features(gender=gender), request)
    if kind.endswith("plural"):
        return " ".join(word + "s" for word in words.split())
    first = context.after[0] if context.after else ""
    before_noun = (first[:1].islower() and first.isalpha() and first not in request.data["function_words"]
                   and not first.endswith("s") and noun_gender(first, request.data) is not F)
    if kind == "apocope" or (gender is M and before_noun):
        *head, last = words.split()
        words = " ".join([*head, {"primero": "primer", "tercero": "tercer"}.get(last, last)])
    return words


def speak_fraction(span: Span, context: SpanContext) -> str:
    """`1/2` before a noun is `medio` or `media`, which agrees with it (DPD «fraccionarios», 2: "media
    tortilla"); in other places `un medio` (DPD «fraccionarios», 3.a)."""
    fields, request = span.fields, context.request
    agree = agreement(span, context)
    if fields["numerator"] == "1" and fields["denominator"] == "2" and agree.noun is not None:
        words = "media" if agree.gender is F else "medio"
    else:
        words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), request)
    return _signed(words, fields["sign"], request)


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    high = agreement(span, context).read(span.fields["high"], request)
    return f"{_plain_cardinal(span.fields['low'], request)} {request.data['range_word']} {high}"


def _signed_operand(operand: str, request: Request) -> str:
    sign = {"−": "-"}.get(operand[0], operand[0]) if operand[0] in "-−+" else ""
    return _signed(_plain_cardinal(operand.lstrip("-−+"), request), sign, request)


def speak_expression(span: Span, context: SpanContext) -> str:
    request = context.request
    operands = span.fields["operands"]
    words = [_signed_operand(operands[0], request)]
    for operator, operand in zip(span.fields["operators"], operands[1:]):
        words += [request.data["operators"][operator], _signed_operand(operand, request)]
    return " ".join(words)


def speak_date(span: Span, context: SpanContext) -> str:
    """Day, `de`, the month name, `de`, the year (DPD «fecha», 1.a and 3.c). The first day is `uno` in Spain and
    `primero` in America (DPD «primero», 3)."""
    request = context.request
    fields = span.fields
    if fields["day"] == 1 and request.data["first_of_month"] == "ordinal":
        day = SPELLER.ordinal("1", Features(gender=M), request)
    else:
        day = _plain_cardinal(str(fields["day"]), request)
    month = request.data["months"][fields["month"] - 1]
    return f"{day} de {month} de {SPELLER.year(str(fields['year']), Features(), request)}"


def _day_period(hour: int) -> str:
    """The part of the day of a 24-hour hour (DPD «hora», 2.1 and 2.1.2). The DPD bounds the afternoon and the
    night by sunset; this file puts that bound at 20:00."""
    if hour == 0 or hour >= 20:
        return "noche"
    if hour <= 5:
        return "madrugada"
    if hour <= 11:
        return "mañana"
    return "mediodía" if hour == 12 else "tarde"


def _hour(hour: int, request: Request) -> str:
    """An hour is feminine, as `la una`, `las veintiuna` (DPD «hora», 5.2)."""
    return SPELLER.cardinal(str(hour), Features(gender=F), request)


def speak_time(span: Span, context: SpanContext) -> str:
    """The 24-hour model reads the hour and the minutes as numbers: "las once treinta horas" for `11:30 h`, and
    the symbol `h` reads `horas` except after `la una` (DPD «hora», 5.4). A full hour reads `horas`: "a las
    diecinueve horas" (DPD «hora», 3.d).

    A written `a. m.` or `p. m.`, or `minute_style="phrase"`, gives the 12-hour model of DPD «hora», 2.1: `y
    cuarto`, `y media`, `menos cuarto`, `y diez`, `menos veinte`, and the part of the day."""
    request = context.request
    data = request.data
    fields = span.fields
    hour, minute, period = fields["hour"], fields["minute"], fields["period"]
    if period is None and request.params.minute_style != "phrase":
        words = [_hour(hour, request)]
        if minute:
            words.append(_plain_cardinal(str(minute), request) if minute >= 10
                         else f"cero {_plain_cardinal(str(minute), request)}")
        if hour != 1 and (fields["suffix"] or not minute):
            words.append("horas")
        return " ".join(words)
    day_hour = hour if period is None else hour % 12 + (12 if period == "pm" else 0)
    face = twelve_hour(day_hour)
    phrase = data["minute_phrases"].get(str(minute))
    if minute == 0:
        words = [_hour(face, request)] if period is not None else [_hour(face, request), phrase]
    elif minute <= 30:
        words = [_hour(face, request), phrase or f"y {_plain_cardinal(str(minute), request)}"]
    else:
        words = [_hour(twelve_hour(day_hour + 1), request),
                 phrase or f"menos {_plain_cardinal(str(60 - minute), request)}"]
    if period is not None or day_hour == 0 or day_hour >= 13:
        words.append(data["day_period_words"][_day_period(day_hour)])
    return " ".join(words)


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount agrees with the currency, "veintiún euros", "veintiuna libras". Two decimals are the minor
    unit, after `con`. A scale word takes `de` before the currency: "un millón de euros" (DLE «millón», 1.a)."""
    request = context.request
    fields = span.fields
    currency = request.data["currencies"][fields["currency"]]
    agree = Agreement(GrammaticalGender(currency["gender"]), currency["other"])
    amount = FrozenMap({**fields["amount"], "sign": ""})
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        amount = FrozenMap({**amount, "fraction": fraction.rstrip("0")})
        words = f"{_amount(amount, request, Agreement(M, scale))} {scale} de {currency['other']}"
    elif len(fraction) == 2:
        major = f"{agree.read(integer, request)} {currency[plural_category(request, integer)]}"
        cents = str(int(fraction))
        minor = f"{Agreement(M, 'centavo').read(cents, request)} {currency['minor'][plural_category(request, cents)]}"
        if int(fraction) == 0:
            words = major
        else:
            words = minor if bounded_integer(integer) == 0 else f"{major} con {minor}"
    else:
        words = f"{_amount(amount, request, agree)} {currency[plural_category(request, _written(amount))]}"
    return _signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The last amount agrees with the unit: "treinta y un kilos", "veintiuna toneladas" (DPD «uno», 2.3)."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]]
    words = unit[plural_category(request, _written(amounts[-1]))]
    agree = Agreement(GrammaticalGender(unit["gender"]), words)
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    read = [_amount(a, request) for a in amounts[:-1]] + [_amount(amounts[-1], request, agree)]
    return f"{f' {link} '.join(read)} {words}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """`por ciento` after the full number, "el treinta y uno por ciento"; a whole is `cien por cien` in Spain
    and `ciento por ciento` in America (DPD «ciento», 3)."""
    request = context.request
    amount = span.fields["amount"]
    percent = request.data["percent"]
    if amount["integer"] == "100" and not amount["fraction"] and not amount["sign"]:
        return percent["whole"]
    return f"{_amount(amount, request)} {percent['word']}"


def speak_telephone(span: Span, context: SpanContext) -> str:
    request = context.request
    digit_words = DigitSpeller(request.data["digit_words"])
    groups = [digit_words.cardinal(group, Features(), request) for group in span.fields["groups"]]
    if span.fields["country_code"]:
        groups.insert(0, f"{request.data['sign_words']['+']} "
                         f"{digit_words.cardinal(span.fields['country_code'], Features(), request)}")
    return " ".join(groups)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """An abbreviation reads as the full word (DPD «abreviatura», 3). A title abbreviation has a capital, while
    the word is lowercase (DPD «abreviatura», 8.c), so the word takes a capital only where a clause starts. Any
    other abbreviation keeps the case of its first letter."""
    data = context.request.data
    key = span.fields["key"]
    for table in ("titles", "abbreviations", "number_abbreviations"):
        word = data[table].get(key)
        if word is not None:
            capital = not context.before if table == "titles" else key[0].isupper()
            return word[0].upper() + word[1:] if capital else word
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


@dataclass(frozen=True)
class Clock:
    """The shared clock recognizer, with the symbol `h` after the time as evidence, as in `17:30 h` (DPD «hora»,
    4.c). The symbol joins the span when a space or the time itself comes before it and no letter after it."""
    name: str = "time_clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        clock = SHARED["time_clock"]
        spans = {span.start: span for span in clock.find(text, tokens, request)}
        symbols = Variety(request.variety.tag,
                          FrozenMap({**request.variety.data, "time_suffixes": request.data["time_symbols"]}))
        with_symbol = Request(request.tag, symbols, request.language, request.params, request.memo)
        for span in clock.find(text, tokens, with_symbol):
            if span.fields["suffix"] or span.start not in spans:
                spans[span.start] = span
        return iter(sorted(spans.values(), key=lambda span: span.start))


class SpanishTelephone(Telephone):
    """The shared telephone recognizer, where an article may stand between the phone word and the run, as in
    `Llama al 112.`, and a phone word up to three words back names a run with the shape of a phone number."""

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        index = bisect_right(words, start, key=lambda word: word.end)
        return range(index - len(clause_window(text, words, start, end, -1, limit=3, breaks=breaks)), index)

    def names_back(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
                   shaped: bool, short_code: bool, request: Request) -> bool:
        before = clause_window(text, words, start, end, -1, limit=2, breaks=breaks)
        linked = (len(before) == 2 and before[1].lower() in request.data["phone_links"]
                  and before[0].lower() in request.data["phone_words"])
        return shaped or linked


@dataclass(frozen=True)
class Ordinal:
    """`1.º`, `2.ª`, `1.er`, `3.os`: a whole number and a marker of the `ordinal_marks` table (DPD «abreviatura»,
    5.b: `n.º`, letters written high). `1ª` and `3er` with no full stop are common, and their marker tells the
    ordinal apart. A bare `º`, as in `25º`, is also written for a degree, so it stays as written."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = sorted(request.data["ordinal_marks"], key=len, reverse=True)
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None or (number.start and is_word_char(text[number.start - 1])):
                continue
            marker = next((m for m in marks if text.startswith(m, number.end)), None)
            if marker is None or not is_bounded(text, number.start, number.end + len(marker)):
                continue
            yield Span(number.start, number.end + len(marker), Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, `n.º` before a number, and the abbreviations of the table (DPD,
    appendix 2). `D.` after an initial, as in `J. D. Salinger`, is an initial too."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        tables = (("titles", str.isupper), ("number_abbreviations", str.isdigit), ("abbreviations", lambda _: True))
        final = frozenset(data["sentence_final"])
        for table, follows in tables:
            for key in sorted(data[table], key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    initial = table == "titles" and _INITIAL.search(text, 0, position) is not None
                    if is_bounded(text, position, end) and follows(following) and not initial:
                        sentence_end = key in final and (following == "" or following.isupper())
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}),
                                   trail="." if sentence_end else "", recognizer=self.name)
                    position = text.find(key, end)


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """Spanish declares no proclitic and no case ending. The one suffix is the time symbol `h`, which the time
    verbalizer reads."""
    return spoken


LANGUAGE = LanguageSpec(
    code="es",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["date_numeric"], Clock(), SpanishTelephone(), SHARED["money"],
                 SHARED["percent"], SHARED["measure"], Expression(), SHARED["fraction"], SHARED["range"], Ordinal(),
                 Abbreviation(), SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time,
        Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    attach=attach,
    genders=frozenset({M, F}),
    default_gender=M,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"24h"}),
        "minute_style": frozenset({"number", "phrase"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long"}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"register"}),
)
