"""Italian: it-IT, the default variety, it-CH and it-SM.

Number words come from CLDR RBNF `it` (design section 5.4). A cardinal reads the `spellout-numbering` rule set, which
writes the full form of a compound in uno: "ventuno", "centouno", "milleuno". The Enciclopedia dell'Italiano Treccani,
"numerali", Pronuncia e grafia, allows both forms before a noun: "Nei composti (ventuno, trentuno, ecc.) accompagnati da
un nome, questo è invariabile se il numerale segue il nome, ma può essere apocopato se il numerale precede il nome". The
same section corrects one RBNF form: "con cento seguito da una decina o da un'unità, l'elisione è poco comune con uno,
otto e undici [...] (29) centootto [raramente centotto]". So every "centotto" of RBNF reads "centootto", as in 108 and
1108. The same section gives "I composti di tre vanno accentati", and RBNF writes "milletre" for 1003 and "duemilatre"
for 2003, so a compound word that ends in tre ends in "tré". A number of 10**18 or more stays as written, because RBNF
`it` has no rule for it.

Of the cardinals, only uno changes with the noun (Treccani, "numerali", Cardinali: "In italiano sono invariabili, a
eccezione di uno, che varia secondo il genere [...] e che al femminile assume la forma una"). Without a noun, 1
reads "uno" (Vocabolario Treccani, "uno", 1: "il numero uno, a pagina uno"), or "una" when the caller gives
`default_gender` feminine. Before a noun, uno takes the form of the indefinite article ("numerali": "Il numerale
cardinale uno subisce apocope là dove la subirebbe l'articolo indeterminativo"). Before a masculine noun the article
is un, unless the noun takes lo (Vocabolario Treccani, "uno": "l'uso della quale è regolato dalle stesse norme che
regolano l'uso dell'art. determ. masch. sing. il, rispetto alla sua variante lo: un uomo, un osso, un cane, uno
scolaro, uno zoccolo"). lo stands "davanti alle consonanti gl(i), gn, sc(i), z [...] e davanti a quei gruppi
consonantici che si possono scindere tra due sillabe" (Vocabolario Treccani, "lo"), and no masculine noun that this
file reads after 1 starts so: these nouns are the CLDR unit and currency names and the scale words. The file knows
the noun and its gender only after an amount of money or a unit, and before a scale word such as "milione"
(Vocabolario Treccani, "milione": "un milione di euro"). Before any other lowercase word, `1` stays as written,
because that word may be a noun of either gender, or the noun may come later, as in `tra 1 e 2 ore`.

A decimal reads the CLDR RBNF `it` rule `x.x: ←← virgola →→` of `spellout-numbering`: the whole part, "virgola",
then each digit of the decimal part, so `3,14` reads "tre virgola uno quattro" and the zero of `2,50` stays. The
minus sign reads "meno" (RBNF `-x: meno →→`; Vocabolario Treccani, "meno": "il termometro segna m. quattro (-4)"),
and the plus sign "più" ("più": "stamattina il termometro segna appena più tre (+ 3)").

An ordinal is written with "il piccolo segno esponenziale ‹º› per il genere maschile o ‹ª› per il genere femminile"
("numerali", Pronuncia e grafia), as the CLDR RBNF `it` rules `digits-ordinal-masculine` and
`digits-ordinal-feminine` write it. It reads `spellout-ordinal-masculine` or `spellout-ordinal-feminine`. RBNF
writes "centoottantesimo" for 180 and "duemilamillesimo" for 21000, so an ordinal above 100 stays as written. `1°`
with the degree sign stays as written too, because the degree sign also writes an angle or a temperature.

A fraction is "formati da un aggettivo numerale cardinale e da un ordinale (un terzo, due quinti, quattro decimi,
ecc.)" ("numerali", Frazionari), and 1/2 is "un mezzo" (Vocabolario Treccani, "mezzo", 5: "un mezzo, una metà"). The
ordinal is plural after a numerator other than one (`spellout-ordinal-masculine-plural`). Before a noun, mezzo is
an adjective that agrees with it ("numerali", Frazionari: "mi darebbe mezzo chilo di patate e mezza lattuga?"), so
1/2 before a lowercase word stays as written. `half_links` names the words after which 1/2 is still the noun
"un mezzo" ("mezzo", 1: "ancora un mezzo di vino"). A percentage is the
number and "per cento" (Vocabolario Treccani, "per cento": "n per cento (simbolo: n%)").

An expression reads its operators by the Vocabolario Treccani: "più" ("quattro più cinque è uguale a nove (in
simboli: 4 + 5 = 9)"), "meno" ("tredici meno otto è uguale a cinque"), "per" ("a × b [...] si legge: a per b") and
"è uguale a" for `=`. The dimension mark `×` of a measure reads "per" too.

Unit words and the gender of each unit come from CLDR 49 (`cldr-units-full`, the `long` patterns of the variety):
`5 km` reads "cinque chilometri" and `1 h` "una ora", because CLDR gives `duration-hour` the feminine gender. The
article form una does not elide, as the Vocabolario Treccani, "uno", allows: "il femm. sing. una può subire elisione
dinanzi a parola che comincia per vocale". A symbol that cannot be a plain word, such as `km/h` or `°C`, reads with no
list. `unit_symbols` names the symbols made only of letters that read as units.

Currency names and currency symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of the variety): `15 €`
reads "quindici euro", because CLDR `it` gives the euro one name for every plural category, and the Vocabolario
Treccani, "euro", marks it "s. m. [...] invar.". `currency_symbols` names the ISO 4217 codes that read, because a symbol
of letters reads only from that list. CLDR gives a currency no gender, so `currency_genders` gives the gender of the
currencies that `1` reads before: euro (Vocabolario Treccani, "euro": "s. m."), dollaro ("dollaro": "s. m."), sterlina
("sterlina": "s. f.") and franco ("franco": "s. m."). One unit of another currency stays as written. An amount next to
`$` or `¥` stays as written, with its number, because CLDR `it` gives each of these signs to more than one currency;
`kept_currency_signs` names them. An amount with decimals stays as written, because no source of this file gives the
reading of the minor unit. A scale word after an amount takes "di" before the currency ("numerali", Cardinali: milione,
miliardo "devono essere [...] seguiti – qualora precedano un altro nome – dalla preposizione di"), so `€ 2 milioni`
reads "due milioni di euro".

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`) of the variety.

A title reads as its full word before a name, in the short form that the word takes there (Vocabolario Treccani,
"signore", 2: "il signor Rossi [...] al sig. Mario Rossi"; "dottore", 2: "si abbrevia in dott. o dr.", and "il
dottor Graziano"; "professore": "il professor Mario Rossi"). The feminine forms do not shorten: "sig.ra" ("signora":
"Alla sig.ra Luisa Rossi"), "sig.na" ("signorina": "Alla sig.na Claudia Bianchi"), "dott.ssa" ("dott.": "abbreviando
dottoressa in dott.ssa") and "prof.ssa" ("prof.": "per il femm. professoressa si usa o prof. o, volendo evitare
equivoco, prof.ssa"). The word is lowercase, as these entries write it, and takes a capital only where a clause
starts. "ecc." reads "eccetera" ("ecc.": "Abbreviazione di eccetera"), "art." before a number "articolo" ("art.":
"Abbreviazione grafica di articolo"), and "pag." before a number "pagina" ("pagina": "vedi a pagina (abbrev. p. o
pag.) 40").

it-IT and it-SM write the decimal comma and the group mark `.`, and it-CH the decimal point and the group mark `'` (CLDR
49 number symbols of `it`, `it_SM` and `it_CH`). In it-CH a number with a decimal point stays as written: Italian text
also writes a thousands group with the point, as in `1.000` (CLDR `it`), and a lone point before three digits fits both
readings (CGPM 2003, Resolution 10: the decimal marker "shall be either the point on the line or the comma on the
line"). The same point writes a clock time, as in `alle 8.00` of FLORES-200 devtest. The file reads no date, time or
year: `ovos-date-parser` gives no `spoken_*` reading for Italian, so a numeric date and a clock time stay as written.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from itertools import takewhile

from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.numbers import written_amount
from text2spoken.core.recognizers import SHARED, numbers_in, signed, speak_decimal, speak_expression
from text2spoken.core.recognizers import speak_cardinal as core_speak_cardinal
from text2spoken.core.recognizers import speak_fraction as core_speak_fraction
from text2spoken.core.recognizers import speak_lexicon, speak_percent
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import RbnfSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.tokens import Token, is_bounded, is_word_char
from text2spoken.core.units import unit_reading
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, FrozenMap, Form, GrammaticalGender, freeze

M, F = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "meno", "+": "più"},
    "digit_words": ["zero", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove"],
    "decimal_word": "virgola",
    "leads": {"pag. ": "pagina"},
    "percent": {"signs": ["%"], "position": "after", "word": "per cento"},
    "currency_symbols": ["EUR", "USD", "GBP", "CHF"],
    "currency_genders": {"EUR": "masculine", "USD": "masculine", "GBP": "feminine", "CHF": "masculine"},
    "kept_currency_signs": ["$", "¥"],
    "scales": {"milione": "milione", "milioni": "milioni", "miliardo": "miliardo", "miliardi": "miliardi"},
    "unit_symbols": ["kg", "g", "km", "m", "cm", "mm", "l", "h", "min"],
    "dimension_marks": ["x", "×"],
    "dimension_word": "per",
    "operators": {"+": "più", "−": "meno", "×": "per", "=": "è uguale a"},
    "ordinal_marks": {"º": "masculine", "ª": "feminine"},
    "half_links": ["di"],
    "titles": {"Sig.": "signor", "sig.": "signor", "Sig.ra": "signora", "sig.ra": "signora", "Sig.na": "signorina",
               "sig.na": "signorina", "Dott.": "dottor", "dott.": "dottor", "Dr.": "dottor", "dr.": "dottor",
               "Dott.ssa": "dottoressa", "dott.ssa": "dottoressa", "Prof.": "professor", "prof.": "professor",
               "Prof.ssa": "professoressa", "prof.ssa": "professoressa"},
    "abbreviations": {"ecc.": "eccetera"},
    "sentence_final": ["ecc."],
    "number_abbreviations": {"art.": "articolo"},
    "symbols": {"%": "percent", "€": "money", "£": "money", "$": "money", "¥": "money", "°": "measure", "×": "measure"},
    "patterns": {"expression": "[-−+]?[0-9]+(?: ?[+−×=] ?[-−+]*[0-9]+)+"},
})

VARIETIES = (
    Variety("it-IT"),
    Variety("it-CH", freeze({"number_marks": {"Latn": [{"decimal": ".", "group": "'"}]}, "keep_decimals": True})),
    Variety("it-SM"),
)

LARGEST_ORDINAL = 100
"""The last ordinal that reads. RBNF `it` writes "centoottantesimo" for 180, where the cardinal is "centottanta"."""


class ItalianSpeller:
    """CLDR RBNF `it` integers, with "una" for a feminine 1, decimals by the RBNF `x.x` rule, and fractions."""

    def __init__(self):
        self.rbnf = RbnfSpeller(cardinal={Features(): "spellout-numbering"},
                                ordinal={Features(): "spellout-ordinal-masculine",
                                         Features(gender=F): "spellout-ordinal-feminine"})
        self.plural = RbnfSpeller(cardinal={Features(): "spellout-numbering"},
                                  ordinal={Features(): "spellout-ordinal-masculine-plural"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        if features.gender is F and bounded_integer(digits) == 1:
            return "una"
        words = self.rbnf.cardinal(digits, Features(), request).replace("centotto", "centootto")
        return " ".join(w[:-3] + "tré" if w.endswith("tre") and w != "tre" else w for w in words.split(" "))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._ordinal(self.rbnf, digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", Features(), request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        if bounded_integer(numerator) == 1:
            bottom = "mezzo" if bounded_integer(denominator) == 2 else self.ordinal(denominator, Features(), request)
            return f"un {bottom}"
        bottom = self._ordinal(self.plural, denominator, Features(), request)
        return f"{self.cardinal(numerator, Features(), request)} {bottom}"

    @staticmethod
    def _ordinal(speller: RbnfSpeller, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or value > LARGEST_ORDINAL:
            raise DeclinedReading(f"no ordinal above {LARGEST_ORDINAL}")
        return speller.ordinal(digits, features, request)


SPELLER = ItalianSpeller()


def _default_gender(request: Request) -> GrammaticalGender | None:
    return request.params.default_gender.get(LANGUAGE.code)


def one_before(noun: str, gender: str | None) -> str:
    """1 before a noun: "una" for a feminine noun, "un" for a masculine one."""
    if gender not in (M.value, F.value):
        raise DeclinedReading(f"no gender for {noun!r}")
    return "una" if gender == F.value else "un"


def plain_amount(amount: FrozenMap, request: Request) -> str:
    """An amount with its sign, through the decimal speller for decimals and the cardinal speller for integers."""
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    else:
        words = SPELLER.cardinal(amount["integer"] or "0", Features(), request)
    return signed(words, amount["sign"], request)


def amount_before(amount: FrozenMap, noun: str, gender: str | None, request: Request) -> str:
    """An amount before its noun: the article form for 1, else the plain amount."""
    if amount["fraction"] or bounded_integer(amount["integer"] or "0") != 1:
        return plain_amount(amount, request)
    return signed(one_before(noun, gender), amount["sign"], request)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """1 reads "un" before a scale word, and by `default_gender` in other places. Other numbers read through the
    core verbalizer."""
    fields, request = span.fields, context.request
    if fields["lead"] or bounded_integer(fields["digits"]) != 1 or len(fields["digits"]) > 1:
        return core_speak_cardinal(span, context)
    if context.after and context.after[0] in request.data["scales"]:
        words = one_before(context.after[0], M.value)
    else:
        words = SPELLER.cardinal("1", Features(gender=_default_gender(request)), request)
    return signed(words, fields["sign"], request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """1/2 before a word other than "di" stays as written, because mezzo is then an adjective that agrees with its
    noun: "mezzo chilo di patate e mezza lattuga"."""
    fields, after = span.fields, context.after
    half = bounded_integer(fields["numerator"]) == 1 and bounded_integer(fields["denominator"]) == 2
    noun = bool(after) and after[0].isalpha() and after[0].islower()
    if half and noun and after[0] not in context.request.data["half_links"]:
        raise DeclinedReading("1/2 before a noun agrees with it")
    return core_speak_fraction(span, context)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    gender = GrammaticalGender(context.request.data["ordinal_marks"][span.fields["marker"]])
    return SPELLER.ordinal(span.fields["digits"], Features(gender=gender), context.request)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The last amount agrees with the unit: "un chilometro", "una ora"."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    pattern, gender = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amounts[-1])))
    noun = pattern.replace("{0}", "").split()[0]
    read = [plain_amount(a, request) for a in amounts[:-1]] + [amount_before(amounts[-1], noun, gender, request)]
    return pattern.replace("{0}", f" {request.data['dimension_word']} ".join(read))


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount and the currency name in the plural category of the amount: "quindici euro", "un euro". A scale
    word comes between them, with "di": "due milioni di euro"."""
    request = context.request
    fields = span.fields
    currency = currency_table(request)[fields["currency"]]
    amount = fields["amount"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        return f"{amount_before(amount, scale, M.value, request)} {scale} di {currency_name(currency, 'other')}"
    if amount["fraction"]:
        raise DeclinedReading("no source gives the reading of the minor unit")
    name = currency_name(currency, plural_category(request, written_amount(amount)))
    gender = request.data["currency_genders"].get(fields["currency"])
    return f"{amount_before(amount, name, gender, request)} {name}"


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """The full word of the abbreviation, with a capital where a clause starts."""
    data = context.request.data
    key = span.fields["key"]
    word = next(data[table][key] for table in ("titles", "abbreviations", "number_abbreviations")
                if data[table].get(key) is not None)
    return word[0].upper() + word[1:] if not context.before else word


@dataclass(frozen=True)
class OneBeforeWord:
    """`1` before a lowercase word, as in `1 mela` and `tra 1 e 2 ore`, stays as written: uno takes the gender of
    the noun that it counts, and the file does not know that noun. A scale word is a masculine noun."""
    name: str = "one_before_word"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for number in numbers_in(text, request):
            if (number.integer != "1" or number.sign or number.fraction is not None or number.end - number.start != 1
                    or (number.start and is_word_char(text[number.start - 1]))):
                continue
            after = text[number.end + 1:] if text.startswith(" ", number.end) else ""
            word = "".join(takewhile(str.isalpha, after))
            if word.isalpha() and word.islower() and word not in data["scales"]:
                yield Span(number.start, number.end, Form.CARDINAL,
                           FrozenMap({"digits": "1", "sign": "", "lead": "", "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptDecimal:
    """In a variety with `keep_decimals`, a number with a decimal mark stays as written, also in an amount, a
    measure or a percentage: `1.000` and `8.00` are a thousands group and a clock time in Italian text."""
    name: str = "kept_decimal"
    form: Form = Form.DECIMAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        if request.data.get("keep_decimals"):
            for number in numbers_in(text, request):
                if number.fraction is not None:
                    yield Span(number.start, number.end, Form.DECIMAL, number.amount(), recognizer=self.name,
                               keep=True)


@dataclass(frozen=True)
class KeptMoney:
    """An amount next to a sign of `kept_currency_signs`, as `5 $` and `2.500 ¥`, stays as written, with its
    number: CLDR `it` gives each of these signs to more than one currency."""
    name: str = "kept_money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        signs = FrozenMap({"kept": FrozenMap({"symbols": request.data["kept_currency_signs"]})})
        data = FrozenMap({**{k: v for k, v in request.language.data.items() if k != "currency_symbols"},
                          "currencies": signs})
        kept = Request(request.tag, request.variety, replace(request.language, data=data), request.params)
        return (replace(span, keep=True) for span in SHARED["money"].find(text, tokens, kept))


@dataclass(frozen=True)
class Ordinal:
    """`1º`, `2ª`: a whole number and a marker of the `ordinal_marks` table, with no full stop between them."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None or (number.start and is_word_char(text[number.start - 1])):
                continue
            marker = text[number.end:number.end + 1]
            if marker in marks and is_bounded(text, number.start, number.end + 1):
                yield Span(number.start, number.end + 1, Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="it",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], KeptDecimal(), SHARED["money"], KeptMoney(), SHARED["percent"], SHARED["measure"],
                 SHARED["expression"], SHARED["fraction"], Ordinal(), SHARED["abbreviation"], SHARED["decimal"],
                 OneBeforeWord(), SHARED["cardinal"], SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.ORDINAL: speak_ordinal, Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal,
        Form.CARDINAL: speak_cardinal, Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    genders=frozenset({M, F}),
    default_gender=M,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"default_gender": frozenset({"masculine", "feminine"})},
    not_applicable=frozenset(OPTIONS) - {"default_gender"},
)
