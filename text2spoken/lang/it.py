"""Italian: it-IT, the default variety, it-CH and it-SM.

Cardinals and ordinals come from ovos-number-parser (design section 5.4), the `it` extra. Its forms agree with the
Enciclopedia dell'Italiano Treccani, "numerali", Pronuncia e grafia. A compound in uno keeps its full form, as
"ventuno", "centouno" and "ventunomila", and the same section allows both forms before a noun: "Nei composti
(ventuno, trentuno, ecc.) accompagnati da un nome, questo è invariabile se il numerale segue il nome, ma può essere
apocopato se il numerale precede il nome". 108 reads "centootto": "con cento seguito da una decina o da un'unità,
l'elisione è poco comune con uno, otto e undici [...] (29) centootto [raramente centotto]". 1003 reads "milletré": "I
composti di tre vanno accentati". CLDR RBNF `it` writes "centotto" and "milletre" for these numbers.

Of the cardinals, only uno changes with the noun (Treccani, "numerali", Cardinali: "In italiano sono invariabili, a
eccezione di uno, che varia secondo il genere [...] e che al femminile assume la forma una"). Without a noun, 1
reads "uno" (Vocabolario Treccani, "uno", 1: "il numero uno, a pagina uno"), or "una" when the caller gives
`default_gender` feminine. Before a noun, uno takes the form of the indefinite article ("numerali": "Il numerale
cardinale uno subisce apocope là dove la subirebbe l'articolo indeterminativo"). Before a masculine noun the article
is un, unless the noun takes lo (Vocabolario Treccani, "uno": "l'uso della quale è regolato dalle stesse norme che
regolano l'uso dell'art. determ. masch. sing. il, rispetto alla sua variante lo: un uomo, un osso, un cane, uno
scolaro, uno zoccolo"). The Vocabolario Treccani, "articolo", gives where lo stands, and un and uno "si usano
rispettivamente negli stessi casi di il e di lo": "b) davanti alle consonanti gl(i), gn, sc(i), z [...] c) davanti ai
gruppi consonantici s + cons., ps-, pn-, x". `lo_onsets` lists these onsets, and an s before a consonant takes uno
too, so `1 zaino` reads "uno zaino" and `1 studente` "uno studente". The gender of a noun comes from the noun list
`data/wiktionary/it_noun_genders.json`, which `scripts/extract_noun_genders.py` makes from the categories "Italian
masculine nouns" and "Italian feminine nouns" of the English Wiktionary. The Italian Wiktionary has no category for
the gender of a noun. The list leaves out a word of both categories. So `1 anno` reads "un anno" and `1 gatta` "una
gatta". A scale word is a masculine noun (Vocabolario Treccani, "milione": "un milione di euro"). After a number, a
noun that is also a preposition, a conjunction, an adverb, a pronoun, a determiner or an article may be a word that
the number does not count, as "oggi" in `pagina 1 oggi`, and the list names these nouns in `function_words`. A unit
name of CLDR, such as "ora", is a noun, and takes its CLDR gender, so `1 ora` reads "una ora". A month name after a
number writes a date, as in `1 maggio`. Before these words and any other lowercase word, `1` stays as
written, because the noun may come later, as in `tra 1 e 2 ore`.

A decimal reads the CLDR RBNF `it` rule `x.x: ←← virgola →→` of `spellout-numbering`: the whole part, "virgola",
then each digit of the decimal part, so `3,14` reads "tre virgola uno quattro" and the zero of `2,50` stays. The
minus sign reads "meno" (RBNF `-x: meno →→`; Vocabolario Treccani, "meno": "il termometro segna m. quattro (-4)"),
and the plus sign "più" ("più": "stamattina il termometro segna appena più tre (+ 3)").

An ordinal is written with "il piccolo segno esponenziale ‹º› per il genere maschile o ‹ª› per il genere femminile"
("numerali", Pronuncia e grafia), as the CLDR RBNF `it` rules `digits-ordinal-masculine` and
`digits-ordinal-feminine` write it. The Vocabolario Treccani, "ordinale", gives the rule of the ordinals after
decimo: they "si formano dal tema del corrispondente cardinale ital. con l'aggiunta della terminazione -èsimo: così
undicesimo, [...] ventitreesimo, [...] centunesimo, [...] millesimo, duemillesimo, [...] diecimillesimo". So 108
reads "centoottesimo", from "centootto", and 180 "centottantesimo". The same entry gives the separate form for the
ordinals "per i quali l'altro tipo sarebbe sentito come poco eufonico: centesimo decimo, millesimo primo, millesimo
secondo, millesimo decimo, millesimo undecimo o undicesimo, ecc. (in questi casi la grafia staccata è preferita)".
`SEPARATE_ORDINALS` holds these five numbers. ovos-number-parser follows the rule, with two differences, where the
file follows the Treccani entry: it writes "centodecimo" for 110, and it writes "decimo" at the end of every other
number above 100 that ends in 10, as "duecentodecimo" for 210, where the rule gives "duecentodiecesimo" from
"duecentodieci". An ordinal above 999999 stays as written, because ovos-number-parser writes
"tremilionecinquantamilasimo" for 3500000.

The degree sign writes an ordinal too (Vocabolario Treccani, "centesimo": "in scrittura numerica 100°"; "articolo":
"l'a. 1° della Costituzione"; "gennaio": "cominciare l'anno dal 1° marzo"). `noun_ordinal_marks` names it. Before a
month name of `months` or a noun that the number counts it is an ordinal that agrees with the noun, so `1° maggio`
reads "primo maggio" and `21° secolo` "ventunesimo secolo". A month name is masculine ("gennaio": "s. m."). Before `C`
or `F` the degree sign writes a temperature, and in other places an angle, so there it is not an ordinal.

A fraction is "formati da un aggettivo numerale cardinale e da un ordinale (un terzo, due quinti, quattro decimi,
ecc.)" ("numerali", Frazionari), and 1/2 is "un mezzo" (Vocabolario Treccani, "mezzo", 5: "un mezzo, una metà"). The
ordinal is plural after a numerator other than one (`spellout-ordinal-masculine-plural`), and a denominator above 100
stays as written. Before a noun, mezzo is an adjective that agrees with it ("numerali", Frazionari: "mi darebbe mezzo
chilo di patate e mezza lattuga?"), so 1/2 before a noun of the noun list reads "mezzo" or "mezza", and before
another lowercase word it stays as written. `half_links` names the words after which 1/2 is still the noun "un
mezzo" ("mezzo", 1: "ancora un mezzo di vino"). A percentage is the
number and "per cento" (Vocabolario Treccani, "per cento": "n per cento (simbolo: n%)").

An expression reads its operators by the Vocabolario Treccani: "più" ("quattro più cinque è uguale a nove (in
simboli: 4 + 5 = 9)"), "meno" ("tredici meno otto è uguale a cinque"), "per" ("a × b [...] si legge: a per b") and
"è uguale a" for `=`. The dimension mark `×` of a measure reads "per" too.

Unit words and the gender of each unit come from CLDR 49 (`cldr-units-full`, the `long` patterns of the variety):
`5 km` reads "cinque chilometri" and `1 h` "una ora", because CLDR gives `duration-hour` the feminine gender. A unit
with no CLDR gender takes the gender of its first word in the noun list. The
article form una does not elide, as the Vocabolario Treccani, "uno", allows: "il femm. sing. una può subire elisione
dinanzi a parola che comincia per vocale". A symbol that cannot be a plain word, such as `km/h` or `°C`, reads with no
list. `unit_symbols` names the symbols made only of letters that read as units.

Currency names and currency symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of the variety): `15 €`
reads "quindici euro", because CLDR `it` gives the euro one name for every plural category, and the Vocabolario
Treccani, "euro", marks it "s. m. [...] invar.". `currency_symbols` names the ISO 4217 codes that read, because a symbol
of letters reads only from that list. CLDR gives a currency no gender, so 1 takes the gender of the first word of the
currency name in the noun list: "un euro", "una sterlina britannica". An amount next to `$` or `¥` stays as written,
with its number, because CLDR `it` gives each of these signs to more than one currency; `kept_currency_signs` names
them. Two decimals read as the minor unit after "e", so `10,50 €` reads "dieci euro e cinquanta centesimi", and
other decimals read as a decimal number before the currency name. The minor unit of the euro and of the franc is the
centesimo (Vocabolario Treccani, "centesimo", 2b: "Moneta che vale la centesima parte di un'euro, di una lira o di
altra unità monetaria"), of the dollar the cent (the same entry: "cent negli Stati Uniti d'America"), and of the
pound the penny ("penny": "pl. pence [...] usato in ital. al masch. [...] alla 100a parte della sterlina").
`currencies` gives these names, and the gender of a name that the noun list does not hold. A scale word after an
amount takes "di" before the currency ("numerali", Cardinali: milione, miliardo "devono essere [...] seguiti –
qualora precedano un altro nome – dalla preposizione di"), so `€ 2 milioni` reads "due milioni di euro".

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

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.resources import files
from itertools import takewhile

from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.numbers import written_amount
from text2spoken.core.recognizers import SHARED, numbers_in, signed, speak_decimal, speak_expression
from text2spoken.core.recognizers import speak_cardinal as core_speak_cardinal
from text2spoken.core.recognizers import speak_fraction as core_speak_fraction
from text2spoken.core.recognizers import speak_lexicon, speak_percent
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.tokens import Token, is_bounded, is_word_char
from text2spoken.core.units import cldr_data, unit_reading
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
    "currencies": {"EUR": {"minor": {"one": "centesimo", "other": "centesimi"}},
                   "CHF": {"minor": {"one": "centesimo", "other": "centesimi"}},
                   "USD": {"minor": {"one": "cent", "other": "cent"}},
                   "GBP": {"minor": {"one": "penny", "other": "pence", "gender": "masculine"}}},
    "kept_currency_signs": ["$", "¥"],
    "scales": {"milione": "milione", "milioni": "milioni", "miliardo": "miliardo", "miliardi": "miliardi"},
    "unit_symbols": ["kg", "g", "km", "m", "cm", "mm", "l", "h", "min"],
    "dimension_marks": ["x", "×"],
    "dimension_word": "per",
    "operators": {"+": "più", "−": "meno", "×": "per", "=": "è uguale a"},
    "ordinal_marks": {"º": "masculine", "ª": "feminine"},
    "noun_ordinal_marks": ["°"],
    "months": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
               "novembre", "dicembre"],
    "lo_onsets": ["gli", "gn", "ps", "pn", "x", "z"],
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

LARGEST_PLURAL_ORDINAL = 100
"""The last plural ordinal that a fraction reads, by RBNF `it`. The core fraction recognizer reads no larger
denominator."""
LARGEST_ORDINAL = 999_999
"""The last ordinal that reads. From a million up ovos-number-parser writes "tremilionecinquantamilasimo" for
3500000."""
SEPARATE_ORDINALS = frozenset({110, 1001, 1002, 1010, 1011})
"""The ordinals that the Vocabolario Treccani, "ordinale", writes as two words: "centesimo decimo, millesimo primo,
millesimo secondo, millesimo decimo, millesimo undecimo o undicesimo"."""
VOWELS = "aeiouàèéìíòóù"


class ItalianSpeller:
    """ovos-number-parser for integers and ordinals, with the Treccani forms where the parser differs from them;
    decimals by the RBNF `x.x` rule; fractions with the plural ordinals of RBNF."""

    def __init__(self):
        self.parser = OvosNumberSpeller({M: "masculine", F: "feminine"})
        self.plural = RbnfSpeller(cardinal={Features(): "spellout-numbering"},
                                  ordinal={Features(): "spellout-ordinal-masculine-plural"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.parser.cardinal(digits, Features(gender=features.gender), request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or value > LARGEST_ORDINAL:
            raise DeclinedReading(f"no ordinal above {LARGEST_ORDINAL}")
        features = Features(gender=features.gender)
        if value in SEPARATE_ORDINALS:
            head = 100 if value < 1000 else 1000
            return f"{self.ordinal(str(head), features, request)} {self.ordinal(str(value - head), features, request)}"
        if value > 100 and value % 100 == 10:
            stem = self.cardinal(digits, Features(), request)[:-1]
            return stem + ("esima" if features.gender is F else "esimo")
        return self.parser.ordinal(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", Features(), request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        if bounded_integer(numerator) == 1:
            bottom = "mezzo" if bounded_integer(denominator) == 2 else self.ordinal(denominator, Features(), request)
            return f"un {bottom}"
        value = bounded_integer(denominator)
        if value is None or value > LARGEST_PLURAL_ORDINAL:
            raise DeclinedReading(f"no plural ordinal above {LARGEST_PLURAL_ORDINAL}")
        bottom = self.plural.ordinal(denominator, Features(), request)
        return f"{self.cardinal(numerator, Features(), request)} {bottom}"


SPELLER = ItalianSpeller()


def _default_gender(request: Request) -> GrammaticalGender | None:
    return request.params.default_gender.get(LANGUAGE.code)


@lru_cache(maxsize=1)
def _noun_list() -> dict:
    path = files("text2spoken") / "data" / "wiktionary" / "it_noun_genders.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def noun_genders() -> dict[str, str]:
    """The gender of each noun of `data/wiktionary/it_noun_genders.json`, by its lowercase singular."""
    table = _noun_list()
    return {**dict.fromkeys(table["masculine"], M.value), **dict.fromkeys(table["feminine"], F.value)}


@lru_cache(maxsize=1)
def function_nouns() -> frozenset[str]:
    """The nouns of the noun list that are also a preposition, a conjunction, an adverb, a pronoun, a determiner or
    an article."""
    return frozenset(_noun_list()["function_words"])


def one_before(noun: str, gender: str | None, request: Request) -> str:
    """1 before a noun, as the indefinite article: "una" before a feminine noun, "uno" before a masculine noun that
    takes lo, and "un" before another masculine noun."""
    if gender == F.value:
        return "una"
    if gender != M.value:
        raise DeclinedReading(f"no gender for {noun!r}")
    takes_lo = noun.startswith(tuple(request.data["lo_onsets"])) or (
        noun[:1] == "s" and noun[1:2] != "" and noun[1] not in VOWELS)
    return "uno" if takes_lo else "un"


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
    return signed(one_before(noun, gender, request), amount["sign"], request)


@lru_cache(maxsize=None)
def unit_nouns(tag: str) -> dict[str, str]:
    """The gender of each one-word CLDR unit name of a variety that CLDR gives a gender: "ora", "metro"."""
    return {name: unit["gender"] for unit in cldr_data(tag)["units"].values() if unit.get("gender")
            for pattern in unit["names"].values() if pattern.startswith("{0} ") and " " not in (name := pattern[4:])}


def counted_noun(word: str, request: Request) -> str | None:
    """The gender of a word after a number that the number counts: a scale word is masculine, a CLDR unit name has
    its CLDR gender, and a noun has its gender in the noun list. A month name, as in `1 maggio`, and a noun that is
    also a function word, as "oggi" in `pagina 1 oggi`, may be no noun that the number counts, and give None."""
    if word in request.data["scales"]:
        return M.value
    if word in unit_nouns(request.variety.tag):
        return unit_nouns(request.variety.tag)[word]
    if word in request.data["months"] or word in function_nouns():
        return None
    return noun_genders().get(word)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """1 that `OneBeforeWord` finds before a noun that it counts reads as the article of that noun: "un milione",
    "uno zaino", "una gatta", "una ora". In other places 1 reads by `default_gender`, as the label in `(1) portata`.
    Other numbers read through the core verbalizer."""
    fields, request = span.fields, context.request
    if fields["lead"] or bounded_integer(fields["digits"]) != 1 or len(fields["digits"]) > 1:
        return core_speak_cardinal(span, context)
    counted = span.recognizer == OneBeforeWord.name and context.after
    gender = counted_noun(context.after[0], request) if counted else None
    if gender is not None:
        words = one_before(context.after[0], gender, request)
    else:
        words = SPELLER.cardinal("1", Features(gender=_default_gender(request)), request)
    return signed(words, fields["sign"], request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """1/2 before a noun is the adjective mezzo, which agrees with the noun: "mezzo chilo di patate e mezza
    lattuga". Before "di" it is the noun "un mezzo". Before another lowercase word 1/2 stays as written."""
    fields, after = span.fields, context.after
    half = bounded_integer(fields["numerator"]) == 1 and bounded_integer(fields["denominator"]) == 2
    word = after[0] if after and after[0].isalpha() and after[0].islower() else ""
    if not half or not word or word in context.request.data["half_links"] or fields["sign"]:
        return core_speak_fraction(span, context)
    gender = counted_noun(word, context.request)
    if gender is None:
        raise DeclinedReading("1/2 before a word that is not in the noun list")
    return "mezza" if gender == F.value else "mezzo"


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """The marker gives the gender of the ordinal. After a mark of `noun_ordinal_marks` the ordinal agrees with the
    noun that follows, and a month name is masculine: "1° maggio" reads "primo maggio"."""
    request = context.request
    marker, word = span.fields["marker"], context.after[0] if context.after else ""
    gender = request.data["ordinal_marks"].get(marker) or counted_noun(word, request) or M.value
    return SPELLER.ordinal(span.fields["digits"], Features(gender=GrammaticalGender(gender)), request)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The last amount agrees with the unit, by the CLDR gender of the unit or else by the noun list: "un
    chilometro", "una ora"."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    pattern, gender = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amounts[-1])))
    noun = pattern.replace("{0}", "").split()[0]
    gender = gender.value if isinstance(gender, GrammaticalGender) else gender or noun_genders().get(noun)
    read = [plain_amount(a, request) for a in amounts[:-1]] + [amount_before(amounts[-1], noun, gender, request)]
    words = f" {request.data['dimension_word']} ".join(read)
    return pattern.replace("{0}", words)


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount and the currency name in the plural category of the amount: "quindici euro", "un euro". 1 takes
    the gender of the first word of the name in the noun list: "una sterlina britannica". A scale word comes between
    them, with "di": "due milioni di euro". Two decimals are the minor unit, when the currency names one: "dieci
    euro e cinquanta centesimi". Other decimals read as a decimal number: "uno virgola cinque euro"."""
    request = context.request
    fields = span.fields
    currency = currency_table(request)[fields["currency"]]
    amount = FrozenMap({**fields["amount"], "sign": ""})
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        words = f"{amount_before(amount, scale, M.value, request)} {scale} di {currency_name(currency, 'other')}"
    elif fraction and not (len(fraction) == 2 and "minor" in currency):
        category = plural_category(request, written_amount(amount))
        words = f"{plain_amount(amount, request)} {currency_name(currency, category)}"
    elif fraction and int(fraction):
        cents = str(int(fraction))
        minor = _counted(cents, currency["minor"][plural_category(request, cents)], request,
                         currency["minor"].get("gender"))
        words = minor if bounded_integer(integer) == 0 else f"{_currency_amount(integer, currency, request)} e {minor}"
    else:
        words = _currency_amount(integer, currency, request)
    return signed(words, fields["amount"]["sign"], request)


def _counted(digits: str, name: str, request: Request, gender: str | None = None) -> str:
    """A whole number before a noun phrase of the given gender, or else of the gender of its first word in the noun
    list."""
    amount = FrozenMap({"integer": digits, "fraction": "", "sign": ""})
    noun = name.split()[0]
    return f"{amount_before(amount, noun, gender or noun_genders().get(noun), request)} {name}"


def _currency_amount(integer: str, currency: FrozenMap, request: Request) -> str:
    return _counted(integer, currency_name(currency, plural_category(request, integer)), request)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """The full word of the abbreviation, with a capital where a clause starts."""
    data = context.request.data
    key = span.fields["key"]
    word = next(data[table][key] for table in ("titles", "abbreviations", "number_abbreviations")
                if data[table].get(key) is not None)
    return word[0].upper() + word[1:] if not context.before else word


@dataclass(frozen=True)
class OneBeforeWord:
    """`1` and a space before a lowercase word. Before a noun that 1 counts, the span reads as the article of the
    noun. Before another word, as in `tra 1 e 2 ore`, it stays as written: uno takes the gender of the noun that it
    counts, and the file does not know that noun."""
    name: str = "one_before_word"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if (number.integer != "1" or number.sign or number.fraction is not None or number.end - number.start != 1
                    or (number.start and is_word_char(text[number.start - 1]))):
                continue
            after = text[number.end + 1:] if text.startswith(" ", number.end) else ""
            word = "".join(takewhile(str.isalpha, after))
            if word and word.islower():
                yield Span(number.start, number.end, Form.CARDINAL,
                           FrozenMap({"digits": "1", "sign": "", "lead": "", "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name,
                           keep=counted_noun(word, request) is None)


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
    """`1º`, `2ª`: a whole number and a marker of the `ordinal_marks` table, with no full stop between them. A mark
    of `noun_ordinal_marks` makes an ordinal only before a month name or a noun that the number counts, as in `1°
    maggio` and `21° secolo`: before `C` or `F` it writes a temperature, and in other places an angle."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None or (number.start and is_word_char(text[number.start - 1])):
                continue
            marker = text[number.end:number.end + 1]
            if marker in data["noun_ordinal_marks"]:
                word = "".join(takewhile(str.isalpha, text[number.end + 2:]))
                noun = text.startswith(" ", number.end + 1) and (
                    word in data["months"] or counted_noun(word, request) is not None)
                marker = marker if noun else ""
            if marker in (*data["ordinal_marks"], *data["noun_ordinal_marks"]) \
                    and is_bounded(text, number.start, number.end + 1):
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
