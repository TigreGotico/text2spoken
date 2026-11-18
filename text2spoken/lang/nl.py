"""Dutch: nl-NL, the default variety, nl-BE and nl-SR.

The sources are the advice pages of the Nederlandse Taalunie (taaladvies.net), the advice pages of Genootschap Onze Taal
(onzetaal.nl/taalloket), the Dutch Wiktionary and CLDR 49.

Cardinals come from ovos-number-parser (design section 5.4). Its words follow Taaladvies.net,
"Aaneenschrijven van telwoorden (algemeen)", Hoofdtelwoorden: "21 eenentwintig", "43 drieënveertig", "800 achthonderd",
"135 honderdvijfendertig", "101 honderdeen of honderdeneen". The number 1 alone reads "één": Onze Taal, "een van de /
één van de", "Eén is juist als het telwoord één bedoeld is en er ook nadruk op één ligt", with "Ik moet rijden, dus ik
neem maar één biertje. (duidelijker)". A digit writes the numeral and never the article, and a digit that a reader sees
is a count that the speaker stresses. The same Taaladvies.net page puts a space after "duizend": "Na het woord
duizend (en samenstellingen hiermee, zoals vierduizend) staat een spatie", with "vierduizend twee" and "zesduizend
achtentwintig". Onze Taal, "Getallen uitschrijven", says "Na duizend komt een spatie" and "Deze regel geldt zowel voor
hoofdtelwoorden als voor rangtelwoorden". ovos-number-parser and CLDR RBNF `nl` write no space there, as in
"tweeduizenddriehonderdvijftig", so the file puts it in a cardinal, an ordinal and a year: "tweeduizend
driehonderdvijftig", "tweeduizend tweeëntwintigste".

A minus sign reads "min": CLDR RBNF `nl`, `spellout-cardinal`, `-x: min →→`, and Wiktionary, "min", "minus, verminderd
met (-)". `digit_words` holds the CLDR RBNF words of 0 to 9, with "één" for 1 by the Onze Taal rule above. A number
after the lead `nr. ` reads "nummer" (Wiktionary, "nr.", "afkorting van nummer"), and its digits read one by one when
the first is 0.

An ordinal is written as the number and `e`, `de` or `ste`: Taaladvies.net, "1°, 2°, 3° / 1ᵉ, 2ᵉ, 3ᵉ / 1ste, 2de, 3de /
1e, 2e, 3e", "Correcte weergaven zijn 1ste, 2de, 3de en 1e, 2e, 3e [...] Tussen de cijfers en de letters komt geen
koppelteken". Onze Taal, "1ste / 1e", gives "1ste, 2de, 8ste, 12de, 1000ste" and "1e, 2e, 8e, 12e, 1000e". The ending
`e` goes with every number. `de` and `ste` go with the number whose ordinal word ends in them: "In samengestelde
rangtelwoorden ga je van het laatste deel uit: negenhonderdzevende, driehonderdachtste, honderdeneerste" (Onze Taal,
"Honderdeneende / honderdeneerste"). So `ste` follows a number that ends in 1 or 8 after a ten digit 0, or in 00, or
that has a ten digit of 2 or more, and `de` follows the others: `3de`, `21ste`, `12de`, `100ste`. Any other ending, as
in `3ste`, stays as written. The ordinal words come from CLDR RBNF `nl`, `spellout-ordinal`, which writes
"honderdeerste" (Onze Taal gives "honderdeerste" as correct) and "honderdtweede". ovos-number-parser writes
"honderdeenste" and "honderdtweeste", so the file does not read ordinals through it. RBNF writes the ordinal of a
million as "eenmiljoenste", and Taaladvies.net writes "4 000 000e vier miljoenste" with no "een", so an ordinal above
999999 stays as written.

A decimal reads the CLDR RBNF `nl` rule `x.x: ←← komma →→` of `spellout-cardinal`: the whole part, "komma", then each
digit of the decimal part, so `3,14` reads "drie komma één vier" and the zero of `2,50` stays. The decimal mark is the
comma (Taaladvies.net, "Komma of punt bij decimale getallen": "We zetten een komma voor decimalen"), and the group mark
is the full stop (Onze Taal, "Komma of punt in getal": "In het Nederlands komen punten voor in hele getallen van vier
cijfers of meer. Je gebruikt ze om de cijfers per drie te groeperen"). Taaladvies.net, "10.000.000 / 10 000 000", gives
the space of the ISO norm too, "De ISO-norm en de BIN-norm schrijven de spatie als scheidingsteken voor (10 000 000),
maar in de praktijk is ook de schrijfwijze met punten gebruikelijk". So `1 000 000` reads "één miljoen" and `12 000`
"twaalfduizend", alone, in an amount and in a measure, as in `€ 12 000` and `10 000 km`. A digit run that continues the
groups after one space or one mark, as in the phone number `+31 20 123 4567`, and a first group that starts with 0, as
in `020 123 456`, show no number of groups, so each group reads as it would alone. A date splits into groups of one, two
or four digits, so it holds no group of three after a space. An amount reads the groups and a decimal comma after them
whole: the same page writes "$ 34 898 456,78", and `€ 12 000,50` reads "twaalfduizend euro vijftig". No group of a
number of groups reads alone as an amount. An amount or a measure whose whole part starts with 0 and holds more
digits, as in `€ 05,00` and `012 000 kg`, stays as written, and so does a run whose first group starts with 0 and
that has a decimal comma, as in `012 000,5`. Outside an amount, a number with spaces between its groups and a decimal
comma, a percent sign or a dimension mark stays as written.

A fraction is a cardinal and an ordinal, written apart: Taaladvies.net, "Aaneenschrijven van telwoorden", Breukgetallen:
"Bij breuken is de teller een hoofdtelwoord en de noemer een rangtelwoord [...] Teller en noemer worden los van elkaar
geschreven", "Twee derde van de tekst", and "Het rangtelwoord in de noemer krijgt meestal geen meervouds -n". The
numerator 1 reads "een", as Onze Taal, "telwoord", writes "Breuken bestaan uit een hoofdtelwoord en een rangtelwoord:
een derde, drie vierde". 1/2 stays as written: its word "half" takes the form "halve" before some nouns (Wiktionary,
"half", "een halve fles water"), and the file does not know the noun. A mixed number of a half with no word after it
reads the whole part and "en een half": Onze Taal, "Hoe schrijf je 2½ in letters: tweeënhalf, twee en half,
tweeëneenhalf of twee en een half?" (https://onzetaal.nl/taalloket/twee): "Zowel tweeënhalf als twee en een half is
juist", and "bij hogere getallen een voorkeur voor de versie met en een half". Before a noun
the half inflects as 1/2 does ("tweeënhalve / twee en een halve"), so a mixed number before a word stays as written,
as does a mixed number of another fraction, for which no source gives a reading. `1 1/2` stays as written: Dutch says
"anderhalf" (Taaladvies, "het afgelopen anderhalf jaar / de afgelopen anderhalf jaar": "het afgelopen anderhalf uur"),
which the file does not give.

A percentage reads the number and "procent" (Taaladvies.net, "Een percentage van 25 procent"; Wiktionary, "procent",
"een honderdste deel, weergegeven met symbool %").

An expression reads `+` as "plus", `−` as "min" and `=` as "is": Wiktionary, "plus", "Een plus een is twee", and "min",
"minus, verminderd met (-)".

Unit words come from CLDR 49 (`cldr-units-full`, the `long` patterns of the variety): `5 km` reads "vijf kilometer". The
unit stays singular after a number, as Taaladvies.net, "Enkelvoudsvorm / meervoudsvorm bij hoeveelheidsaanduidende
zelfstandige naamwoorden (algemeen)", gives: "vijfhonderd meter, drie hectare [...] tien euro", and a time unit takes
the plural, "veertig dagen [...] zoveel seconden". The CLDR names agree. `unit_symbols` names the symbols of letters
only that read as units, which Taaladvies.net, "Cm. / cm, kg. / kg", calls symbols: "cm, kg, km, h enzovoort". A measure
with a dimension mark, as in `3 × 4 m`, stays as written, because no source gives the word for the mark.

Currency names and symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of the variety). `15 €` and `€ 15`
read "vijftien euro", as the name after a number stays singular ("tien euro", above). Taaladvies.net, "Euro: valutateken
voor of achter het bedrag?", names the signs: "de tekens voor het Britse pond (£), de dollar ($), de Japanse yen (¥) en
de euro (€)". So in nl-NL and nl-BE `$` reads "dollar", where CLDR `nl` gives `$` to no currency and names USD
"Amerikaanse dollar", and `¥` reads "Japanse yen", where CLDR shares it between the yen and the yuan. In nl-SR, CLDR
`nl_SR` gives `$` to the Surinamese dollar, and the file keeps it. `EUR` after an amount reads as the euro too
(Taaladvies.net, "Euro / EUR / euroteken": "377 EUR"). A minus sign after the symbol reads "min" before the amount:
Taaladvies.net, "Euro: – € 12 / € -12", "Voor negatieve bedragen is het aan te bevelen € -12 te schrijven", and "euro
voluit te schrijven: -12 euro". A whole amount written `€ 5,–`, `€ 5,-` or `€ 5,00` reads "vijf euro": Taaladvies.net,
"Euro: komma en streepje in de notatie van hele bedragen?", "Komt er achter een bedrag in hele euro's een komma met twee
nullen (€ 5,00), een komma met een streep (€ 5,–) of niets (€ 5)? [...] De drie notaties zijn correct". One hyphen or
two type the dash too, as in `€ 5,-` and `€ 5,--`. An amount in
euros with two decimals reads the euros and then the cents: Onze Taal, "Euro / euro / Euro's / euro's",
"Als je een bedrag van € 15,50 ziet staan, spreek je dat uit als 'vijftien euro en vijftig cent' of 'vijftien euro
vijftig'", the short form, which the file reads. Below one euro the amount reads in cents: "Je kunt dus gerust spreken
van 'een blikje frisdrank van vijftig cent'", so `€ 0,50` reads "vijftig cent". The `subunits` table names the cent of
the euro. The word "euro" after an amount reads as the sign does, so `2,50 euro` reads "twee euro vijftig": Onze
Taal writes the name after the amount, "vijftien euro vijftig". Another amount with decimals reads as a decimal before
the currency name. A scale word after the amount
reads before the currency name: Onze Taal, "Getallen uitschrijven", "25.000.000 euro: 25 miljoen euro, € 25 miljoen".

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`) of the variety.

A title reads as its full word: Taaladvies.net, "Dr, ir, mr / dr., ir., mr.", "Schrijf dus dr., drs., ing., ir., lic.,
mr., prof. [...] We spreken de afkortingen uit als de woorden waar ze voor staan: doctor, doctorandus, ingenieur,
licentiaat, meester, professor". `dhr.` reads "de heer" (Taaladvies.net, "Afkortingen: gebruik (algemeen)", "de heer in
plaats van dhr."; Wiktionary, "dhr.", an abbreviation of "de heer") and `mevr.` "mevrouw" (Wiktionary, "mevr.", an
abbreviation of "mevrouw"). These abbreviations are written in lowercase, and a capital starts a sentence, so the
capital form reads the word with a capital. `ing.` also abbreviates "ingenaaid" and "ingeënt" (Wiktionary, "ing."), so
it reads only before a capital, as a title before a name. `Mr.` with a capital stays as written, because it also writes
the English title. The other abbreviations come from Wiktionary: "bijv." and "bv." ("bijvoorbeeld"; Taaladvies.net lists
"bv. of bijv."), "enz." ("de afkorting van enzovoort"), "o.a." ("onder andere"), "d.w.z." ("dat wil zeggen"), "i.p.v."
("in plaats van"), "m.b.t." ("met betrekking tot"), "ca." ("circa"), "evt." ("eventueel") and, before a number, "blz."
("bladzijde"). "enz." at the end of a sentence keeps its full stop.

A year right after `in het jaar` or `anno` (`year_words`), with one space or one no-break space between, as in `in het
jaar 1998`, reads the CLDR RBNF `nl` rule `spellout-numbering-year`: "negentienachtennegentig" and "tweeduizend
zesentwintig". Onze Taal, "Hoe spreek je 2026 uit?", gives this reading: "Jaartallen tot 2000, zoals 1940 en 1998,
spreek je vaak verkort uit [...] 'negentienhonderdachtennegentig' tot 'negentien-achtennegentig'", "Die verkorte vormen
zijn bij jaartallen de standaarduitspraak geworden", and "Sinds 2000 gebruiken we weinig verkorte vormen meer [...]
'tweeduizend zesentwintig'". Taaladvies.net, "Jaartallen voluit", writes a year by the rules of other numbers, so a year
takes the space after "duizend" too: "Jaartallen volgen dezelfde regels voor aaneenschrijven als gewone telwoorden". The
same Onze Taal page reads the number in full in other contexts, "1940 euro klinkt bijvoorbeeld als
'negentienhonderdveertig euro'", so a number with no year word before it reads as a cardinal. After `jaar` alone, after
another preposition or after a mark, a number is often a count, as in `vorig jaar 1450 verkeersdoden`, `gedurende het
jaar 1450 bezoekers` and `het jaar, 1450 mensen`, so `jaar` needs `in het` right before it.

A numeric date stays as written, because the plain reading has no evidence of its field order. With an SSML say-as
`date`, the markup gives that evidence, and the date reads through `ovos_date_parser.spoken_date`: `09-11-2026` reads
"negen november tweeduizend zesentwintig". A clock time such as `14.30 uur` or `14:30` is no number, so it stays as
written."""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.currencies import currency_name, currency_symbols, currency_table
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.numbers import SIGNS, Number, written_amount
from text2spoken.core.recognizers import (SHARED, SPACE_GROUPS, amount_words, numbers_in, signed,
                                          speak_abbreviation, speak_cardinal, speak_decimal, speak_expression,
                                          speak_lexicon, speak_ordinal, speak_percent, speak_spoken_date)
from text2spoken.core.recognizers import Abbreviation as CoreAbbreviation
from text2spoken.core.recognizers import Money as CoreMoney, speak_fraction as core_speak_fraction
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.tokens import Token, digit_script, fold_digits, is_bounded, is_word_char
from text2spoken.core.units import unit_reading, units_at
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, FrozenMap, Form, freeze

LARGEST_ORDINAL = 999999
"""The largest ordinal that reads: RBNF writes "eenmiljoenste" for 1000000, and no source writes the "een"."""

FRACTION_ONE = "een"
"""The numerator 1 of a fraction, as Onze Taal writes "een derde"."""

WHOLE_AMOUNT_MARKS = (",--", ",–", ",-")
"""The comma and the dash after a whole amount in euros, as in `€ 5,–`, where two hyphens or one also type the
dash."""

WORD_JOINERS = "'\u2019-\u2010"
"""The apostrophe, the right single quotation mark, the hyphen-minus and the hyphen, which join a suffix or a second
word to a word, as in `euro's` and `euro-cent`."""

GROUP_SPACES = " \u00a0\u202f"
"""The spaces between the groups of a number: the space, the no-break space and the narrow no-break space."""

DIGIT_BEFORE = re.compile("[0-9][ \u00a0\u202f/:.,–-]?$")
DIGIT_AFTER = re.compile("[ \u00a0\u202f/:.,–-]?[0-9]")
"""A digit run that continues a number of groups after one space or one mark, as in a phone number."""

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "min", "+": "plus"},
    "digit_words": ["nul", "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen"],
    "decimal_word": "komma",
    "mixed_word": "en",
    "mixed_half": {"other": "een half"},
    "leads": {"nr. ": "nummer", "Nr. ": "Nummer"},
    "ordinal_marks": ["ste", "de", "e"],
    "percent": {"signs": ["%"], "position": "after", "word": "procent"},
    "currency_symbols": ["EUR"],
    "currencies": {"JPY": {"symbols": ["¥"]}},
    "subunits": {"EUR": "cent"},
    "currency_words": {"euro": "EUR", "Euro": "EUR", "EURO": "EUR"},
    "year_words": ["in het jaar", "anno"],
    "scales": {"miljoen": "miljoen", "miljard": "miljard"},
    "unit_symbols": ["kg", "g", "km", "m", "cm", "mm", "l", "ml"],
    "dimension_marks": ["x", "×"],
    "operators": {"+": "plus", "−": "min", "=": "is"},
    "patterns": {"expression": "[-−+]?[0-9]+(?: ?[+−=] ?[-−+]*[0-9]+)+"},
    "titles": {"ing.": "ingenieur", "Ing.": "Ingenieur"},
    "abbreviations": {"dr.": "doctor", "Dr.": "Doctor", "drs.": "doctorandus", "Drs.": "Doctorandus",
                      "ir.": "ingenieur", "Ir.": "Ingenieur", "prof.": "professor", "Prof.": "Professor",
                      "mr.": "meester", "dhr.": "de heer", "Dhr.": "De heer", "mevr.": "mevrouw", "Mevr.": "Mevrouw",
                      "bijv.": "bijvoorbeeld", "bv.": "bijvoorbeeld", "enz.": "enzovoort", "o.a.": "onder andere",
                      "d.w.z.": "dat wil zeggen", "i.p.v.": "in plaats van", "m.b.t.": "met betrekking tot",
                      "ca.": "circa", "evt.": "eventueel"},
    "sentence_final": ["enz."],
    "number_abbreviations": {"blz.": "bladzijde"},
    "symbols": {"%": "percent", "€": "money", "$": "money", "£": "money", "¥": "money", "°": "measure",
                "×": "measure"},
})

DOLLAR = {"currencies": {"USD": {"symbols": ["$"], "one": "dollar", "other": "dollar"}}}
"""`$` is the dollar in the Netherlands and Belgium (Taaladvies.net, "de dollar ($)")."""

VARIETIES = (
    Variety("nl-NL", freeze(DOLLAR)),
    Variety("nl-BE", freeze(DOLLAR)),
    Variety("nl-SR"),
)


def ordinal_ending(number: int) -> str:
    """The ending `ste` or `de` of the ordinal word of a number, by its last two digits."""
    last = number % 100
    return "ste" if last == 0 or last >= 20 or last in (1, 8) else "de"


def space_after_thousand(words: str) -> str:
    """The number words with a space after "duizend" where a word follows in the same number word, as Dutch writes it:
    "vierduizendtwee" gives "vierduizend twee". The ordinal "duizendste" keeps its one word."""
    first, *rest = words.split("duizend")
    parts = [first]
    for part in rest:
        joined = part[:1].isalpha() and part.split(" ", 1)[0] != "ste"
        parts.append(("duizend " if joined else "duizend") + part)
    return "".join(parts)


class DutchSpeller:
    """Cardinals through ovos-number-parser, ordinals and years through CLDR RBNF, and decimals and fractions built
    from both."""

    def __init__(self):
        self.words = OvosNumberSpeller({})
        self.rbnf = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return space_after_thousand(self.words.cardinal(digits, features, request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or value > LARGEST_ORDINAL:
            raise DeclinedReading(f"no source writes the ordinal of a number above {LARGEST_ORDINAL}")
        return space_after_thousand(self.rbnf.ordinal(digits, features, request))

    def year(self, digits: str, features: Features, request: Request) -> str:
        return space_after_thousand(self.rbnf.year(digits, features, request))

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", features, request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        top = FRACTION_ONE if bounded_integer(numerator) == 1 else self.cardinal(numerator, features, request)
        if bounded_integer(denominator) == 2:
            return f"{top} half"
        return f"{top} {self.ordinal(denominator, features, request)}"


SPELLER = DutchSpeller()


def is_group_run(folded: str, start: int, end: int, leading_zero: bool = False) -> bool:
    """Whether the run of digit groups from `start` to `end` is one number: no digit run continues it, and its first
    group does not start with 0, as the phone number `020 123 4567` does, unless `leading_zero` is true. The groups of
    another run read alone."""
    return (leading_zero or folded[start] != "0") and not DIGIT_BEFORE.search(folded, 0, start) \
        and not DIGIT_AFTER.match(folded, end)


def spaced_numbers(text: str, leading_zero: bool = False) -> tuple[Number, ...]:
    """The numbers written with a space between groups of three digits, as in `12 000`, and with a decimal comma
    after the groups, as in `12 000,50`. A sign right before the digits belongs to the number. With `leading_zero`,
    a run whose first group starts with 0, as in `012 000`, is a number too."""
    folded = fold_digits(text)
    found = []
    for match in SPACE_GROUPS.finditer(folded):
        start, end = match.span()
        script = digit_script(text[start:end])
        integer, _, fraction = match.group().partition(",")
        if script is None or not any(space in integer for space in GROUP_SPACES) \
                or any(space in fraction for space in GROUP_SPACES) \
                or not is_group_run(folded, start, end, leading_zero):
            continue
        sign = ""
        if start and text[start - 1] in SIGNS and (start == 1 or not is_word_char(text[start - 2])):
            sign, start = SIGNS[text[start - 1]], start - 1
        elif start and is_word_char(text[start - 1]):
            continue
        found.append(Number(start, end, sign, re.sub("[^0-9]", "", integer), fraction or None, script))
    return tuple(found)


@dataclass(frozen=True)
class SpacedMeasure:
    """`10 000 km`: a whole number with a space between its groups and a unit after it, with no space or one space
    between them. After a number and a dimension mark, as in `3 × 12 000 m`, the span takes the first number too, and
    the measure stays as written as `3 × 4 m` does. A measure whose first group starts with 0, as in `012 000 kg`,
    stays as written, so that no group reads alone."""
    name: str = "spaced_measure"
    form: Form = Form.MEASURE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in spaced_numbers(text, leading_zero=True):
            if number.fraction is not None:
                continue
            start, relation, amount = number.start, "", number.amount()
            before = text[:number.start].rstrip(GROUP_SPACES)
            if before[-1:] in request.data["dimension_marks"]:
                head = before[:-1].rstrip(GROUP_SPACES)
                first = next((n for n in (*spaced_numbers(text), *numbers_in(text, request)) if n.end == len(head)),
                             None)
                if first is None:
                    continue
                start, relation, amount = first.start, "dimension", (first.amount(), amount)
            for at in (number.end, number.end + 1):
                if at > number.end and text[number.end:at] not in GROUP_SPACES:
                    break
                unit = next((u for u in units_at(text, at, request)
                             if at + len(u) == len(text) or not (is_word_char(text[at + len(u)])
                                                                 or text[at + len(u)] == "/")), None)
                if unit is not None:
                    yield Span(start, at + len(unit), Form.MEASURE,
                               FrozenMap({"amount": amount, "relation": relation, "unit": unit, "prefix": "",
                                          "suffix": ""}), recognizer=self.name, keep=number.integer.startswith("0"))
                    break


@dataclass(frozen=True)
class SpacedCardinal:
    """`12 000`, `1 000 000`: a whole number with a space between its groups, with no letter after it and no sign of
    the `symbols` table next to it. A currency sign before it is the exception: an amount reads that sign, as in
    `1€ 12 000`, so the groups after it read as a cardinal. So is a percent sign after a number before it: the
    percentage reads that sign, as in `50% 1 000`, and a second pass, which sees its words, reads the groups too.
    `KeptGroups` after it keeps the others as written."""
    name: str = "spaced_cardinal"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        symbols = request.data["symbols"]
        for number in spaced_numbers(text):
            if number.fraction is not None:
                continue
            head = text[:number.start].rstrip(GROUP_SPACES)
            before = head[-1:]
            read_sign = unicodedata.category(before) == "Sc" \
                or (symbols.get(before) == "percent" and head[:-1].rstrip(GROUP_SPACES)[-1:].isdecimal())
            after = number.end + (text[number.end:number.end + 1] in GROUP_SPACES)
            if (before in symbols and not read_sign) or text[after:after + 1] in symbols \
                    or (text[number.end:number.end + 1] and is_word_char(text[number.end])):
                continue
            yield Span(number.start, number.end, Form.CARDINAL,
                       FrozenMap({"digits": number.integer, "sign": number.sign, "lead": "", "prefix": "",
                                  "suffix": "", "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class KeptGroups:
    """A number with a space between its groups that no other recognizer of the file reads, as in `12 000,5 liter`,
    kept as written so that no recognizer reads one group alone. A run of groups that a digit run continues, or whose
    first group starts with 0, as in the phone number `020 123 4567`, is no number of groups, so its groups read as
    cardinals. A run whose first group starts with 0 and that has a decimal comma, as in `012 000,5 kg`, is no phone
    number, so it stays as written. A run that a letter joins, as in `Type A12 000 kg`, is part of a code and stays as
    written too."""
    name: str = "kept_groups"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        folded = fold_digits(text)
        for match in SPACE_GROUPS.finditer(folded):
            start, end = match.span()
            script = digit_script(text[start:end])
            integer, comma, _ = match.group().partition(",")
            leading_zero = bool(comma) and len(re.sub("[^0-9]", "", integer)) > 1
            if script is None or not is_group_run(folded, start, end, leading_zero):
                continue
            yield Span(start, end, Form.CARDINAL,
                       FrozenMap({"digits": re.sub("[^0-9]", "", match.group()), "sign": "", "lead": "", "prefix": "",
                                  "suffix": "", "script": script}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptDate:
    """A numeric date such as `12-03-2024`, kept as written: no source of the file gives its words, so the span
    keeps its digits from the cardinal recognizer, as the core language does (design section 6.1)."""
    name: str = "kept_date"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in SHARED["date_numeric"].find(text, tokens, request):
            written = text[span.start:span.end]
            yield Span(span.start, span.end, Form.CARDINAL,
                       FrozenMap({"digits": re.sub("[^0-9]", "", fold_digits(written)), "sign": "", "lead": "",
                                  "prefix": "", "suffix": "", "script": digit_script(written)}),
                       recognizer=self.name, keep=True)


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 right after an entry of the `year_words` table, in any case, with one space, one
    no-break space or one narrow no-break space between them, as in `in het jaar 1998` and `Anno 1650`. After `jaar`
    alone, after another preposition, after a mark, after a line break or after two spaces, a number is often a count,
    as in `vorig jaar 1450 verkeersdoden`, `gedurende het jaar 1450 bezoekers` and `het jaar, 1450 mensen`, so it
    reads as a cardinal."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None or number.end - number.start != 4 \
                    or not 1000 <= int(number.integer) <= 2099 or not is_bounded(text, number.start, number.end):
                continue
            if text[number.start - 1:number.start] in GROUP_SPACES \
                    and any(text[max(0, number.start - len(phrase) - 1):number.start - 1].lower() == phrase
                            and is_bounded(text, number.start - len(phrase) - 1, number.start - 1)
                            for phrase in request.data["year_words"]):
                yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": number.integer, "suffix": ""}),
                           recognizer=self.name)


@dataclass(frozen=True)
class Ordinal:
    """`1e`, `3de`, `21ste`: a whole number and an ending of `ordinal_marks` that agrees with its ordinal word."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None:
                continue
            marker = next((m for m in request.data["ordinal_marks"] if text.startswith(m, number.end)), None)
            if marker is None or not is_bounded(text, number.start, number.end + len(marker)):
                continue
            value = bounded_integer(number.integer)
            if marker != "e" and (value is None or ordinal_ending(value) != marker):
                continue
            yield Span(number.start, number.end + len(marker), Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation(CoreAbbreviation):
    """The shared abbreviations, where a key that one mark joins to a word or a number before it, as in `0-blz.` and
    `4_Dr.`, stays as written. A key joined to a digit would wait on the digit while the number waits on the key,
    and a second pass, which reads the number as a word, would read both."""

    def refuses(self, text: str, position: int, table: str, data) -> bool:
        return position >= 2 and not text[position - 1].isspace() and not is_word_char(text[position - 1]) \
            and is_word_char(text[position - 2])


@dataclass(frozen=True)
class Money(CoreMoney):
    """The shared money recognizer, with a negative amount after the symbol, as in `€ -12`, the comma and the dash
    of a whole amount, as in `€ 5,–`, and an amount with a space between its groups, as in `€ 12 000`. An amount
    whose whole part starts with 0 and holds more digits, as in `€ 05,00` and `€ 012 000,50`, stays as written, so
    that no group reads alone."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in (*super().find(text, tokens, request), *self._negative(text, tokens, request),
                     *self._words(text, tokens, request)):
            mark = next((mark for mark in WHOLE_AMOUNT_MARKS if text.startswith(mark, span.end)), "")
            end = span.end + len(mark)
            if mark and not span.fields["amount"]["fraction"] and (end == len(text) or not is_word_char(text[end])):
                span = replace(span, end=end)
            integer = span.fields["amount"]["integer"]
            if len(integer) > 1 and integer.startswith("0"):
                span = replace(span, keep=True)
            yield span

    def numbers(self, text: str, tokens: Sequence[Token], request: Request) -> Sequence[Number]:
        """The numbers of the text, where a number with a space between its groups replaces the numbers of its
        groups, also when its first group starts with 0, as in `€ 012 000`."""
        folded = fold_digits(text)
        runs = [match.span() for match in SPACE_GROUPS.finditer(folded)
                if is_group_run(folded, *match.span(), leading_zero=True)]
        return (*(number for number in numbers_in(text, request)
                  if not any(start < number.end and number.start < end for start, end in runs)),
                *spaced_numbers(text, leading_zero=True))

    def _words(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """`2,50 euro`: an amount and a currency word of `currency_words` after it, with one space between them. When
        letters, an apostrophe or a hyphen continue the word, as in `2,50 euro's` and `2,50 euro-cent`, an amount
        with a decimal part stays as written with the word, because its cents would read after the suffix. A whole
        amount reads, as in `5 euro's`. The currency name reads in lower case, so before a suffix in capitals, as in
        `5 EURO'S`, only the number reads and the word stays as written."""
        for number in self.numbers(text, tokens, request):
            for word, code in request.data["currency_words"].items():
                end = number.end + 1 + len(word)
                if text[number.end:end] not in (f" {word}", f"\u00a0{word}") \
                        or not is_bounded(text, number.start, number.end):
                    continue
                glued = end
                while glued < len(text) and (is_word_char(text[glued]) or text[glued] in WORD_JOINERS):
                    glued += 1
                fields = FrozenMap({"amount": number.amount(), "currency": code, "written_symbol": word, "scale": "",
                                    "prefix": "", "suffix": ""})
                if glued > end and number.fraction is not None:
                    yield Span(number.start, glued, Form.MONEY, fields, recognizer=self.name, keep=True)
                elif is_bounded(text, number.start, end) and text[end:glued] == text[end:glued].lower():
                    yield Span(number.start, end, Form.MONEY, fields, recognizer=self.name)

    def _negative(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in self.numbers(text, tokens, request):
            if not number.sign:
                continue
            for symbol, code in currency_symbols(request):
                start = next((number.start - len(gap) - len(symbol) for gap in ("", " ", "\u00a0")
                              if text[:number.start].endswith(symbol + gap)), None)
                if start is not None and is_bounded(text, start, number.end):
                    yield Span(start, number.end, Form.MONEY,
                               FrozenMap({"amount": number.amount(), "currency": code, "written_symbol": symbol,
                                          "scale": "", "prefix": "", "suffix": ""}), recognizer=self.name)
                    break


def speak_fraction(span: Span, context: SpanContext) -> str:
    """The fraction, except 1/2: its word "half" takes the form "halve" before some nouns, and the file does not know
    the noun. A mixed number reads through the core reading, which reads only a half with no word after it. One
    and a half is the one word "anderhalf", which the file does not give, so `1 1/2` stays as written."""
    if span.fields["whole"] == "1":
        raise DeclinedReading("one and a half is anderhalf, which the file does not give")
    if span.fields["whole"]:
        return core_speak_fraction(span, context)
    if bounded_integer(span.fields["denominator"]) == 2:
        raise DeclinedReading("the Dutch word for a half agrees with the noun after it")
    return core_speak_fraction(span, context)


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount, a scale word when the text writes one, and the currency name. Zero decimals read as a whole
    amount. Two decimals of a currency in `subunits` read after the currency name, or with the subunit word when the
    whole part is zero."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    if not amount["fraction"].strip("0"):
        amount = FrozenMap({**amount, "fraction": ""})
    currency = currency_table(request)[fields["currency"]]
    subunit = request.data["subunits"].get(fields["currency"])
    fraction = amount["fraction"]
    if subunit and not fields["scale"] and len(fraction) == 2:
        amount = FrozenMap({**amount, "fraction": ""})
        cents = amount_words(FrozenMap({**amount, "integer": fraction.lstrip("0")}), request)
        if not amount["integer"].strip("0"):
            return signed(f"{cents} {subunit}", fields["amount"]["sign"], request)
        fraction_words = f" {cents}"
    else:
        fraction_words = ""
    words = amount_words(amount, request)
    if fields["scale"]:
        words = f"{words} {request.data['scales'][fields['scale']]} {currency_name(currency, 'other')}"
    else:
        words = f"{words} {currency_name(currency, plural_category(request, written_amount(amount)))}{fraction_words}"
    return signed(words, fields["amount"]["sign"], request)


def speak_year(span: Span, context: SpanContext) -> str:
    return SPELLER.year(span.fields["digits"], Features(), context.request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    if span.fields["relation"]:
        raise DeclinedReading("no source gives the Dutch word for a dimension mark")
    amount = span.fields["amount"]
    pattern, _ = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amount)))
    return pattern.replace("{0}", amount_words(amount, request))


LANGUAGE = LanguageSpec(
    code="nl",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], Money(), SHARED["kept_money"], SpacedMeasure(), SpacedCardinal(),
                 KeptGroups(), KeptDate(), SHARED["percent"],
                 SHARED["measure"], SHARED["expression"], SHARED["fraction"], Ordinal(), Year(), Abbreviation(),
                 SHARED["decimal"], SHARED["cardinal"], SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.ORDINAL: speak_ordinal, Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal,
        Form.CARDINAL: speak_cardinal, Form.YEAR: speak_year, Form.DATE: speak_spoken_date, Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER,
              Form.YEAR: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={},
    not_applicable=frozenset(OPTIONS),
)
