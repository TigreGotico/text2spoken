"""Greek: el-GR.

Cardinals come from the CLDR RBNF rule sets of `el` (design section 5.4): `spellout-cardinal-masculine`,
`spellout-cardinal-feminine` and `spellout-cardinal-neuter`. A number takes the gender of the noun that it counts. The
words that change are 1 (ένας, μία, ένα), 3 (τρεις, τρία), 4 (τέσσερις, τέσσερα), 13 and 14, the hundreds from 200
(διακόσιοι, διακόσιες, διακόσια) and 1000 (χίλιοι, χίλιες, χίλια). From 2000 up the thousands are the feminine noun
χιλιάδες, and the number before it takes the feminine in every gender, as the rule `2000:
←%spellout-cardinal-feminine← χιλιάδες` says: `3000` reads "τρεις χιλιάδες". Wikipedia, "Modern Greek grammar",
Numerals: "The numerals one, three and four are declined irregularly. Other numerals such as διακόσιοι [...] and
χίλιοι [...] are declined regularly like adjectives."

A number with no noun reads the neuter. The `el` rule set `spellout-numbering` is `0: =%spellout-cardinal-neuter=;`,
and UTS #35, Part 3, "Rule-Based Number Formatting", defines that rule set as "the default used when there is no
context for the number. Usually this is used for counting without reference to a noun". The English Wiktionary,
"δεκατρείς", Usage notes: "When counting, use the "numeral noun", neuter δεκατρία", and "δεκατέσσερις" says the same of
δεκατέσσερα. A number before a word that the lists below do not hold reads the same neuter, and `default_gender`
changes it.

The gender of a noun comes from `data/wiktionary/el_nouns.json`, which `scripts/extract_el_nouns.py` makes from the
categories "Greek masculine nouns", "Greek feminine nouns" and "Greek neuter nouns" of the English Wiktionary, with the
inflected forms of each noun, singular and plural, by case. So `3 βιβλία` reads "τρία βιβλία", `3 γυναίκες` "τρεις
γυναίκες" and `200 σκύλοι` "διακόσιοι σκύλοι". The noun may come after adjectives: Wikipedia, "Modern Greek grammar":
"Within the noun phrase, adjectives commonly precede the noun", with "the usual order ένα νέο βιβλίο". The same page
says "Adjectives agree with nouns in gender, case and number", so an adjective form of the category "Greek adjectives"
gives the gender too, when no noun of the list follows it: `3 μεγάλα κουτάκια` reads "τρία". Between two numbers a
word of `number_links` stands, and both numbers count the noun after the second: `3 ή 4 γυναίκες` reads "τρεις ή
τέσσερις γυναίκες".

The article before a number agrees with the same noun (Wikipedia, "Modern Greek grammar", Articles: "The article
agrees with the noun it modifies"), and `articles` gives its genders from the table of definite articles on that page.
The forms with σε are contractions, as the English Wiktionary, "στις", says: "contraction of σε τις". The article
decides when no noun follows, as in `στις 5` and `το 1956`. When the article and the noun disagree, the article
decides, because the noun lists also hold forms of other words. A phrase that leaves more than one gender open reads
the default gender when that gender is one of them, and else the masculine: `οι 200` reads "διακόσιοι", and so does
`200 γιατροί`, a noun of both genders that the English Wiktionary heads `{{el-noun|m|g2=f}}`, masculine first.

The case of the noun form changes the number, by the rules of CLDR (common/rbnf/el.xml on the main branch of
unicode-org/cldr): `spellout-cardinal-masculine-accusative` gives "έναν", the hundreds in "-κόσιους" and "χίλιους",
and the genitive rule sets give "ενός", "μιας", "τριών", "τεσσάρων", the hundreds in "-κοσίων", "χιλίων",
"χιλιάδων" and "εκατομμυρίων". The feminine and the neuter accusative are the nominative ("0:
=%spellout-cardinal-feminine=;"). `case_words` holds these words. A noun form that is only accusative or only
genitive gives its case, as `σκύλους` and `βιβλίων`. A form that is also nominative reads the nominative. An article
gives no case alone, because a year after a genitive article keeps its nominative, as in `του 1998`.

A day before a month name counts the feminine ημέρα, the day of the month, and day 1 is its ordinal: Βικιλεξικό,
"Πρωτομαγιά": "η πρώτη ημέρα του Μαΐου". `month_names` holds the genitive month names of CLDR 49, `el`, format
wide and abbreviated. So `4 Ιουνίου` reads "τέσσερις Ιουνίου" and `1 Μαΐου` "πρώτη Μαΐου".

The RBNF data of unicode-rbnf writes "χίλιάδες" with two accents, "εννενήντα" with two ν and 13 as "δεκατρεις" with
no accent. The core table `data/rbnf_corrections.json` gives the right words and their sources, and `RbnfSpeller`
reads it (design section 5.4).

A minus reads "μείον", the word of the RBNF rule `-x: μείον →→`. As in the other files, the hyphen of `5-10` and
`A-5` is no minus. Money, measures and an ordinal with a full stop stay as written, as for a language with no file
(design section 6.1), and so does an amount with a minus, as `-50 €` and `€ -50`.

A percentage reads its number and "τοις εκατό", the unit pattern of `concentr-percent` in the CLDR units of `el`, which
gives the unit the neuter gender: `20%` reads "είκοσι τοις εκατό" and `-5%` "μείον πέντε τοις εκατό". A decimal, a
per mille sign and two percentages that a dash joins stay as written.

A fraction reads when its denominator has a one-word name in the English Wiktionary appendix "Greek numerals",
Fraction column: 2 to 12, 20 and 100. The half is the adjective μισός, which agrees with its noun (English Wiktionary,
"μισός": "μισή ώρα", half an hour; "μισό": "μισό κιλό κρασί"). Any other name is a neuter noun, as "τρίτο", plural
"τρίτα", and "τέταρτο", plural "τέταρτα" (English Wiktionary), so its numerator reads in the neuter: `1/3` reads "ένα
τρίτο" and `3/4` "τρία τέταρτα". The plural of each name is the neuter plural of its ordinal adjective in -ος. Any
other fraction stays as written.

A numeric date reads day, month and year, as the CLDR long date format of `el`, `d MMMM y`, writes it, with the month
name of `months`, CLDR 49 format wide, in the genitive. The day is the feminine ημέρα, as above, and the year reads
in the neuter, as a number with no noun. The date adds no weekday. The core resolves the order: a field above 12 is
the day, and when both fields are 12 or below the day comes first, as in the CLDR short date format `d/M/yy`. The
decimal mark is the comma and the group mark the full stop (CLDR 49 number symbols of `el`), so `1.234` reads as one
number. A decimal stays as written.
"""
from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (GAPS, SHARED, OrdinalStop, _free_before, numbers_in, signed,
                                          speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Recognizer, Span, SpanContext
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, FrozenMap, Form, GrammaticalGender, freeze

M, F, N = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE, GrammaticalGender.NEUTER
NOMINATIVE, ACCUSATIVE, GENITIVE = "nominative", "accusative", "genitive"
MASCULINE, FEMININE, NEUTER = M.value, F.value, N.value

_HUNDREDS = ("διακόσι", "τριακόσι", "τετρακόσι", "πεντακόσι", "εξακόσι", "επτακόσι", "οκτακόσι", "εννιακόσι")

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "μείον"},
    "percent": {**written_shapes()["percent"], "word": "τοις εκατό"},
    "months": ["Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", "Ιουλίου", "Αυγούστου",
               "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"],
    "half": {
        MASCULINE: {NOMINATIVE: "μισός", ACCUSATIVE: "μισό", GENITIVE: "μισού"},
        FEMININE: {NOMINATIVE: "μισή", ACCUSATIVE: "μισή", GENITIVE: "μισής"},
        NEUTER: {NOMINATIVE: "μισό", ACCUSATIVE: "μισό", GENITIVE: "μισού"},
    },
    "fraction_names": {"3": ["τρίτο", "τρίτα"], "4": ["τέταρτο", "τέταρτα"], "5": ["πέμπτο", "πέμπτα"],
                       "6": ["έκτο", "έκτα"], "7": ["έβδομο", "έβδομα"], "8": ["όγδοο", "όγδοα"],
                       "9": ["ένατο", "ένατα"], "10": ["δέκατο", "δέκατα"], "11": ["ενδέκατο", "ενδέκατα"],
                       "12": ["δωδέκατο", "δωδέκατα"], "20": ["εικοστό", "εικοστά"], "100": ["εκατοστό", "εκατοστά"]},
    "leads": {},
    "case_words": {
        ACCUSATIVE: {"ένας": "έναν", "χίλιοι": "χίλιους", **{f"{h}οι": f"{h}ους" for h in _HUNDREDS}},
        GENITIVE: {"ένας": "ενός", "ένα": "ενός", "μία": "μιας", "τρεις": "τριών", "τρία": "τριών",
                   "τέσσερις": "τεσσάρων", "τέσσερα": "τεσσάρων", "δεκατρείς": "δεκατριών", "δεκατρία": "δεκατριών",
                   "δεκατέσσερις": "δεκατεσσάρων", "δεκατέσσερα": "δεκατεσσάρων", "χίλιοι": "χιλίων",
                   "χίλιες": "χιλίων", "χίλια": "χιλίων", "χιλιάδες": "χιλιάδων", "εκατομμύριο": "εκατομμυρίου",
                   "εκατομμύρια": "εκατομμυρίων", "δισεκατομμύριο": "δισεκατομμυρίου",
                   "δισεκατομμύρια": "δισεκατομμυρίων", "τρισεκατομμύριο": "τρισεκατομμυρίου",
                   "τρισεκατομμύρια": "τρισεκατομμυρίων",
                   **{f"{h}{end}": h.replace("όσι", "οσί") + "ων" for h in _HUNDREDS for end in ("οι", "ες", "α")}},
    },
    "articles": {
        "ο": [[MASCULINE, NOMINATIVE]], "η": [[FEMININE, NOMINATIVE]],
        "το": [[NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]], "τον": [[MASCULINE, ACCUSATIVE]],
        "τη": [[FEMININE, ACCUSATIVE]], "την": [[FEMININE, ACCUSATIVE]],
        "του": [[MASCULINE, GENITIVE], [NEUTER, GENITIVE]], "της": [[FEMININE, GENITIVE]],
        "οι": [[MASCULINE, NOMINATIVE], [FEMININE, NOMINATIVE]], "τα": [[NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]],
        "τους": [[MASCULINE, ACCUSATIVE]], "τις": [[FEMININE, ACCUSATIVE]],
        "των": [[MASCULINE, GENITIVE], [FEMININE, GENITIVE], [NEUTER, GENITIVE]],
        "στο": [[NEUTER, ACCUSATIVE]], "στον": [[MASCULINE, ACCUSATIVE]], "στη": [[FEMININE, ACCUSATIVE]],
        "στην": [[FEMININE, ACCUSATIVE]], "στου": [[MASCULINE, GENITIVE], [NEUTER, GENITIVE]],
        "στης": [[FEMININE, GENITIVE]], "στα": [[NEUTER, ACCUSATIVE]], "στους": [[MASCULINE, ACCUSATIVE]],
        "στις": [[FEMININE, ACCUSATIVE]], "στων": [[MASCULINE, GENITIVE], [FEMININE, GENITIVE], [NEUTER, GENITIVE]],
    },
    "number_links": ["ή", "έως", "ως", "μέχρι", "με"],
    "month_names": ["ιανουαρίου", "φεβρουαρίου", "μαρτίου", "απριλίου", "μαΐου", "ιουνίου", "ιουλίου", "αυγούστου",
                    "σεπτεμβρίου", "οκτωβρίου", "νοεμβρίου", "δεκεμβρίου", "ιαν", "φεβ", "μαρ", "απρ", "μαΐ", "ιουν",
                    "ιουλ", "αυγ", "σεπ", "οκτ", "νοε", "δεκ"],
})

GENDER_ORDER = (M, F, N)
CASE_ORDER = (NOMINATIVE, ACCUSATIVE, GENITIVE)
ADJECTIVE_WALK = 2
"""The adjectives that may stand between a number and its noun."""


class GreekSpeller:
    """The RBNF `el` cardinal of a gender, with the case words of `case_words`. The accusative words are masculine
    words only; the genitive words serve each gender."""

    def __init__(self):
        self.rbnf = RbnfSpeller(
            cardinal={Features(): "spellout-numbering", Features(gender=M): "spellout-cardinal-masculine",
                      Features(gender=F): "spellout-cardinal-feminine", Features(gender=N): "spellout-cardinal-neuter"},
            ordinal={Features(): "spellout-ordinal-neuter", Features(gender=M): "spellout-ordinal-masculine",
                     Features(gender=F): "spellout-ordinal-feminine", Features(gender=N): "spellout-ordinal-neuter"})

    @staticmethod
    def _respell(words: str, features: Features, request: Request) -> str:
        if features.case == GENITIVE or (features.case == ACCUSATIVE and features.gender == M):
            table = request.data["case_words"][features.case]
            return " ".join(table.get(word, word) for word in words.split())
        return words

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self._respell(self.rbnf.cardinal(digits, Features(gender=features.gender), request), features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._respell(self.rbnf.ordinal(digits, Features(gender=features.gender), request), Features(),
                             request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        raise NotImplementedError("the Greek file reads no year")

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        raise NotImplementedError("the Greek file reads no decimal")

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """A half in the gender and case of `features`, as μισή; any other fraction as the neuter numerator and the
        name of `fraction_names`, as "ένα τρίτο" and "δύο τρίτα"."""
        numerator, denominator = str(int(numerator)), str(int(denominator))
        if denominator == "2":
            gender = (features.gender or N).value
            return request.data["half"][gender][features.case or NOMINATIVE]
        singular, plural = request.data["fraction_names"][denominator]
        count = self.cardinal(numerator, Features(gender=N, case=NOMINATIVE), request)
        return f"{count} {singular if numerator == '1' else plural}"


SPELLER = GreekSpeller()

Reading = frozenset[tuple[str, str]]
"""The (gender, case) pairs that a word may have."""


@lru_cache(maxsize=1)
def _word_list() -> dict:
    path = files("text2spoken") / "data" / "wiktionary" / "el_nouns.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _readings(table: dict) -> dict[str, Reading]:
    found: dict[str, set[tuple[str, str]]] = {}
    for gender, by_case in table.items():
        for case, forms in by_case.items():
            for form in forms:
                found.setdefault(form, set()).add((gender, case))
    return {form: frozenset(pairs) for form, pairs in found.items()}


@lru_cache(maxsize=1)
def noun_readings() -> dict[str, Reading]:
    """The gender and the case of each noun form of `data/wiktionary/el_nouns.json`."""
    return _readings(_word_list()["nouns"])


@lru_cache(maxsize=1)
def adjective_readings() -> dict[str, Reading]:
    """The gender and the case of each adjective form of `data/wiktionary/el_nouns.json`."""
    return _readings(_word_list()["adjectives"])


def phrase_after(after: Sequence[str], data: FrozenMap) -> tuple[Reading | None, bool]:
    """The genders and cases that the words after a number give, and whether a month name follows it. The walk skips
    a word of `number_links` with the number after it, and up to `ADJECTIVE_WALK` adjectives; a noun form ends it."""
    nouns, adjectives = noun_readings(), adjective_readings()
    found: Reading | None = None
    walked = 0
    index = 0
    while index < len(after):
        word = after[index].lower()
        if word in data["month_names"]:
            return frozenset({(FEMININE, NOMINATIVE)}), True
        if word in data["number_links"] and index + 1 < len(after) and after[index + 1].isdigit():
            index += 2
            continue
        if word in nouns:
            return nouns[word], False
        if word in adjectives and walked < ADJECTIVE_WALK:
            found = adjectives[word] if found is None else (found & adjectives[word]) or found
            walked += 1
            index += 1
            continue
        break
    return found, False


def choose(readings: Reading, default: GrammaticalGender) -> Features:
    """One gender and case of the open ones: the default gender when it is one of them, else the first of
    `GENDER_ORDER`, and the first case of `CASE_ORDER` that the gender has."""
    genders = {gender for gender, _ in readings}
    gender = default.value if default.value in genders else next(g.value for g in GENDER_ORDER if g.value in genders)
    case = next(c for c in CASE_ORDER if (gender, c) in readings)
    return Features(gender=GrammaticalGender(gender), case=case)


def number_features(context: SpanContext) -> tuple[Features, bool]:
    """The gender and case of a number, from the noun phrase around it, and whether a month name follows it."""
    if context.hint is not None:
        return context.hint, False
    request = context.request
    default = request.params.default_gender.get(request.language.code) or request.language.default_gender
    data = request.data
    after, month = phrase_after(context.after, data)
    article = data["articles"].get(context.before[-1].lower()) if context.before else None
    if article is not None:
        pairs = frozenset(map(tuple, article))
        genders = {gender for gender, _ in pairs}
        agreeing = frozenset(pair for pair in after or () if pair[0] in genders)
        after = ((after or frozenset()) & pairs) or agreeing or frozenset((gender, NOMINATIVE) for gender in genders)
    if after is None:
        return Features(gender=default, case=NOMINATIVE), month
    return choose(after, default), month


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal in the gender and case of its noun phrase; day 1 before a month name reads its ordinal."""
    request = context.request
    features, month = number_features(context)
    digits = span.fields["digits"]
    if month and digits == "1":
        words = SPELLER.ordinal(digits, features, request)
    else:
        words = SPELLER.cardinal(digits, features, request)
    return signed(words, span.fields["sign"], request)


KEPT_FIELDS = FrozenMap(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


def kept(span: Span, name: str) -> Span:
    """`span` as a span that keeps its text and guards it from the cardinal reading (design section 6.1)."""
    return replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=name, keep=True)


def speak_date(span: Span, context: SpanContext) -> str:
    """Day, month name and year: the day in the feminine of ημέρα, day 1 as its ordinal, the month in the genitive
    of `months`, and the year in the neuter."""
    request = context.request
    fields = span.fields
    day = str(fields["day"])
    if day == "1":
        day_words = SPELLER.ordinal(day, Features(gender=F), request)
    else:
        day_words = SPELLER.cardinal(day, Features(gender=F, case=NOMINATIVE), request)
    year = SPELLER.cardinal(str(fields["year"]), Features(gender=N, case=NOMINATIVE), request)
    return f"{day_words} {request.data['months'][fields['month'] - 1]} {year}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """The amount in the neuter, the gender of τοις εκατό, then the word of the `percent` table."""
    request = context.request
    amount = span.fields["amount"]
    words = SPELLER.cardinal(amount["integer"], Features(gender=N, case=NOMINATIVE), request)
    return f"{signed(words, amount['sign'], request)} {request.data['percent']['word']}"


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction in the gender and case of the noun phrase around it, which only a half shows."""
    fields = span.fields
    features, _ = number_features(context)
    return signed(SPELLER.fraction(fields["numerator"], fields["denominator"], features, context.request),
                  fields["sign"], context.request)


DASHES = ("-", "–", "−")


@dataclass(frozen=True)
class ReadPercent:
    """A whole number before a percent sign, with no sign or a minus. A decimal, a per mille sign, a sign before
    the number and two percentages that a dash joins, as `10%-20%`, stay as written: the file has no range word. So
    does a percentage that a word character or a symbol touches from the left, as the fraction recognizer of the core
    decides, because its words would join that character."""
    name: str = "read_percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in SHARED["percent"].find(text, tokens, request):
            amount = span.fields["amount"]
            read = (isinstance(amount, FrozenMap) and not amount["fraction"] and amount["integer"]
                    and (not amount["sign"] or amount["sign"] in request.data["sign_words"])
                    and span.fields["sign_position"] == "after" and "%" in text[span.start:span.end]
                    and _free_before(text, span.start, request.data["symbols"])
                    and text[span.end:span.end + 1] not in DASHES
                    and not (span.start > 1 and text[span.start - 1] in DASHES and text[span.start - 2] in "%٪‰"))
            yield span if read else replace(span, keep=True)


@dataclass(frozen=True)
class ListedFraction:
    """A proper fraction whose denominator has a name: 2 and the keys of `fraction_names`. Any other fraction stays
    as written."""
    name: str = "listed_fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        names = request.data["fraction_names"]
        for span in SHARED["fraction"].find(text, tokens, request):
            fields = span.fields
            denominator = str(int(fields["denominator"]))
            read = (not span.keep and (denominator == "2" or denominator in names)
                    and (not fields["sign"] or fields["sign"] in request.data["sign_words"]))
            yield span if read else replace(span, keep=True)


@dataclass(frozen=True)
class Kept:
    """The spans of a shape recognizer, kept as written, as for a language with no file. A span takes the form and
    the fields of the cardinal that it guards, so that it guards the digits also when only `CARDINAL` is on."""
    shape: Recognizer
    form: Form = Form.CARDINAL

    @property
    def name(self) -> str:
        return self.shape.name

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return (kept(span, self.name) for span in self.shape.find(text, tokens, request))


@dataclass(frozen=True)
class SignedMoney:
    """A number with a sign next to a currency sign, as `-50 €` and `€ -50`, stays as written, as money does."""
    name: str = "signed_money"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        symbols = request.data["currencies"]["Sc"]["symbols"]
        for number in numbers_in(text, request):
            if not number.sign:
                continue
            for gap in GAPS:
                after = number.end + len(gap)
                before = number.start - len(gap) - 1
                if text.startswith(gap, number.end) and text[after:after + 1] in symbols:
                    yield kept(Span(number.start, after + 1, Form.CARDINAL, KEPT_FIELDS), self.name)
                    break
                if before >= 0 and text[before] in symbols and text[before + 1:number.start] == gap:
                    yield kept(Span(before, number.end, Form.CARDINAL, KEPT_FIELDS), self.name)
                    break


SHAPES = (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
          OrdinalStop(bare_stop=False))

LANGUAGE = LanguageSpec(
    code="el",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("el-GR"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["date_numeric"], ReadPercent(), ListedFraction(), *map(Kept, SHAPES),
                 SignedMoney(), SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DATE: speak_date,
                 Form.PERCENT: speak_percent, Form.FRACTION: speak_fraction},
    spellers={Form.CARDINAL: SPELLER, Form.FRACTION: SPELLER},
    genders=frozenset({M, F, N}),
    default_gender=N,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"default_gender": frozenset({"masculine", "feminine", "neuter"})},
    not_applicable=frozenset(OPTIONS) - {"default_gender"},
)
