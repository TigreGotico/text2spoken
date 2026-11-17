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

`spelling` corrects three words of the RBNF data of unicode-rbnf. It writes "χίλιάδες" with two accents and
"εννενήντα" with two ν, where CLDR on its main branch writes "χιλιάδες" and "ενενήντα", as the English Wiktionary
entries "χιλιάδα" (plural "χιλιάδες") and "ενενήντα" do. It writes 13 as "δεκατρεις" with no accent, where the
English Wiktionary writes "δεκατρείς", /ðe.kaˈtɾis/.

A minus reads "μείον", the word of the RBNF rule `-x: μείον →→`. As in the other files, the hyphen of `5-10` and
`A-5` is no minus. Money, percentages, measures, numeric dates and an ordinal with a full stop stay as written, as
for a language with no file (design section 6.1), and so does an amount with a minus, as `-50 €` and `€ -50`. The
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
from text2spoken.core.recognizers import (GAPS, SHARED, OrdinalStop, numbers_in, signed, speak_lexicon,
                                          written_shapes)
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
    "leads": {},
    "spelling": {"χίλιάδες": "χιλιάδες", "εννενήντα": "ενενήντα", "δεκατρεις": "δεκατρείς"},
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
    """The RBNF `el` cardinal of a gender, with the corrected spelling of `spelling` and the case words of
    `case_words`. The accusative words are masculine words only; the genitive words serve each gender."""

    def __init__(self):
        self.rbnf = RbnfSpeller(
            cardinal={Features(): "spellout-numbering", Features(gender=M): "spellout-cardinal-masculine",
                      Features(gender=F): "spellout-cardinal-feminine", Features(gender=N): "spellout-cardinal-neuter"},
            ordinal={Features(): "spellout-ordinal-neuter", Features(gender=M): "spellout-ordinal-masculine",
                     Features(gender=F): "spellout-ordinal-feminine", Features(gender=N): "spellout-ordinal-neuter"})

    @staticmethod
    def _respell(words: str, features: Features, request: Request) -> str:
        data = request.data
        spelled = [data["spelling"].get(word, word) for word in words.split()]
        if features.case == GENITIVE or (features.case == ACCUSATIVE and features.gender == M):
            spelled = [data["case_words"][features.case].get(word, word) for word in spelled]
        return " ".join(spelled)

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
        raise NotImplementedError("the Greek file reads no fraction")


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
    recognizers=(SHARED["lexicon"], *map(Kept, SHAPES), SignedMoney(), SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER},
    genders=frozenset({M, F, N}),
    default_gender=N,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"default_gender": frozenset({"masculine", "feminine", "neuter"})},
    not_applicable=frozenset(OPTIONS) - {"default_gender"},
)
