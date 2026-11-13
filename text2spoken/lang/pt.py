"""Portuguese: pt-PT, the default variety, and pt-BR. Every other `pt-*` tag reads the variety that
`linguatag.closest_lang` gives it, so `pt-AO` and `pt-MZ` read pt-PT.

Number words come from ovos-number-parser (design section 5.4), read with the variety tag. pt-PT follows the
official norm: the long scale (Priberam, "bilião": "Um milhão de milhões"), "dezanove" (Priberam, "dezanove":
"Grafia no Brasil: dezenove"), and lowercase month names (AO1990, Base XIX, 1.º b).

A number agrees with the noun that it counts. The hint of a frontend decides first, then the noun after the
number, then a determiner before it, then `default_gender`. `um`, `dois` and the hundreds from `duzentos` have a
feminine form; a scale word from `milhão` up is a masculine noun, so the words before it stay masculine (Priberam,
"duas": "uma mesa e duas cadeiras"; "uma": "Flexão feminina de um"; "milhão": "nome masculino").

The gender of a common noun comes from the noun lexicon of `tugalex`, behind the `pt` extra (design section 16).
Without the extra, the `noun_gender` table and the endings of `gender_suffixes` give it.
"""
from __future__ import annotations

import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import Money as CoreMoney
from text2spoken.core.recognizers import PHONE_PLANS, SHARED, Telephone, TimeClock, digit_run_matches, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext, Word, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import DigitSpeller, OvosNumberSpeller, bounded_integer
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import Token, digit_script, fold_digits, is_bounded, next_visible, one_digit_set
from text2spoken.errors import DeclinedReading
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

MASCULINE, FEMININE = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE
_SIGNS = "-−+"

MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
          "novembro", "dezembro"]
_MONTH = "(" + "|".join(f"[{m[0]}{m[0].upper()}]{m[1:]}" for m in MONTHS) + ")"

UNITS_PT = {
    "kg": {"one": "quilograma", "many": "de quilogramas", "other": "quilogramas"},
    "g": {"one": "grama", "many": "de gramas", "other": "gramas"},
    "km": {"one": "quilómetro", "many": "de quilómetros", "other": "quilómetros"},
    "m": {"one": "metro", "many": "de metros", "other": "metros"},
    "cm": {"one": "centímetro", "many": "de centímetros", "other": "centímetros"},
    "mm": {"one": "milímetro", "many": "de milímetros", "other": "milímetros"},
    "km/h": {"one": "quilómetro por hora", "many": "de quilómetros por hora", "other": "quilómetros por hora"},
    "l": {"one": "litro", "many": "de litros", "other": "litros"},
    "ml": {"one": "mililitro", "many": "de mililitros", "other": "mililitros"},
    "°C": {"one": "grau Celsius", "many": "de graus Celsius", "other": "graus Celsius"},
}
"""SI symbols and the Portuguese unit names. Each unit name is a masculine noun (Priberam, "quilograma", "grama",
"litro", "grau": "nome masculino"), so a number before it reads in the masculine."""

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}, {"decimal": ".", "group": ","}]},
    "sign_words": {"-": "menos", "+": "mais"},
    "digit_words": ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"],
    "leads": {"#": "número", "-": ""},
    "range_word": "a",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"},
                    {"mark": "h", "seconds": False, "needs": "none", "closes_hour": True}],
    "time_words": ["às", "as", "à", "pelas", "das", "até", "desde"],
    "time_suffixes": ["h"],
    "time_units": {"h": {"one": "hora", "other": "horas"}, "min": {"one": "minuto", "other": "minutos"},
                   "s": {"one": "segundo", "other": "segundos"}},
    "range_articles": {"da": {"one": "à", "other": "às"}, "das": {"one": "à", "other": "às"}},
    "day_periods": {"am": ["a.m."], "pm": ["p.m."]},
    "dimension_marks": ["x", "×"],
    "dimension_word": "por",
    "operators": {"+": "mais", "−": "menos", "×": "vezes", "=": "igual a"},
    "months": MONTHS,
    "currencies": {
        "EUR": {"symbols": ["€"], "one": "euro", "many": "de euros", "other": "euros",
                "minor": {"one": "cêntimo", "other": "cêntimos"}},
        "BRL": {"symbols": ["R$"], "one": "real", "many": "de reais", "other": "reais",
                "minor": {"one": "centavo", "other": "centavos"}},
        "USD": {"symbols": ["US$", "$"], "one": "dólar", "many": "de dólares", "other": "dólares",
                "minor": {"one": "cêntimo", "other": "cêntimos"}},
    },
    "scales": {"mil": "mil", "milhão": "milhão de", "milhões": "milhões de", "bilhão": "bilhão de",
               "bilhões": "bilhões de", "bilião": "bilião de", "biliões": "biliões de"},
    "symbols_before_only": ["$"],
    "percent": {"signs": ["%"], "position": "after", "word": "por cento"},
    "fraction_names": {"2": "meio", "3": "terço", "4": "quarto", "5": "quinto", "6": "sexto", "7": "sétimo",
                       "8": "oitavo", "9": "nono", "10": "décimo", "100": "centésimo"},
    "fraction_word": "avos",
    "units": UNITS_PT,
    "phone_words": ["telefone", "tel", "telemóvel", "telemóveis", "ligue", "ligar", "liga", "telefona", "fax",
                    "contacto", "contato", "celular"],
    "short_codes": ["112", "190", "192", "193", "199"],
    "list_links": ["e", "ou"],
    "phone_shapes": ["[(][1-9][0-9][)] 9?[0-9]{4}-[0-9]{4}"],
    "phone_unit_shapes": ["[29][0-9]{2} [0-9]{3} [0-9]{3}"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "function_words": ["o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos",
                       "nas", "para", "pelo", "pela", "por", "e", "ou", "com", "ao", "que", "agora", "já", "hoje"],
    "color_words": ["cor", "cores"],
    "colors": {"000000": "preto", "0000ff": "azul", "008000": "verde", "ff0000": "vermelho", "ffff00": "amarelo",
               "ffffff": "branco"},
    "titles": {"Sr.": "Senhor", "Dr.": "Doutor", "Dra.": "Doutora", "Prof.": "Professor", "Eng.": "Engenheiro"},
    "abbreviations_any_case": ["sr.", "dr.", "dra.", "prof.", "eng."],
    "honorific_before_name": {"D.": {"masculine": "Dom", "feminine": "Dona"}},
    "abbreviations": {"Av.": "Avenida", "av.": "avenida", "etc.": "et cetera"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"n.º": "número", "N.º": "Número"},
    "ordinal_marks": {"º": "masculine", "ª": "feminine"},
    "regnal_titles": ["D", "Dom", "Dona", "rei", "rainha", "papa", "imperador", "imperatriz", "príncipe",
                      "princesa", "infante", "infanta"],
    "century_words": ["século", "séculos"],
    "determiners": {"as": "feminine", "das": "feminine", "nas": "feminine", "pelas": "feminine", "às": "feminine",
                    "à": "feminine", "os": "masculine", "dos": "masculine", "nos": "masculine", "pelos": "masculine"},
    "noun_gender": {
        "dia": "masculine", "dias": "masculine", "mapa": "masculine", "mapas": "masculine",
        "problema": "masculine", "problemas": "masculine", "sistema": "masculine", "sistemas": "masculine",
        "programa": "masculine", "programas": "masculine", "tema": "masculine", "temas": "masculine",
        "grama": "masculine", "gramas": "masculine", "quilograma": "masculine", "quilogramas": "masculine",
        "lei": "feminine", "leis": "feminine", "vez": "feminine", "vezes": "feminine", "noite": "feminine",
        "noites": "feminine", "tarde": "feminine", "tardes": "feminine", "parte": "feminine", "partes": "feminine",
        "mulher": "feminine", "mulheres": "feminine", "flor": "feminine", "flores": "feminine",
        "Isabel": "feminine", "Leonor": "feminine", "Beatriz": "feminine", "Inês": "feminine",
    },
    "gender_suffixes": [["dade", "feminine"], ["dades", "feminine"], ["agem", "feminine"], ["agens", "feminine"],
                        ["ção", "feminine"], ["ções", "feminine"], ["a", "feminine"], ["as", "feminine"]],
    "symbols": {"%": "percent", "€": "money", "$": "money", "°": "measure", "×": "measure"},
    "patterns": {
        "date_named": "([0-9][0-9]?) de " + _MONTH + "(?: de ([0-9][0-9][0-9][0-9]))?",
        "expression": "[-−+]?[0-9]+(?: ?[+−×=] ?[-−+]*[0-9]+)+",
    },
})

DEFAULTS = {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ","}

VARIETIES = (
    Variety("pt-PT", freeze({"defaults": {**DEFAULTS, "scale": "long"},
                             "colors": {"808080": "cinzento"}})),
    Variety("pt-BR", freeze({
        "defaults": {**DEFAULTS, "scale": "short"},
        "colors": {"808080": "cinza"},
        "currencies": {"USD": {"minor": {"one": "centavo", "other": "centavos"}}},
        "units": {unit: {category: word.replace("ómetro", "ômetro") for category, word in forms.items()}
                  for unit, forms in UNITS_PT.items()},
    })),
)

_SCALE_WORD = re.compile("[a-z]+(?:ão|ões)")


def at_variety(request: Request) -> Request:
    """The request with the tag of its variety, so that `pt-US`, which reads pt-BR, gets the Brazilian words and
    plural rules, and `pt-AO` gets those of pt-PT."""
    return request if request.tag == request.variety.tag else replace(request, tag=request.variety.tag)


class PortugueseSpeller:
    """ovos-number-parser, read with the variety tag and the gender of the noun."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.ovos.cardinal(digits, Features(gender=gender), at_variety(request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """From 2000 up, the first element is a cardinal: `2022.º` reads `dois milésimo vigésimo segundo`
        (Teyssier, Manual de Língua Portuguesa, p. 183, as the owner of ovos-number-parser reports it)."""
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.ovos.ordinal(digits, Features(gender=gender), at_variety(request))

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, Features(), request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        return self.ovos.decimal(integer, fraction, Features(), at_variety(request))

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """`um meio`, `três quartos`, `um centésimo`, and the cardinal and `avos` for any other denominator:
        `dois onze avos` (Ciberdúvidas 11493, after Cunha and Cintra). A field with a leading zero, as in `01/02`,
        may be a day and a month, so the fraction stays as written."""
        if numerator.startswith("0") or denominator.startswith("0"):
            raise DeclinedReading("a fraction with a leading zero may be a day and a month")
        top = self.cardinal(numerator, Features(), request)
        name = request.data["fraction_names"].get(denominator)
        if name is None:
            return f"{top} {self.cardinal(denominator, Features(), request)} {request.data['fraction_word']}"
        return f"{top} {name if numerator == '1' else name + 's'}"


SPELLER = PortugueseSpeller()


def _cardinal(digits: str, request: Request, gender: GrammaticalGender | None = None) -> str:
    return SPELLER.cardinal(digits, Features(gender=gender), request)


def _plural(request: Request, written: str) -> str:
    return plural_category(at_variety(request), written)


def _counted(forms: FrozenMap, request: Request, written: str) -> str:
    """The word of `forms` for the plural category of the written number: `hora` or `horas`."""
    return forms.get(_plural(request, written), forms["other"])


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _amount(amount: FrozenMap, request: Request) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    else:
        words = _cardinal(amount["integer"] or "0", request)
    return _signed(words, amount["sign"], request)


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


_LEXICON_GENDERS = {"m": "masculine", "f": "feminine"}
_PARTITIVES = ("das", "dos")


def _lexicon_gender(word: str) -> str | None:
    """The gender code that `tugalex` gives a word read as a common noun: "m", "f", "mf" for a noun of two genders,
    or None when tugalex does not know the word or is not installed."""
    try:
        from tugalex import TugaLexicon
    except ImportError:
        return None
    return TugaLexicon.get_noun_gender(word)


def _gender_of(word: str, request: Request) -> GrammaticalGender | None:
    """The gender of a noun or a given name: the `noun_gender` table, then the endings of `gender_suffixes`."""
    data = request.data
    if word in data["function_words"]:
        return None
    entry = data["noun_gender"].get(word) or data["noun_gender"].get(word.lower())
    if entry is not None:
        return GrammaticalGender(entry)
    for suffix, gender in data["gender_suffixes"]:
        if word.lower().endswith(suffix):
            return GrammaticalGender(gender)
    return None


def agreement(context: SpanContext) -> GrammaticalGender:
    """The gender of a number (design section 5.6): the hint, the noun after the number, a determiner before it,
    then the `default_gender` of the params, then the language default.

    A written `mil` after the number is not the noun: `mil` has two genders (Priberam, "mil": "quantificador
    numeral cardinal de dois géneros"), so `2 mil pessoas` takes the gender of `pessoas`, as `2000 pessoas` does. A
    partitive `das` or `dos` right after the number gives the gender, as in `1 das casas`.

    The `noun_gender` table names a noun first. When tugalex knows the word after the number, a determiner comes
    before the answer of tugalex, because tugalex reads any word as a noun ("The caller decides whether the word is
    a noun"), and that word can be an adjective with no noun, as in `as 2 melhores`. A noun of two genders, such as
    `artista` (Priberam: "nome de dois géneros"), takes its gender from the determiner or the default. Without
    tugalex, the endings of `gender_suffixes` come before the determiner."""
    if context.hint is not None and context.hint.gender is not None:
        return context.hint.gender
    request = context.request
    data = request.data
    after = list(context.after)
    if after and after[0].lower() == "mil":
        after = after[1:]
    noun = after[0] if after else ""
    if noun.lower() in _PARTITIVES:
        return GrammaticalGender(data["determiners"][noun.lower()])
    determiner = data["determiners"].get(context.before[-1].lower()) if context.before else None
    listed = data["noun_gender"].get(noun) or data["noun_gender"].get(noun.lower())
    code = _lexicon_gender(noun) if noun and listed is None and noun not in data["function_words"] else None
    if code is None:
        found = _gender_of(noun, request) if noun else None
        gender = found or (GrammaticalGender(determiner) if determiner else None)
    else:
        name = determiner or _LEXICON_GENDERS.get(code)
        gender = GrammaticalGender(name) if name else None
    return gender or request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal that agrees with its noun, with the sign and lead words of the data. A lead word of "" stands for
    a space. Digits with a leading zero, which only a lead admits, read one by one. A reading that ends in a scale
    word from `milhão` up takes `de` before the noun, because the scale word is a noun (Priberam, "milhão": "nome
    masculino"): `um milhão de pessoas`."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)
    else:
        words = _cardinal(digits, request, agreement(context))
        if _SCALE_WORD.fullmatch(words.split()[-1]) and context.after \
                and context.after[0].lower() not in request.data["function_words"]:
            words += " de"
    words = _signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """`1.º` and `1.ª`: the indicator gives the gender."""
    marker = span.fields["marker"][-1]
    gender = GrammaticalGender(context.request.data["ordinal_marks"][marker])
    return SPELLER.ordinal(span.fields["digits"], Features(gender=gender), context.request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """`um meio`, `três quartos`, `três onze avos` (Priberam, "avo": "doze vinte e cinco avos = 12/25")."""
    fields = span.fields
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request)
    return _signed(words, fields["sign"], context.request)


def _range_word(before: Sequence[str], high: str, request: Request) -> str:
    """`às` or `à` after `das` or `da` names the end of a span of time with its article, as in `das cinco às seis
    horas`. With no article before the range, `a` stays (Ciberdúvidas 22241: "de cinco a seis horas")."""
    articles = request.data["range_articles"].get(before[-1].lower()) if before else None
    return _counted(articles, request, high) if articles is not None else request.data["range_word"]


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    gender = agreement(context)
    low, high = (_cardinal(span.fields[end], request, gender) for end in ("low", "high"))
    hours = request.data["time_units"]["h"].values()
    of_hours = bool(context.after) and context.after[0] in hours
    word = _range_word(context.before, span.fields["high"], request) if of_hours else request.data["range_word"]
    return f"{low} {word} {high}"


def _day(day: int, request: Request) -> str:
    """The first day of a month reads `primeiro`, and every other day a cardinal. Ciberdúvidas 32700 gives this
    rule, paraphrasing Cunha and Cintra, Nova Gramática do Português Contemporâneo, p. 374: in the days of the
    month the cardinals are used, except for the first day, where the ordinal is the rule. A written `1.º` is an
    ordinal span."""
    if day == 1:
        return SPELLER.ordinal("1", Features(gender=MASCULINE), request)
    return _cardinal(str(day), request)


def speak_date(span: Span, context: SpanContext) -> str:
    request = context.request
    fields = span.fields
    words = [_day(fields["day"], request), "de",
             request.data["months"][fields["month"] - 1]]
    if fields["year"] is not None:
        words += ["de", SPELLER.year(str(fields["year"]), Features(), request)]
    return " ".join(words)


def speak_time(span: Span, context: SpanContext) -> str:
    """`catorze e trinta` for `14:30`, `catorze horas`, `uma hora`. The hour counts `hora`, a feminine noun
    (Priberam, "hora"). A time that writes the hour symbol `h` reads its units, so `17h30` reads `dezassete horas e
    trinta minutos` (Ciberdúvidas 14648; Ciberdúvidas 3267: "às onze horas e trinta minutos"). Seconds read as in
    Ciberdúvidas 14586: "em 20 h 30 m 24 s, é claro que se quer dizer vinte horas, trinta minutos e vinte e quatro
    segundos". A written `a.m.` or
    `p.m.` gives the hour of the 24-hour clock (Priberam, "a.m.": "antes do meio-dia"; "p.m.": "depois do
    meio-dia")."""
    request = context.request
    fields = span.fields
    units = request.data["time_units"]
    hour, minute = fields["hour"], fields["minute"]
    if fields["period"] is not None:
        hour = hour % 12 + (12 if fields["period"] == "pm" else 0)
    hour_words = _cardinal(str(hour), request, FEMININE)
    second = fields["second"]
    if minute == 0 and not second:
        return f"{hour_words} {_counted(units['h'], request, str(hour))}"
    if not fields["suffix"]:
        return f"{hour_words} e {_cardinal(str(minute), request)}"
    parts = [f"{hour_words} {_counted(units['h'], request, str(hour))}"]
    for value, unit in ((minute, "min"), (second, "s")):
        if value:
            parts.append(f"{_cardinal(str(value), request)} {_counted(units[unit], request, str(value))}")
    return ", ".join(parts[:-1]) + " e " + parts[-1]


def speak_money(span: Span, context: SpanContext) -> str:
    """Two decimals are the minor unit: `dois euros e cinquenta cêntimos`. A scale word that the text writes reads
    before the plural name: `dois milhões de reais`."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = request.data["currencies"][fields["currency"]]
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        words = f"{_amount(amount, request)} {request.data['scales'][fields['scale']]} {currency['other']}"
    elif len(fraction) == 2:
        major = f"{_cardinal(integer, request)} {currency[_plural(request, integer)]}"
        cents = str(int(fraction))
        minor = f"{_cardinal(cents, request)} {currency['minor'][_plural(request, cents)]}"
        if int(fraction) == 0:
            words = major
        else:
            words = minor if bounded_integer(integer) == 0 else f"{major} e {minor}"
    else:
        words = f"{_amount(amount, request)} {currency[_plural(request, _written(amount))]}"
    return _signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]][_plural(request, _written(amounts[-1]))]
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    joined = f" {link} ".join(_amount(a, request) for a in amounts)
    return f"{joined} {unit}"


def speak_percent(span: Span, context: SpanContext) -> str:
    request = context.request
    return f"{_amount(span.fields['amount'], request)} {request.data['percent']['word']}"


def _signed_operand(operand: str, request: Request) -> str:
    sign = {"−": "-"}.get(operand[0], operand[0]) if operand[0] in _SIGNS else ""
    return _signed(_cardinal(operand.lstrip(_SIGNS), request), sign, request)


def speak_expression(span: Span, context: SpanContext) -> str:
    """Each operand may carry a sign: `-2+3=1` reads `menos dois mais três igual a um`."""
    request = context.request
    operands = span.fields["operands"]
    words = [_signed_operand(operands[0], request)]
    for operator, operand in zip(span.fields["operators"], operands[1:]):
        words += [request.data["operators"][operator], _signed_operand(operand, request)]
    return " ".join(words)


def _digits(digits: str, request: Request) -> str:
    return DigitSpeller(request.data["digit_words"]).cardinal(digits, Features(), request)


def speak_telephone(span: Span, context: SpanContext) -> str:
    request = context.request
    groups = [_digits(group, request) for group in span.fields["groups"]]
    if span.fields["country_code"]:
        groups.insert(0, f"{request.data['sign_words']['+']} {_digits(span.fields['country_code'], request)}")
    return " ".join(groups)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """A title keeps the case of the written form: `Dr.` reads `Doutor`, and `dr.` reads `doutor`. `D.` reads `Dom`
    or `Dona` by the gender of the name after it (Priberam, "D.": "Abreviatura de dom e de dona")."""
    data = context.request.data
    key = span.fields["key"]
    honorific = data["honorific_before_name"].get(key)
    if honorific is not None:
        name = context.after[0] if context.after else ""
        return honorific[str(_gender_of(name, context.request) or MASCULINE)]
    titles = {**data["titles"], **{k.lower(): v.lower() for k, v in data["titles"].items()
                                   if k.lower() in data["abbreviations_any_case"]}}
    for table in (titles, data["abbreviations"], data["number_abbreviations"]):
        if table.get(key) is not None:
            return table[key]
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


def speak_roman(span: Span, context: SpanContext) -> str:
    """Ordinal to ten and cardinal from eleven (Ciberdúvidas 14167, for kings and popes; 12370, for centuries).
    After a name, the ordinal agrees with the name and the reading takes a capital, as the name does."""
    request = context.request
    value = str(span.fields["value"])
    before = context.before[-1] if context.before else ""
    if before.lower() in request.data["century_words"]:
        gender, capital = MASCULINE, False
    else:
        gender, capital = _gender_of(before, request) or MASCULINE, True
    if span.fields["role"] == "ordinal":
        words = SPELLER.ordinal(value, Features(gender=gender), request)
    else:
        words = _cardinal(value, request)
    return words[0].upper() + words[1:] if capital else words


def speak_color(span: Span, context: SpanContext) -> str:
    """A colour with no name spells its digits as the text writes them."""
    request = context.request
    name = request.data["colors"].get(span.fields["rgb"])
    if name is not None:
        return name
    return " ".join(_digits(c, request) if c.isdigit() else c.upper() for c in span.fields["hex"])


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """Portuguese declares no proclitic and no case ending. Its one suffix is the `h` of `14:30h`, which the time
    reading already says, so it adds no word."""
    return spoken


class PortugueseTelephone(Telephone):
    """The shared telephone recognizer, where a phone word also names a run up to three words back, and a function
    word does not count, as in `Ligue para o 112.` The window names a run with the shape of a phone number, and a
    short code that ends its clause or that a function word follows. Two years that a dash joins have no phone
    shape (`no_phone_shapes`), so `Os telemóveis de 2010-2020` reads a range."""

    def window(self, text: str, words: Sequence[Word], breaks: Sequence[int], start: int, end: int,
               request: Request) -> range:
        function_words = frozenset(request.data["function_words"])
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
        function_words = frozenset(request.data["function_words"])
        following = clause_window(text, words, start, end, 1, limit=1, breaks=breaks)
        return all(word.lower() in function_words for word in following)


@dataclass(frozen=True)
class Clock(TimeClock):
    """The times of the core, and two Portuguese forms that it leaves. One is the unit symbols `h`, `min` and `s`
    around the digits, spaced or not: `17 h`, `17h30 min`, `17h30min`, `17:30 h` (Ciberdúvidas 14648: "17h30 min";
    "Considero perfeitamente aceitável 17:30 h") and `17 h 34 min 25 s` (Ciberdúvidas 3267). The other is two times
    that a range mark joins, as in `das 9h-17h` and `das 9:00-17:00`, where the second time takes the article of the
    first (Ciberdúvidas 22241: "das cinco às seis horas"). A chain of three times or more stays as written. A time
    that writes `h` keeps it in the `suffix` field, so it reads its units."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        own = list(self._ranges(text, tokens, request))
        for span in self._symbols(text, request):
            if not any(span.start < other.end and other.start < span.end for other in own):
                own.append(span)
        for span in super().find(text, tokens, request):
            if not any(span.start < other.end and other.start < span.end for other in own):
                own.append(self._with_symbol(span, text))
        yield from sorted(own, key=lambda span: span.start)

    @staticmethod
    def _with_symbol(span: Span, text: str) -> Span:
        if span.fields["suffix"] or "h" not in text[span.start:span.end]:
            return span
        return replace(span, fields=FrozenMap({**span.fields, "suffix": "h"}))

    def _time(self, start: int, hour: str, minute: str | None, symbol: str, second: str | None = None) -> Span | None:
        fields = clock_fields(hour, minute or "00", second)
        if fields is None:
            return None
        return Span(start, start, Form.TIME, FrozenMap({"hour": fields[0], "minute": fields[1], "second": fields[2],
                                                        "period": None, "suffix": symbol}), recognizer=self.name)

    def _symbols(self, text: str, request: Request) -> Iterator[Span]:
        """`17 h`, `17h30 min`, `17h 30min`, `17 h 34 min 25 s` and `17:30 h`. Minutes after a space take `min`.
        The core reads `17h`, `17h30` and `17:30h`, so they are left to it."""
        hour, minute, second = (re.escape(unit) + "(?![^\\W\\d_])" for unit in ("h", "min", "s"))
        minutes = f"(?:([0-9][0-9])(?: ?{minute})?| ([0-9][0-9]) ?{minute})(?: ([0-9][0-9]) ?{second})?"
        pattern = re.compile(f"([0-9][0-9]?)(?: ?{hour}(?:{minutes})?|:([0-9][0-9]) {hour})")
        core_form = re.compile(f"[0-9][0-9]?{hour}(?:[0-9][0-9])?")
        for match in pattern.finditer(text):
            h, glued, spaced, seconds, colon = match.groups()
            if core_form.fullmatch(match.group()) or not is_bounded(text, *match.span()):
                continue
            if span := self._time(match.start(), h, glued or spaced or colon, "h", seconds):
                yield replace(span, end=match.end())

    def _ranges(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        time = "([0-9][0-9]?)(?:h([0-9][0-9])?|:([0-9][0-9]))"
        marks = "|".join(map(re.escape, data["range_marks"]))
        words = context_words(tokens)
        time_words = frozenset(word.lower() for word in data["time_words"])
        pair = re.compile(f"{time}(?:{marks}){time}")
        for chain in re.finditer(f"{time}(?:(?:{marks}){time})+", text):
            if not is_bounded(text, *chain.span()):
                continue
            match = pair.fullmatch(text, *chain.span())
            if match is None:
                h, m, c = re.match(time, text[chain.start():]).groups()
                if first := self._time(chain.start(), h, m or c, "h" if c is None else ""):
                    yield replace(first, end=chain.end(), keep=True)
                continue
            h1, m1, c1, h2, m2, c2 = match.groups()
            before = clause_window(text, words, match.start(), match.end(), -1, limit=1)
            glued = c1 is None or c2 is None
            if not glued and not (before and before[0].lower() in time_words):
                continue
            first = self._time(match.start(), h1, m1 or c1, "h" if c1 is None else "")
            second_start = match.start(4)
            second = self._time(second_start, h2, m2 or c2, "h" if c2 is None else "")
            if first is None or second is None:
                continue
            word = _range_word(before, str(second.fields["hour"]), request)
            yield replace(first, end=second_start, trail=f" {word} ")
            yield replace(second, end=match.end())


@dataclass(frozen=True)
class Money(CoreMoney):
    """The money of the core. A `$` after the number is the cifrão of the escudo, which Portugal wrote to the right
    of the digits (Priberam, "cifrão": "antes do euro, indicava escudos, e escrevia-se à direita do algarismo"), so
    `100$` stays as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        before_only = request.data["symbols_before_only"]
        for span in super().find(text, tokens, request):
            symbol = span.fields["written_symbol"]
            written = text[span.start:span.end]
            first_digit = next(index for index, char in enumerate(written) if char.isdigit())
            yield replace(span, keep=True) if symbol in before_only and symbol not in written[:first_digit] else span


@dataclass(frozen=True)
class Ordinal:
    """`1.º`, `2.ª`, `3º`: a whole number and the ordinal indicator, with or without the full stop."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = "".join(request.data["ordinal_marks"])
        for match in re.finditer(f"[0-9]+([.]?[{marks}])", fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or not one_digit_set(text[start:match.start(1)]):
                continue
            digits = match.group()[:match.start(1) - start]
            script = digit_script(text[start:match.start(1)])
            if len(digits) > 1 and digits[0] == "0":
                continue
            yield Span(start, end, Form.ORDINAL,
                       FrozenMap({"digits": digits, "marker": match.group(1), "prefix": "", "suffix": "",
                                  "script": script}), recognizer=self.name)


@dataclass(frozen=True)
class Expression:
    """`5+3`, `2 × 2 = 4`, `-2+3=1`: operators between integers, with no letter on either side, as in `en.py`.
    Each integer may carry one sign right before its digits. An operator right after the last integer, two signs
    before one integer, or a symbol of the `symbols` table next to the expression keep it as written."""
    name: str = "expression"
    form: Form = Form.EXPRESSION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        operators = re.escape("".join(request.data["operators"]))
        open_operator = re.compile(f" ?[{operators}]")
        symbols = request.data["symbols"]
        for match in digit_run_matches(request.data["patterns"]["expression"], fold_digits(text)):
            start, end = match.span()
            if (not (is_bounded(text, start, end) and one_digit_set(text[start:end]))
                    or open_operator.match(text, end)):
                continue
            written = match.group().replace(" ", "")
            first = re.match(f"[{_SIGNS}]?[0-9]+", written).group()
            pairs = re.findall(f"([{operators}])([{_SIGNS}]*[0-9]+)", written[len(first):])
            if not pairs:
                continue
            signs, others = zip(*pairs)
            unclear = (any(len(operand) - len(operand.lstrip(_SIGNS)) > 1 for operand in others)
                       or (start > 0 and (text[start - 1] in symbols
                                          or (text[start - 1] in _SIGNS and not first[0].isdigit())))
                       or (end < len(text) and text[end] in symbols))
            yield Span(start, end, Form.EXPRESSION, FrozenMap({"operands": (first, *others), "operators": signs}),
                       recognizer=self.name, keep=unclear)


@dataclass(frozen=True)
class DateNamed:
    """`1 de março de 2024`, `15 de maio`: a day, `de`, a month name and perhaps `de` and a year."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months = [month.lower() for month in request.data["months"]]
        for match in re.finditer(request.data["patterns"]["date_named"], fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or not one_digit_set(text[start:end]):
                continue
            day, month_name, year = match.groups()
            month = months.index(month_name.lower()) + 1
            year_value = int(year) if year is not None else None
            if not is_valid(year_value, month, int(day)):
                continue
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year_value, "month": month, "day": int(day),
                                  "written_order": "DMY", "month_written": "name",
                                  "prefix": "", "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Roman:
    """A Roman numeral after a name or after `século`: `D. Maria II`, `Luís XIV`, `século XIX`.

    A numeral right after a title, as in `D. XIV` or `Dom XIV`, has no name and stays as written. After a name, a
    value from 1 to 30 reads when a regnal title comes right before the name, as in `D. João V`
    and `papa Pio X`, or when the numeral has two letters or more and a value from 11, which reads as a cardinal with
    no gender, as in `Luís XIV`. A short numeral after another capitalised word, as in `Malcolm X` or `Classe II`,
    stays as written."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value

        data = request.data
        titles = frozenset(data["regnal_titles"])
        not_names = titles | {key.rstrip(".") for key in data["titles"]} | frozenset(data["titles"].values())
        centuries = frozenset(data["century_words"])
        words = context_words(tokens)
        breaks = clause_breaks(text)
        for match in re.finditer("[IVXLCDM]+", text):
            start, end = match.span()
            value = roman_value(match.group())
            if value is None or not is_bounded(text, start, end) or not text.endswith(" ", 0, start):
                continue
            before = clause_window(text, words, start, end, -1, limit=1, breaks=breaks)
            if not before:
                continue
            index = bisect_right(words, start, key=lambda word: word.end)
            if index >= 1 and words[index - 1].text in not_names:
                continue
            title = index >= 2 and words[index - 2].text in titles \
                and text[words[index - 2].end:words[index - 1].start] in (" ", ". ")
            if before[-1].lower() in centuries:
                reads = value <= 30
            elif before[-1][0].isupper() and value <= 30:
                reads = title or (len(match.group()) >= 2 and value >= 11)
            else:
                reads = False
            if reads:
                yield Span(start, end, Form.ROMAN,
                           FrozenMap({"value": value, "role": "ordinal" if value <= 10 else "cardinal",
                                      "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, `D.` before a name, `n.º` before a number, a title written in lowercase,
    and the abbreviations of the table."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        tables = ((data["titles"], str.isupper), (data["honorific_before_name"], str.isupper),
                  (data["number_abbreviations"], str.isdigit),
                  (dict.fromkeys(data["abbreviations_any_case"]), lambda _: True),
                  (data["abbreviations"], lambda _: True))
        final = frozenset(data["sentence_final"])
        for table, follows in tables:
            for key in sorted(table, key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    if is_bounded(text, position, end) and follows(following):
                        sentence_end = key in final and (following == "" or following.isupper())
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}),
                                   trail="." if sentence_end else "", recognizer=self.name)
                    position = text.find(key, end)


LANGUAGE = LanguageSpec(
    code="pt",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["color"], DateNamed(), SHARED["date_numeric"], Clock(),
                 PortugueseTelephone(), Money(), SHARED["percent"], SHARED["measure"], Expression(),
                 SHARED["fraction"], SHARED["range"], Ordinal(), Roman(), Abbreviation(), SHARED["decimal"],
                 SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.COLOR: speak_color, Form.DATE: speak_date, Form.TIME: speak_time,
        Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range,
        Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    attach=attach,
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"24h"}),
        "minute_style": frozenset({"number"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long", "short"}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"register"}),
)
