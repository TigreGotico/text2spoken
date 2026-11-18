"""Catalan: ca-ES, the default variety, ca-AD and ca-ES-valencia.

The sources are the Ortografia catalana of the Institut d'Estudis Catalans (OIEC, 2017), the Diccionari normatiu
valencià of the Acadèmia Valenciana de la Llengua (DNV), the guide "Abreviacions" of the Generalitat de Catalunya
(Criteris lingüístics 28, third edition, 2021), which the Optimot service publishes, and CLDR 49.

Cardinals come from ovos-number-parser (design section 5.4), as for a tag with no file. The masculine words follow the
rule of OIEC section 4.3.2.2a: a hyphen joins "entre desena i unitat, i entre unitat i els mots cents, centes", as in
"vint-i-dos, quaranta-tres, noranta-u, dues-centes, tres-cents, nou-cents setanta-set". Of the words of a number,
only un, dos and the hundreds take the feminine: DNV "un -a", DNV "dos (o dos dues)", and OIEC "dues-centes" and DNV
"dos-cents dos-centes (o dos-cents dues-centes)". A number before mil and a number before a scale noun take no other
rule: DNV "milió", "m. Mil milers, 1.000.000. Un milió de persones". So a feminine number reads only when the words of
ovos-number-parser follow this rule: un and dos become una and dues, also at the end of a compound, as "vint-i-una",
and a word in -cents becomes -centes, with dues for dos. A number with a feminine form before mil stays as written,
because no source of the file gives that form. Every other feminine number stays as written too, because
ovos-number-parser writes another form, as "vinta" for 20.

A number alone reads in the masculine, or in the feminine when the caller gives `default_gender` feminine. A number
before a word does not agree with the word, because the file has no gender of a noun; `1 casa` reads "un casa", as
on a tag with no file. A number with the group mark before a word, as `2.000 pessetes`, stays as written
(`KeptGrouped`) when its words change in the feminine, because the gender of the word is not known.

A decimal reads the whole part through the cardinal speller, then "coma", then each digit of the decimal part, by the
CLDR RBNF `ca` rule `x.x: ←← coma →→` of `spellout-numbering`, so the zero of `2,50` stays. The digit 1 reads "u", the
`1: u` rule of the same rule set and the name of the number in DNV "dos", "U més u, 2". The decimal mark is the comma
(DNV "coma": "Signe gràfic (,) que s'usa per a separar la part decimal de la part entera en una fracció decimal"), and
the group mark is the full stop (DNV "milió": "1.000.000"; CLDR 49 number symbols of `ca`). A number with spaces
between its groups of three digits, as `1 000 000`, stays as written (the core `space_groups`). A minus sign reads
"menys": DNV "menys", "Signe de la subtracció i dels nombres negatius (-)".

An ordinal is written as the number and "l'última lletra del mot desplegat" ("Abreviacions", 8, Numerals ordinals):
"1r 1a 2n 2a 3r 3a 4t 4a 5è 5a", "primer primera segon segona tercer tercera quart quarta cinquè cinquena". CLDR RBNF
`ca` writes the same marks in `digits-ordinal-masculine`. So a number and a letter of `ordinal_marks` reads as an
ordinal when the letter is the last letter of the ordinal word, and `a` gives the feminine. The words come from
ovos-number-parser. They follow OIEC section 4.3.2.2a, "vint-i-dosè, quaranta-tresè, noranta-unè", and section
3.1.2.1a, "els numerals ordinals (cinquè, sisè, setè, vuitè, novè, dissetè)". The parser writes the ordinal of 101
"cent primer", which the OIEC rule does not give, so an ordinal above 100 stays as written. A plural ordinal, as
`1rs` and `5ns` ("Quan els ordinals van en plural"), stays as written: the parser writes no plural ordinal.

A fraction is a cardinal and the name of the part: DNV "terç", "Un terç, 1/3. Dos terços, 2/3"; "quart", "Tres
quarts, ¾"; "quint", "Un quint, 1/5. Quatre quints, 4/5"; "mig", "Un mig, ½". `fraction_names` holds these names, and
a fraction with another denominator stays as written. "mig" agrees with its noun (DNV "mig mitja": "Mitja hora"), so
1/2 before a word stays as written, and so does 1/2 with another numerator. Another fraction reads before "de" and
its forms of `of_words`, as `3/4 de la població`, or with no word after it. Before another word, or after a word of
`date_words`, the slash may write a date of the CLDR 49 `ca` short date pattern `d/M/yy`, as in `el 3/4`, so the
fraction stays as written. A mixed number stays as written.

A percentage is the number and "per cent": DNV "cent", "per cent loc. adv. Per cada cent, una quantitat establida. El
quaranta per cent de la població activa". "Abreviacions" writes the sign after a space, "del 25 %".

Units come from CLDR 49 (`cldr-units-full`, the `long` patterns of the variety), with the gender of the unit:
"Abreviacions", Símbols, reads "15 m2" as "quinze metres quadrats", "1 cm" as "un centímetre" and "95 m" as
"noranta-cinc metres". CLDR gives `duration-hour` the feminine, so `2 h` reads "dues hores". A unit with no CLDR
gender, such as `mass-ton`, reads only an amount whose words are the same in both genders. `unit_symbols` names the
symbols made only of letters that read as units. A measure with a dimension mark, as `3 × 4 m`, stays as written.
CLDR 49 `ca` gives `m` no unit, because the symbol is both the month and the metre, and it names the millimetre
"mil·límetres" and the millilitre "mil·lilitres", which the core does not read. So `m`, `mm` and `ml` are not in
`unit_symbols`, and `KeptMeasure` keeps a number before them as written, as `35 mm`: the number alone would read in
the masculine before a unit that may be feminine.

Currency names come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of the variety): `15 €` reads "quinze
euros". CLDR gives a currency no gender, so `currency_genders` gives the gender of the euro (DNV "euro", "m. [...]
[símbol € ]") and of the dollar (DNV "dòlar", "m."). Another currency, such as the pound, reads only an amount whose
words are the same in both genders. `$` reads "dòlar": DNV "dòlar", "Unitat monetària dels Estats Units, del Canadà,
d'Austràlia i d'altres països". An amount with decimals stays as written, because no source of the file gives the
reading of the cents. A scale word after the amount, or the scale noun of a number in digits, takes "de" before the
currency name: "Abreviacions" reads "costa 20 MEUR (o M€)" as "costa 20 milions d'euros". The preposition takes the
form d' before a vowel, "precedida o no de h", but not before i or u "amb valor semivocàlic" (OIEC sections 4.1.1 and
4.1.2d). A unit name takes "de" after a scale noun in the same way.

A character that no other form claims reads by its CLDR 49 annotation name of the variety. `symbol_names` replaces
the CLDR name "secció" of `§` with the name that "Abreviacions" gives in its section on symbols: "§ & paràgraf i",
"vegeu el § 4.1".

The titles and abbreviations come from the list of "Abreviacions": "doctor Dr.", "doctora Dra.", "senyor Sr.",
"senyora Sra.", "mossèn Mn.", "etcètera etc.", "per exemple p. e., p. ex., v. gr.", "aproximadament aprox.", and,
before a number, "número n., núm.", "pàgina p., pàg.", "article art.", "capítol cap." and "volum vol.". A title reads
in lowercase, as DNV "senyor" writes it: "La senyora Fuster els rebrà de seguida". "prof." abbreviates "professor/a",
so it stays as written: the file does not know the gender.

A numeric date stays as written, and so does a clock time: ovos-date-parser has no Catalan `spoken_*` reading. A
say-as `date` reads the CLDR 49 `ca` long date pattern `d MMMM 'del' y`, as on a tag with no file (design section
17.5).

The three varieties read the same words. The DNV gives the Valencian forms first and the forms of the OIEC as
variants: "cinqué -ena (o cinquè)", "vuit", "adj. i m. i f. Huit", and "disset", "adj. i m. Dèsset". ovos-number-parser
writes the forms of the OIEC for each variety, so ca-ES-valencia reads "vuit" and "cinquè", which the DNV accepts.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache

from text2spoken.core import parsers
from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.numbers import written_amount
from text2spoken.core.recognizers import (SHARED, Money, OrdinalStop, numbers_in, signed as core_signed,
                                          speak_abbreviation, speak_cardinal as core_speak_cardinal, speak_cldr_date,
                                          speak_decimal as core_speak_decimal, speak_lexicon,
                                          speak_percent as core_speak_percent, written_shapes)
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import DIGIT_BOUND, OvosNumberSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.tokens import Token, digit_script, fold_digits, is_bounded
from text2spoken.core.units import unit_reading
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, FrozenMap, Form, GrammaticalGender, freeze

M, F = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "menys"},
    "digit_words": ["zero", "u", "dos", "tres", "quatre", "cinc", "sis", "set", "vuit", "nou"],
    "decimal_word": "coma",
    "leads": {},
    "ordinal_marks": {"r": "masculine", "n": "masculine", "t": "masculine", "è": "masculine", "a": "feminine"},
    "fraction_names": {"2": {"one": "mig"}, "3": {"one": "terç", "other": "terços"},
                       "4": {"one": "quart", "other": "quarts"}, "5": {"one": "quint", "other": "quints"}},
    "of_words": ["de", "del", "dels"],
    "date_words": ["el", "l'", "l’", "del", "al", "pel", "dia"],
    "percent": {"signs": ["%"], "position": "after", "word": "per cent"},
    "currency_symbols": ["EUR", "USD"],
    "currencies": {"USD": {"symbols": ["$"], "one": "dòlar", "other": "dòlars"}},
    "currency_genders": {"EUR": "masculine", "USD": "masculine"},
    "scales": {"milió": "milió", "milions": "milions", "miliard": "miliard", "miliards": "miliards"},
    "unit_symbols": ["kg", "g", "km", "cm", "l", "h", "min"],
    "dimension_marks": ["x", "×"],
    "titles": {"Sr.": "senyor", "Sra.": "senyora", "Dr.": "doctor", "Dra.": "doctora", "Mn.": "mossèn"},
    "abbreviations": {"etc.": "etcètera", "p. ex.": "per exemple", "aprox.": "aproximadament"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"núm.": "número", "pàg.": "pàgina", "art.": "article", "cap.": "capítol",
                             "vol.": "volum"},
    "symbols": {"%": "percent", "€": "money", "$": "money", "£": "money", "¥": "money", "°": "measure",
                "×": "measure"},
    "symbol_names": {"§": "paràgraf"},
    "operators": {},
})

VARIETIES = (
    Variety("ca-ES"),
    Variety("ca-AD"),
    Variety("ca-ES-valencia"),
)

LARGEST_ORDINAL = 100
"""The last ordinal that reads: ovos-number-parser writes "cent primer" for 101, which OIEC section 4.3.2.2a does not
give."""

FEMININE_ENDS = {"un": "una", "dos": "dues"}
"""The words of a number that take the feminine, also at the end of a compound: DNV "un -a", "dos (o dos dues)"."""

ELIDING = "aeiouàèéíòóú"
SEMIVOWELS = "iu"


class CatalanSpeller:
    """Cardinals and ordinals through ovos-number-parser. A feminine cardinal reads only when the parser writes the
    form of `feminine`. Decimals read the digits of the decimal part one by one, and fractions read the names of
    `fraction_names`."""

    def __init__(self):
        self.parser = OvosNumberSpeller({M: "masculine", F: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        words = self.parser.cardinal(digits, Features(), request)
        if features.gender != F:
            return words
        expected = feminine(words)
        if expected is None:
            raise DeclinedReading(f"no source gives the feminine of {words!r}")
        written = self.parser.cardinal(digits, Features(gender=F), request)
        if written != expected:
            raise DeclinedReading(f"ovos-number-parser writes the feminine {written!r}, not {expected!r}")
        return written

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or value > LARGEST_ORDINAL:
            raise DeclinedReading(f"no ordinal above {LARGEST_ORDINAL}")
        return self.parser.ordinal(digits, Features(gender=features.gender or M), request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", features, request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        names = request.data["fraction_names"].get(str(bounded_integer(denominator)))
        if names is None:
            raise DeclinedReading(f"no name of the part 1/{denominator}")
        if bounded_integer(numerator) == 1:
            return f"un {names['one']}"
        if "other" not in names:
            raise DeclinedReading(f"no plural of {names['one']!r}")
        return f"{self.cardinal(numerator, Features(), request)} {names['other']}"


SPELLER = CatalanSpeller()


def feminine(masculine: str) -> str | None:
    """The feminine of the words of a cardinal: un and dos become una and dues, also at the end of a compound, and a
    word in -cents becomes -centes, with dues for dos. None when such a word stands before "mil", for which the file
    has no source. A word before a scale noun stays masculine, because it counts the noun: "dos milions"."""
    words = masculine.split()
    out = []
    for index, word in enumerate(words):
        head, mark, last = word.rpartition("-")
        if last in FEMININE_ENDS:
            changed = head + mark + FEMININE_ENDS[last]
        elif last == "cents" and mark:
            changed = FEMININE_ENDS.get(head, head) + "-centes"
        else:
            changed = word
        following = words[index + 1] if index + 1 < len(words) else ""
        if changed != word and following in scale_words():
            changed = word
        elif changed != word and following == "mil":
            return None
        out.append(changed)
    return " ".join(out)


def gendered(words: str) -> bool:
    """Whether the words of a cardinal change in the feminine, or have no feminine that the file gives."""
    return feminine(words) != words


@lru_cache(maxsize=1)
def scale_words() -> frozenset[str]:
    """The scale nouns that ovos-number-parser writes after a number: "milió", "milions", "miliard"."""
    words = set()
    for power in range(6, DIGIT_BOUND, 3):
        try:
            readings = [parsers.pronounce_number(lead * 10 ** power, "ca").split() for lead in (1, 2)]
        except (OverflowError, NotImplementedError):
            break
        if any(len(reading) != 2 for reading in readings):
            break
        words.update(reading[1] for reading in readings)
    return frozenset(words)


def of(noun: str) -> str:
    """The preposition de and the noun: d' before a vowel, also after h, but not before i or u and a vowel."""
    letters = noun[1:] if noun[:1] == "h" else noun
    semivowel = letters[:1] in SEMIVOWELS and letters[1:2] in ELIDING
    return f"d'{noun}" if letters[:1] in ELIDING and not semivowel else f"de {noun}"


def counted(digits: str, gender: str | None, request: Request) -> str:
    """A whole number before a noun of the given gender. With no gender, the number reads only when its words are the
    same in both genders."""
    if gender == F.value:
        return SPELLER.cardinal(digits, Features(gender=F), request)
    words = SPELLER.cardinal(digits, Features(), request)
    if gender != M.value and gendered(words):
        raise DeclinedReading(f"no gender for the noun after {words!r}")
    return words


def before_noun(words: str, noun: str) -> str:
    """The number words and the noun, with de after a scale noun: "tres milions de quilòmetres"."""
    return f"{words} {of(noun)}" if words.split()[-1] in scale_words() else f"{words} {noun}"


def check_sign(sign: str, request: Request) -> None:
    """A sign with no word in `sign_words`, as `+`, keeps the form as written: no source of the file gives the word."""
    if sign and sign not in request.data["sign_words"]:
        raise DeclinedReading(f"no word for the sign {sign!r}")


def signed(words: str, sign: str, request: Request) -> str:
    """The words of a number after the word of its sign."""
    check_sign(sign, request)
    return core_signed(words, sign, request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    check_sign(span.fields["sign"], context.request)
    return core_speak_decimal(span, context)


def speak_percent(span: Span, context: SpanContext) -> str:
    check_sign(span.fields["amount"]["sign"], context.request)
    return core_speak_percent(span, context)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal in the gender of `default_gender`, through the core verbalizer for the masculine."""
    fields, request = span.fields, context.request
    gender = request.params.default_gender.get(LANGUAGE.code)
    digits = fields["digits"]
    if gender != F or fields["lead"] or (len(digits) > 1 and digits[0] == "0"):
        return core_speak_cardinal(span, context)
    return signed(SPELLER.cardinal(digits, Features(gender=F), request), fields["sign"], request)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """An ordinal of `Ordinal`. A number with a full stop and a letter, as `2.a`, comes from `OrdinalStop` and stays
    as written: in plain text the letter is not raised, as "Abreviacions" writes it."""
    marks = context.request.data["ordinal_marks"]
    if span.fields["marker"] not in marks:
        raise DeclinedReading(f"{span.fields['marker']!r} is no ordinal mark of the file")
    gender = GrammaticalGender(marks[span.fields["marker"]])
    return SPELLER.ordinal(span.fields["digits"], Features(gender=gender), context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction with no word after it, or before a word of `of_words` or "d'". 1/2 reads only with no word after
    it. After a word of `date_words` the slash may write a date, and before another word the noun may need another
    form, so the fraction stays as written. A mixed number stays as written."""
    fields, request = span.fields, context.request
    if fields["whole"]:
        raise DeclinedReading("no source gives the reading of a mixed number")
    if context.before and context.before[-1].lower() in request.data["date_words"]:
        raise DeclinedReading(f"a fraction after {context.before[-1]!r} may be a date")
    after = context.after[0] if context.after else ""
    if after[:1].isalpha():
        half = bounded_integer(fields["denominator"]) == 2
        if half or not (after in request.data["of_words"] or after.startswith(("d'", "d’"))):
            raise DeclinedReading(f"a fraction before {after!r}")
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), request)
    return signed(words, fields["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The amount and the CLDR unit name, the amount in the gender of the unit."""
    request = context.request
    if span.fields["relation"]:
        raise DeclinedReading("no source gives the Catalan word for a dimension mark")
    amount = span.fields["amount"]
    pattern, gender = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amount)))
    gender = gender.value if isinstance(gender, GrammaticalGender) else gender
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
        if gender != M.value and gendered(words.split(f" {request.data['decimal_word']} ")[0]):
            raise DeclinedReading(f"no feminine decimal {words!r}")
    else:
        words = counted(amount["integer"] or "0", gender, request)
    words = signed(words, amount["sign"], request)
    if pattern.startswith("{0} "):
        return before_noun(words, pattern[4:])
    return pattern.replace("{0}", words)


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount and the currency name in the plural category of the amount: "quinze euros", "un euro". A scale
    word comes between them, with de: "dos milions d'euros". An amount with decimals stays as written."""
    request, fields = context.request, span.fields
    amount = fields["amount"]
    if amount["fraction"]:
        raise DeclinedReading("no source gives the reading of the cents")
    currency = currency_table(request)[fields["currency"]]
    integer = amount["integer"] or "0"
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        words = f"{SPELLER.cardinal(integer, Features(), request)} {scale} {of(currency_name(currency, 'other'))}"
    else:
        gender = request.data["currency_genders"].get(fields["currency"])
        name = currency_name(currency, plural_category(request, integer))
        words = before_noun(counted(integer, gender, request), name)
    return signed(words, amount["sign"], request)


@dataclass(frozen=True)
class Ordinal:
    """`1r`, `2n`, `4t`, `5è`, `2a`: a whole number and a letter of `ordinal_marks` that is the last letter of the
    ordinal word of the number, in the gender of the letter. A full stop after the letter is part of the ordinal
    when a lowercase word follows it: "Abreviacions", 8, "És optatiu posar punt després de la lletra", "1r. 1a.". At
    the end of a sentence one full stop ends both (section 3.2, "només s'escriu un punt"), so it stays."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        for number in numbers_in(text, request):
            marker = text[number.end:number.end + 1]
            if number.sign or number.fraction is not None or marker not in marks \
                    or not is_bounded(text, number.start, number.end + 1):
                continue
            try:
                word = SPELLER.ordinal(number.integer, Features(gender=GrammaticalGender(marks[marker])), request)
            except DeclinedReading:
                word = ""
            end = number.end + 1
            if re.match(r"\.\s+[^\W\d_]", text[end:]) and text[end:].split(maxsplit=1)[1][0].islower():
                end += 1
            yield Span(number.start, end, Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name,
                       keep=not word.endswith(marker))


@dataclass(frozen=True)
class KeptMeasure:
    """A number and a unit symbol that every language writes the same way, which the CLDR units of the variety do not
    read, as `35 mm`, stays as written, as on a tag with no file (design section 6.1). CLDR 49 `ca` names the
    millimetre "mil·límetre", and the core reads no unit name with the middle dot."""
    name: str = "kept_measure"
    form: Form = Form.MEASURE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        table = FrozenMap({**{key: data[key] for key in ("number_marks", "dimension_marks", "symbols")},
                           "units": written_shapes()["units"]})
        kept = Request(request.tag, Variety(request.variety.tag), replace(request.language, data=table),
                       request.params)
        for span in SHARED["measure"].find(text, tokens, kept):
            yield replace(span, keep=True)


@dataclass(frozen=True)
class KeptGrouped:
    """A whole number with a group mark before a lowercase word, as in `2.000 pessetes`, stays as written when its
    words change in the feminine: the file does not know the gender of the word. A number with no group mark reads
    as on a tag with no file."""
    name: str = "kept_grouped"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        group = request.data["number_marks"]["Latn"][0]["group"]
        for number in numbers_in(text, request):
            if number.fraction is not None or group not in text[number.start:number.end] \
                    or not (text.startswith(" ", number.end) and text[number.end + 1:number.end + 2].islower()):
                continue
            if gendered(SPELLER.cardinal(number.integer, Features(), request)):
                yield Span(number.start, number.end, Form.CARDINAL,
                           FrozenMap({"digits": number.integer, "sign": number.sign, "lead": "", "prefix": "",
                                      "suffix": "", "script": number.script}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptDate:
    """A numeric date such as `12/03/2024`, kept as written: the file reads no date, so the span keeps its digits
    from the cardinal recognizer, as the core language does (design section 6.1)."""
    name: str = "kept_date"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in SHARED["date_numeric"].find(text, tokens, request):
            written = text[span.start:span.end]
            yield Span(span.start, span.end, Form.CARDINAL,
                       FrozenMap({"digits": re.sub("[^0-9]", "", fold_digits(written)), "sign": "", "lead": "",
                                  "prefix": "", "suffix": "", "script": digit_script(written)}),
                       recognizer=self.name, keep=True)


LANGUAGE = LanguageSpec(
    code="ca",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], KeptDate(), Money(scale_before_symbol=True), SHARED["kept_money"],
                 SHARED["percent"], SHARED["measure"], KeptMeasure(), SHARED["fraction"], Ordinal(),
                 OrdinalStop(), SHARED["abbreviation"], SHARED["space_groups"], SHARED["decimal"],
                 KeptGrouped(), SHARED["cardinal"], SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.FRACTION: speak_fraction, Form.ORDINAL: speak_ordinal,
        Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
        Form.DATE: speak_cldr_date, Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
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
