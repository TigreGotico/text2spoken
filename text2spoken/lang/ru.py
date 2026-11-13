"""Russian: ru-RU, the one variety, which every other ru-* tag selects through closest_lang.

Nominative cardinals come from ovos-number-parser, and the other cases from CLDR RBNF, with one rule set for each
gender and case (design section 5.4). Ordinals follow the rules of Грамматика-80 over these cardinal words. A number
agrees in gender and case with the noun it counts, and a preposition before it gives the case. The rules cite these
sources:

- Грамматика-80: Русская грамматика, т. I-II, АН СССР, 1980, by paragraph (rusgram.narod.ru).
- Розенталь: Д. Э. Розенталь, Справочник по правописанию и литературной правке, 4-е изд., 1985, by paragraph.
- Правила-2006: Правила русской орфографии и пунктуации. Полный академический справочник, 2006, by paragraph
  (orfo.ruslang.ru).

Number words take the letter ё, as Грамматика-80 § 1374 writes "трёх", "четырёх", "трём", so that a reader says
them right (Правила-2006 § 5).
"""
from __future__ import annotations

import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import SHARED, DateNumeric, numbers_in, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext, Word, context_words
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller, bounded_integer
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import (Token, fold_digits, is_bounded, is_letter, is_word_char, next_visible,
                                     one_digit_set)
from text2spoken.errors import DeclinedReading
from text2spoken.params import Form, FrozenMap, GrammaticalGender, freeze

M, F, N = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE, GrammaticalGender.NEUTER

CASES = ("nominative", "genitive", "dative", "accusative", "instrumental", "prepositional")
"""The six cases, in the order of the declension lists of the nouns."""


def _hard(stem: str, tail: str = "", genitive_plural: str | None = None) -> dict:
    """A masculine noun with a hard stem and no ending in the nominative, the type "стол" (Грамматика-80 § 1134).
    A unit name may keep a zero ending in the genitive plural: "ватт", "герц" (Розенталь § 154, п. 1)."""
    return {"gender": "masculine", "tail": tail,
            "singular": [stem, stem + "а", stem + "у", stem, stem + "ом", stem + "е"],
            "plural": [stem + "ы", genitive_plural or stem + "ов", stem + "ам", stem + "ы", stem + "ами", stem + "ах"]}


DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "\u00a0"}, {"decimal": ".", "group": "\u00a0"}]},
    "defaults": {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ",",
                 "scale": "short"},
    "sign_words": {"-": "минус", "+": "плюс"},
    "digit_words": ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"],
    "leads": {"№": "номер", "№ ": "номер"},
    "range_word": "—",
    "range_marks": ["-", "–", "—"],
    "dimension_marks": ["×"],
    "dimension_word": "на",
    "time_words": ["в", "во", "к", "ко", "до", "с", "со", "после", "по", "от"],
    "zero_minutes": "ноль-ноль",
    "copulas": ["был", "была", "было", "будет", "есть"],
    "onset_verbs": ["наступил", "наступила", "наступило", "наступит"],
    "date_adverbs": ["вот", "и", "а", "но", "да", "ведь", "же", "ну", "ещё", "не", "ли", "наконец", "уже", "тогда",
                     "скоро", "сегодня", "завтра", "вчера", "послезавтра", "позавчера"],
    "date_particles": ["да", "а"],
    "owner_prepositions": ["у", "в", "во"],
    "collective_numerals": {"2": "двое", "3": "трое", "4": "четверо"},
    "pluralia_tantum": ["суток", "саней", "ножниц", "брюк", "ворот"],
    "collective_persons": ["детей", "ребят", "людей"],
    "months": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
               "ноября", "декабря"],
    "year_noun": ["год", "года", "году", "год", "годом", "году"],
    "whole": "цел",
    "fraction_endings": {"one": ["ая", "ой", "ой", "ую", "ой", "ой"], "other": ["ых", "ых", "ым", "ых", "ыми", "ых"]},
    "decimal_denominators": ["десят", "сот", "тысячн", "десятитысячн", "стотысячн", "миллионн", "десятимиллионн",
                             "стомиллионн", "миллиардн"],
    "governed_cases": {
        "без": "genitive", "для": "genitive", "до": "genitive", "из": "genitive", "из-за": "genitive",
        "из-под": "genitive", "кроме": "genitive", "от": "genitive", "ради": "genitive", "у": "genitive",
        "около": "genitive", "после": "genitive", "вокруг": "genitive", "против": "genitive", "среди": "genitive",
        "свыше": "genitive", "более": "genitive", "менее": "genitive", "к": "dative", "ко": "dative",
        "согласно": "dative", "вопреки": "dative", "в течение": "genitive",
        "про": "accusative", "через": "accusative", "сквозь": "accusative", "над": "instrumental",
        "перед": "instrumental", "при": "prepositional", "о": "prepositional", "об": "prepositional",
    },
    "case_choices": {
        "в": ["accusative", "prepositional"], "во": ["accusative", "prepositional"],
        "на": ["accusative", "prepositional"], "за": ["accusative", "instrumental"],
        "под": ["accusative", "instrumental"], "с": ["genitive", "instrumental"], "со": ["genitive", "instrumental"],
        "между": ["instrumental", "genitive"], "по": ["accusative", "dative"],
    },
    "plural_endings": {"ами": "instrumental", "ями": "instrumental", "ьми": "instrumental", "ах": "prepositional",
                       "ях": "prepositional", "ам": "dative", "ям": "dative"},
    "ordinal_endings": ["й", "я", "е", "го", "му", "м", "ю", "х", "ми"],
    "percent": {"signs": ["%"], "position": "after", "noun": _hard("процент")},
    "currencies": {
        "RUB": {"symbols": ["₽"],
                "major": {"gender": "masculine", "tail": "",
                          "singular": ["рубль", "рубля", "рублю", "рубль", "рублём", "рубле"],
                          "plural": ["рубли", "рублей", "рублям", "рубли", "рублями", "рублях"]},
                "minor": {"gender": "feminine", "tail": "",
                          "singular": ["копейка", "копейки", "копейке", "копейку", "копейкой", "копейке"],
                          "plural": ["копейки", "копеек", "копейкам", "копейки", "копейками", "копейках"]}},
        "USD": {"symbols": ["$"], "major": _hard("доллар"), "minor": _hard("цент")},
        "EUR": {"symbols": ["€"], "major": {"gender": "masculine", "tail": "", "singular": ["евро"] * 6,
                                            "plural": ["евро"] * 6},
                "minor": _hard("цент")},
    },
    "scales": {"млн": "миллион", "млрд": "миллиард"},
    "scale_nouns": {"миллион": _hard("миллион"), "миллиард": _hard("миллиард")},
    "units": {
        "кг": _hard("килограмм"), "г": _hard("грамм"), "км": _hard("километр"), "м": _hard("метр"),
        "см": _hard("сантиметр"), "мм": _hard("миллиметр"), "л": _hard("литр"), "мл": _hard("миллилитр"),
        "км/ч": _hard("километр", " в час"), "м/с": _hard("метр", " в секунду"),
        "°C": _hard("градус", " Цельсия"), "°С": _hard("градус", " Цельсия"),
        "Вт": _hard("ватт", genitive_plural="ватт"), "кВт": _hard("киловатт", genitive_plural="киловатт"),
        "Гц": _hard("герц", genitive_plural="герц"), "МГц": _hard("мегагерц", genitive_plural="мегагерц"),
    },
    "titles": {"проф.": "профессор", "г-н": "господин", "д-р": "доктор", "им.": "имени"},
    "abbreviations": {"б-ка": "библиотека", "р-н": "район", "з-д": "завод"},
    "symbols": {"%": "percent", "₽": "money", "$": "money", "€": "money", "°": "measure", "×": "measure"},
})
"""A time word marks a clock time; `около` is none, because it comes before a quantity (Грамматика-80 § 1807:
"около пяти километров"). `более` and `менее` are no prepositions, but a number after them takes the genitive: "более
трех недель" (Розенталь § 190, п. 1 а)), "не менее десяти" (Грамматика-80 § 3123); after `около` and `свыше` too
(Грамматика-80 § 1807, § 1658). Unit symbols, `млн` and `млрд` take no full stop (Правила-2006 § 209). The unit
names are those of the International System of Units in Russian (ru.wikipedia.org, Международная система единиц).
`°С` holds a Cyrillic С, which Russian text also writes. A graphic abbreviation reads as the word it shortens
(Правила-2006, Графические сокращения, before § 209). After 2, 3 and 4 a noun of `pluralia_tantum`, written in the
genitive plural, takes the collective numeral in the nominative and the accusative: "двое саней, трое ножниц, четверо
суток", "двое брюк", and in the other cases the cardinal: "около четырех суток" (Розенталь § 165, п. 1, п. 3;
Грамматика-80 § 1369, п. 4; the genitive forms "суток", "ножниц", "ворот" in § 1201). The other collective numerals are
rare, so "пять суток" takes the cardinal (Розенталь § 165, п. 1). The nouns of `collective_persons` take the collective
numeral in the nominative: "двое детей, трое ребят, трое молодых людей" (Розенталь § 165, п. 1, 3; Грамматика-80 § 1369,
п. 2: "четверо детей, трое людей"). Their accusative is "двоих детей" (Розенталь § 165, п. 3: "мать троих детей"), which
this file does not read. With no preposition, a reader cannot tell it from the nominative where a verb comes before the
number: "Я видел 2 детей". So with no preposition the collective numeral reads only where the number is the subject: at
the start of its clause, after a form of `copulas` ("Нас было двое", § 1369, п. 3) and after a word of
`owner_prepositions` and the owner or the place: "У меня жена, двое девочек" (§ 1369, п. 1), "У соседа трое сыновей", "у
страны / в стране" (§ 2455), "В комнате - ничего лишнего" (§ 2477). A word in an adjectival ending of § 1216 may stand
before the owner: "у моей сестры". In any other place, and after a preposition that governs the accusative, the number
stays as written. A preposition of another case takes the cardinal in that case, which agrees with the noun: "для двух
детей" (Грамматика-80 § 1366: "двух столов, двум столам"; § 1371: "не было и трех взрослых людей"). An adjective in the
genitive plural, in -ых or -их (Грамматика-80 § 1216: "выходных, рабочих"), may stand between the number and the noun:
"пятеро известных лиц" (§ 1369, п. 2). A sign reads "плюс" or "минус", words that do not decline before a number
(Грамматика-80 § 1834: "плюс-минус единица", "равен минус единице"). `в течение` governs the genitive (Грамматика-80 §
1790, § 2710: "в течение двух недель"; Розенталь § 164, п. 3: "в течение двадцати двух суток")."""

VARIETIES = (Variety("ru-RU"),)

_ONE_WORDS = ("один", "одна", "одно", "одну", "одного", "одной", "одному", "одним", "одном")
_SCALE_WORD = re.compile("(?:тысяч|миллион|миллиард|триллион|квадриллион)")
_INNER_THOUSAND = re.compile("((?:миллион|миллиард)[а-я]*) тысяча")
_INNER_MILLION = re.compile("(миллиард[а-я]*) миллион( |$)")
_YO = (("трех", "трёх"), ("четырех", "четырёх"), ("четырем", "четырём"), ("четверт", "четвёрт"))
_ORDINAL_STEMS = {0: "нулев", 1: "перв", 2: "втор", 3: "трет", 4: "четвёрт", 7: "седьм", 40: "сороков", 100: "сот"}
"""The ordinal stems that the genitive of the cardinal does not give (Грамматика-80 § 679 and its note): "первый",
"второй", "третий", "четвёртый", "седьмой", "сороковой", "сотый". "нулевой" is the CLDR form (common/rbnf/ru.xml)."""
_STRESSED = frozenset({0, 2, 6, 7, 8, 40})
"""The ordinals with a stressed ending, which take -ой in the masculine nominative: "второй", "шестой", "седьмой",
"восьмой", "сороковой" (Грамматика-80 § 679, § 1311 "молод-ой")."""
_HARD_ENDINGS = {M: ("ый", "ого", "ому", "ый", "ым", "ом"), N: ("ое", "ого", "ому", "ое", "ым", "ом"),
                 F: ("ая", "ой", "ой", "ую", "ой", "ой"), "plural": ("ые", "ых", "ым", "ые", "ыми", "ых")}
"""The hard adjective declension (Грамматика-80 § 1311, "нов-ый"), by which ordinals decline (§ 1310)."""
_THIRD_ENDINGS = {M: ("ий", "ьего", "ьему", "ий", "ьим", "ьем"), N: ("ье", "ьего", "ьему", "ье", "ьим", "ьем"),
                  F: ("ья", "ьей", "ьей", "ью", "ьей", "ьей"), "plural": ("ьи", "ьих", "ьим", "ьи", "ьими", "ьих")}
""""третий" declines by the first kind of the pronominal declension (Грамматика-80 § 1317, § 1318: треть-его,
треть-ему, треть-ем)."""
_COMPOUND_SCALES = ((10**6, "миллионн"), (1000, "тысячн"))
_COMPOUND_WORDS = {"ста": "сто", "девяноста": "девяносто", "одного": "одно"}
"""In an ordinal in -тысячный or -миллионный the words before it take the genitive and join (Грамматика-80 § 758,
note: "двухсотпятидесятитысячный"), but "сто" and "девяносто" keep their form and "один" reads "одно" (Грамматика-80
§ 775, п. 3; Розенталь § 42, п. 6: "одногодичный, девяностолетие, стократный")."""
_ADJECTIVE_PLURAL = ("ых", "их", "ые", "ие", "ыми", "ими")
_DISTRIBUTIVE_DATIVE = ("1000", "1000000", "1000000000")
_PREPOSITIONAL_TENS = {"двадцать": "двадцати", "тридцать": "тридцати", "сорок": "сорока", "пятьдесят": "пятидесяти",
                      "шестьдесят": "шестидесяти", "семьдесят": "семидесяти", "восемьдесят": "восьмидесяти",
                      "девяносто": "девяноста"}
"""The prepositional of the tens (Грамматика-80 § 1378: "о восьмидесяти семи"). The RBNF rule set of the
prepositional keeps the tens of a count of millions in the nominative ("двадцать миллионах"), but each word of a
compound cardinal declines (§ 1378), so "о двадцати миллионах"."""
_RBNF_CASE = {"nominative": "", "genitive": "-genitive", "dative": "-dative", "accusative": "-accusative",
              "instrumental": "-ablative", "prepositional": "-locative"}


def standard(words: str) -> str:
    """A reading in the standard form. The number 1 is not said before "тысяча" or "миллион" at the start, as
    Грамматика-80 § 1378 declines "тысяча двести восемьдесят семь" and Розенталь § 164, п. 2 writes "в тысяча
    девятьсот шестьдесят пятом году". Inside a number "одна тысяча" keeps "одна": a number has one word for each
    significant digit, and the words "тысяча" and "миллион" besides (Розенталь § 45, п. 2). So "один миллион" keeps
    "один" after "миллиард". The number words take ё
    (Грамматика-80 § 1374, Правила-2006 § 5)."""
    first, _, rest = words.partition(" ")
    if first in _ONE_WORDS and _SCALE_WORD.match(rest):
        words = rest
    words = _INNER_THOUSAND.sub(r"\1 одна тысяча", words)
    words = _INNER_MILLION.sub(r"\1 один миллион\2", words)
    for written, spelled in _YO:
        words = words.replace(written, spelled)
    return " ".join(f"трём{word[4:]}" if word.startswith("трем") and not word.startswith("тремя") else word
                    for word in words.split())


def _rule_sets() -> dict[Features, str]:
    """The RBNF cardinal rule set of each gender and case. The masculine and the neuter decline the same in the
    oblique cases (Грамматика-80 § 1374, § 1378), and the masculine of the prepositional takes the neuter rule set,
    because the masculine one keeps the tens in the nominative: "двадцать одном" for "двадцати одном"."""
    names = {Features(): "spellout-cardinal-masculine"}
    for case, suffix in _RBNF_CASE.items():
        masculine = "neuter" if case == "prepositional" else "masculine"
        names[Features(case=case)] = f"spellout-cardinal-{masculine}{suffix}"
        for gender in (M, F, N):
            name = masculine if gender is M else gender.value
            names[Features(gender=gender, case=case)] = f"spellout-cardinal-{name}{suffix}"
    return names


class RussianSpeller:
    """Cardinals: ovos-number-parser for the nominative, and CLDR RBNF for the other cases. Ordinals: the rules of
    Грамматика-80, over the cardinal words of this speller."""

    def __init__(self):
        self.nominative = OvosNumberSpeller({M: "masculine", F: "feminine", N: "neutral"})
        self.cases = RbnfSpeller(cardinal=_rule_sets(), ordinal={Features(): "spellout-ordinal-masculine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        if features.case in (None, "nominative"):
            words = self.nominative.cardinal(digits, Features(gender=features.gender), request)
        else:
            words = self.cases.cardinal(digits, features, request)
        if features.case == "prepositional":
            words = " ".join(_PREPOSITIONAL_TENS.get(word, word) for word in words.split())
        return standard(words)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """Only the last word of an ordinal declines, and the words before it are the cardinal in the nominative:
        "тысяча двести сороковой" (Грамматика-80 § 758), "в тысяча девятьсот шестьдесят пятом году" (Розенталь
        § 164, п. 2). The last word is an adjective whose stem is that of the oblique cases of its cardinal:
        "восьми - восьмой, пятидесяти - пятидесятый, двухсот - двухсотый" (Грамматика-80 § 679). A round number of
        thousands or millions ends in one word in -тысячный or -миллионный (§ 758, note). An ordinal of a billion
        and above declines."""
        value = bounded_integer(digits)
        if value is None or value >= 10**9:
            raise DeclinedReading(f"no ordinal reading of {len(digits)} digits")
        stem, tail = self._ordinal_stem(value, request)
        endings = _THIRD_ENDINGS if stem == _ORDINAL_STEMS[3] else _HARD_ENDINGS
        case = CASES.index(features.case or "nominative")
        if features.number == "plural":
            ending = endings["plural"][case]
        else:
            gender = features.gender or M
            stressed = gender is M and case in (0, 3) and tail in _STRESSED
            ending = "ой" if stressed else endings[gender][case]
        head = value - tail
        words = f"{self.cardinal(str(head), Features(gender=M), request)} " if head else ""
        return words + stem + ending

    def _ordinal_stem(self, value: int, request: Request) -> tuple[str, int]:
        """The stem of the last word and the part of the value that it reads."""
        for scale, word in _COMPOUND_SCALES:
            if value and value % scale == 0 and (count := value // scale % 1000):
                if count == 1:
                    return word, scale
                genitive = self.cardinal(str(count), Features(gender=M, case="genitive"), request)
                return "".join(_COMPOUND_WORDS.get(part, part) for part in genitive.split()) + word, count * scale
        tail = value % 1000 if value % 100 == 0 else value % 100 if value % 100 < 20 or value % 10 == 0 \
            else value % 10
        if tail in _ORDINAL_STEMS:
            return _ORDINAL_STEMS[tail], tail
        return self.cardinal(str(tail), Features(gender=M, case="genitive"), request).rstrip("иа"), tail

    def year(self, digits: str, features: Features, request: Request) -> str:
        """A year is a masculine ordinal: "в тысяча девятьсот шестьдесят пятом году" (Розенталь § 164, п. 2)."""
        return self.ordinal(digits, replace(features, gender=M), request)

    def _part(self, digits: str, stem: str, case: str, request: Request) -> str:
        """A count of parts: the number in the feminine and an ordinal stem, singular after the category one and
        else plural, which takes the genitive in the nominative and the accusative: "одна целая", "две пятых"."""
        endings = request.data["fraction_endings"]
        one = plural_category(request, digits.lstrip("0") or "0") == "one"
        words = self.cardinal(digits, Features(gender=F, case=case), request)
        return f"{words} {stem}{endings['one' if one else 'other'][CASES.index(case)]}"

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """"одна целая шесть десятых" (Грамматика-80 § 1367), "ноль целых" (Розенталь § 45, п. 7)."""
        stems = request.data["decimal_denominators"]
        if len(fraction) > len(stems):
            raise DeclinedReading(f"no denominator for {len(fraction)} decimal digits")
        case = features.case or "nominative"
        whole = self._part(integer or "0", request.data["whole"], case, request)
        return f"{whole} {self._part(fraction, stems[len(fraction) - 1], case, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """"две пятых" (Розенталь § 45, п. 3): the numerator in the feminine, and the denominator an ordinal."""
        case = features.case or "nominative"
        top = self.cardinal(numerator, Features(gender=F, case=case), request)
        if plural_category(request, numerator.lstrip("0") or "0") == "one":
            return f"{top} {self.ordinal(denominator, Features(gender=F, case=case), request)}"
        plural_case = "genitive" if case in ("nominative", "accusative") else case
        return f"{top} {self.ordinal(denominator, Features(case=plural_case, number='plural'), request)}"


SPELLER = RussianSpeller()


def counted(noun: FrozenMap, written: str, case: str, request: Request) -> str:
    """The form of a noun after a number (Грамматика-80 § 1371). In the nominative and the accusative it is the
    singular after the category one, the genitive singular after few and the genitive plural after many; in the
    other cases the noun agrees, singular after one and plural after the rest. After a decimal the noun takes the
    genitive singular: "35,5 процента" (Розенталь § 164, п. 8; Грамматика-80 § 1367). After the dative of
    "тысяча", "миллион" and "миллиард", which are nouns (Грамматика-80 § 1366; § 1373, примечание), the noun
    takes the genitive plural:
    "по тысяче книг, по миллиону жителей" (Розенталь § 164, п. 7 а))."""
    category = plural_category(request, written)
    index = CASES.index(case)
    if category == "other":
        form = noun["singular"][1]
    elif case == "dative" and written in _DISTRIBUTIVE_DATIVE:
        form = noun["plural"][1]
    elif case in ("nominative", "accusative"):
        form = {"one": noun["singular"][index], "few": noun["singular"][1]}.get(category, noun["plural"][1])
    else:
        form = noun["singular" if category == "one" else "plural"][index]
    return form + noun["tail"]


def governed_case(context: SpanContext, word_after: str = "", category: str = "many", digits: str = "") -> str:
    """The case of a hint, else the case that the preposition before a number governs. A preposition of one case
    gives it (Грамматика-80 § 1657, § 1658), also a preposition of two words such as `в течение`. A preposition
    of two or three cases takes the one that the ending of
    the noun after the number shows: a plural ending, or after the category one a singular ending of the
    prepositional or the instrumental. With no such ending, the first case of `case_choices` applies. Distributive
    `по` takes the dative of "один", "тысяча", "миллион" and "миллиард": "по одному рублю, по тысяче книг, по
    миллиону жителей" (Розенталь § 164, п. 7 а)), and the accusative of the other numbers (п. 7 б))."""
    if context.hint is not None and context.hint.case is not None:
        return context.hint.case
    data = context.request.data
    preposition = context.before[-1].lower() if context.before else ""
    compound = " ".join(context.before[-2:]).lower()
    if compound in data["governed_cases"]:
        return data["governed_cases"][compound]
    if preposition in data["governed_cases"]:
        return data["governed_cases"][preposition]
    choices = data["case_choices"].get(preposition)
    if choices is None:
        return "nominative"
    word = word_after.lower()
    shown = next((case for ending, case in data["plural_endings"].items() if word.endswith(ending)), None)
    if preposition == "по" and (category == "one" or digits.lstrip("0") in _DISTRIBUTIVE_DATIVE):
        shown = "dative"
    elif category == "one" and word.endswith(("е", "и")):
        shown = "prepositional"
    elif category == "one" and word.endswith(("ом", "ем", "ём", "ой", "ей", "ью")):
        shown = "instrumental"
    return shown if shown in choices else choices[0]


_MALE_PERSONS = ("мужчин", "юнош", "дяд", "слуг", "вельмож", "воевод", "старост", "старшин", "старейшин", "судь",
                 "дедушк", "братишк", "мальчишк", "парнишк", "мальчонк", "пап")
"""Stems of the nouns in -а, -я that name a male person. A name of a male person is masculine (Грамматика-80
§ 1136), so "папа" is too. The list "вельможа, воевода, дядя, мужчина, слуга, староста, старшина, юноша" and
"братишка, мальчишка, парнишка, дедушка, мальчонка" is in § 1184, "старейшина" in § 1138 and "судья" in § 1173."""
_SECOND_DECLENSION = ("а", "я", "ы", "и", "е", "у", "ю", "ой", "ей", "ою", "ею", "ёй")
_NEUTER_IN_MYA = ("бре", "вре", "вы", "зна", "пле", "и", "пла", "полы", "се", "стре", "те")
"""The neuter nouns in -мя (Грамматика-80 § 1187: "бремя, время, вымя, знамя, племя, имя, пламя, полымя, семя,
стремя, темя"), whose oblique forms take -мени."""


def _lexical_gender(word: str) -> GrammaticalGender | None:
    """The gender that the meaning or a closed list gives, in any case: a noun in -а, -я that names a male person,
    "мать" by meaning (Грамматика-80 § 1140), "путь" (§ 1187, § 1189) and the nouns in -мя (§ 1187)."""
    if any(word.startswith(stem) and word[len(stem):] in _SECOND_DECLENSION for stem in _MALE_PERSONS):
        return M
    if word in ("путь", "пути", "путём"):
        return M
    if word in ("мать", "матери", "матерью"):
        return F
    for root in _NEUTER_IN_MYA:
        if word in (root + "мя", root + "мени", root + "менем"):
            return N
    return None


def noun_gender(word: str, case: str, category: str) -> GrammaticalGender | None:
    """The gender that the ending of the word after a number shows (Грамматика-80 § 1134, §§ 1173-1188).
    In the nominative an adjective ends in -ая (feminine), -ое (neuter) or -ый, -ий, -ой (masculine); a noun with no
    ending is masculine, a noun in -а, -я feminine and a noun in -о, -е, -ё neuter. A noun in -ь after ж, ш, ч, щ is
    feminine, because a masculine noun of a stem in a hissing consonant has no ь (§ 1173: "нож, мяч, товарищ"; § 1187:
    "рожь, ночь, мощь"); so is a noun of the suffix -ость, -есть (§ 315: "смелость, свежесть"), which declines
    as "область, радость" (§ 1187). "гость" and "тесть" have no such suffix, so a word needs two letters before
    -ость or -есть; another noun in -ь has either gender. After the category few the noun takes the genitive
    singular (§ 1371), where -ы, -и mark the feminine and -а, -я the masculine and the neuter, which both read "два".
    In the dative singular -у, -ю mark the masculine and the neuter ("нож-у", "плеч-у", § 1185), and -е, -и the
    feminine ("карт-е", § 1185; "радост-и", § 1188); in the prepositional -у, -ю mark the masculine (§ 1182), and
    -и after no и the feminine of the third declension. A prepositional in -е or -ии has any gender: "о нож-е",
    "о карт-е" (§ 1185), "о лини-и" (§ 1186)."""
    word = word.lower()
    if not word or not all(is_letter(char) for char in word):
        return None
    if (gender := _lexical_gender(word)) is not None:
        return gender
    if category == "one" and case in ("nominative", "accusative"):
        if word.endswith(("ая", "яя")) or (case == "accusative" and word.endswith(("ую", "юю", "у", "ю"))):
            return F
        if word.endswith(("ое", "ее", "о", "е", "ё")):
            return N
        if word.endswith(("ый", "ий", "ой")) or word[-1] not in "аяеёоиыуюэь":
            return M
        suffixed = len(word) > 5 and word.endswith(("ость", "есть"))
        return F if suffixed or word.endswith(("а", "я", "жь", "шь", "чь", "щь")) else None
    if (category, case) in (("one", "genitive"), ("few", "nominative"), ("few", "accusative")):
        return F if word.endswith(("ы", "и")) else M if word.endswith(("а", "я")) else None
    if category == "one" and case == "instrumental":
        return F if word.endswith(("ой", "ей", "ью")) else M if word.endswith(("ом", "ем", "ём")) else None
    if category == "one" and case == "dative":
        return M if word.endswith(("у", "ю")) else F if word.endswith(("е", "и")) else None
    if category == "one" and case == "prepositional":
        return M if word.endswith(("у", "ю")) else F if word.endswith("и") and not word.endswith("ии") else None
    return None


def agreement(digits: str, context: SpanContext) -> Features:
    """The gender and the case of a cardinal, from the preposition before it and the noun after it; an adjective
    in the plural between them is skipped. A hint wins. With no evidence the default gender applies, the masculine
    of counting (Грамматика-80 § 1368)."""
    if context.hint is not None:
        return context.hint
    request = context.request
    category = plural_category(request, digits.lstrip("0") or "0")
    after = [word for word in context.after if not word.lower().endswith(_ADJECTIVE_PLURAL)]
    word = after[0] if after else ""
    case = governed_case(context, word, category, digits)
    default = request.params.default_gender.get(request.language.code) or request.language.default_gender
    return Features(gender=noun_gender(word, case, category) or default, case=case)


def _signed(words: str, sign: str, request: Request) -> str:
    """The words of the number after the word of its sign. A sign with no word in `sign_words` declines the
    reading, so the span stays as written."""
    if not sign:
        return words
    if sign not in request.data["sign_words"]:
        raise DeclinedReading(f"no word for the sign {sign}")
    return f"{request.data['sign_words'][sign]} {words}"


def _written(amount: FrozenMap) -> str:
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


def _amount(amount: FrozenMap, gender: GrammaticalGender, case: str, request: Request) -> str:
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(case=case), request)
    else:
        words = SPELLER.cardinal(amount["integer"], Features(gender=gender, case=case), request)
    return _signed(words, amount["sign"], request)


def _counted_amount(span: Span, amount: FrozenMap, noun: FrozenMap, context: SpanContext) -> str:
    """An amount and its noun. The first number of a range, which takes the range word as its trail, reads alone:
    "десять — двадцать процентов"."""
    request = context.request
    case = governed_case(context, digits=_written(amount))
    words = _amount(amount, GrammaticalGender(noun["gender"]), case, request)
    if span.trail.strip() == request.data["range_word"]:
        return words
    return f"{words} {counted(noun, _written(amount), case, request)}"


def _adjectival(word: str) -> bool:
    return len(word) > 2 and word.endswith(("ых", "их"))


_MODIFIER_ENDINGS = ("ого", "его", "ой", "ей", "ом", "ем", "ых", "их")
"""The endings of the oblique cases of an adjective in Грамматика-80 § 1216: "выходн-ого, рабоч-его, о выходн-ом,
запят-ой, заведующ-ей, выходн-ых, рабоч-их"."""


def _subject_place(context: SpanContext) -> bool:
    """Whether a number with no preposition before it stands where the subject of its clause stands: first in the
    clause, after a form of `copulas`, or after a phrase of a word of `owner_prepositions` and the owner or the
    place, which one modifier may come before: "у сестры", "у моей сестры", "в семье". The phrase must open the
    clause, because after a verb the number is its object: "Я видел в парке 2 детей". The window holds three words,
    so a full window opens the clause only where its first word starts with a capital letter."""
    data, written = context.request.data, context.before
    words = [word.lower() for word in written]
    if not words or words[-1] in data["copulas"]:
        return True
    opens = len(words) < 3 or written[0][:1].isupper()
    phrase = len(words) == 2 or (len(words) == 3 and len(words[1]) > 2 and words[1].endswith(_MODIFIER_ENDINGS))
    return opens and words[0] in data["owner_prepositions"] and phrase


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal in the gender and the case of its context. Digits with a leading zero after a lead read one by
    one."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = " ".join(request.data["digit_words"][int(digit)] for digit in digits)
    else:
        features = agreement(digits, context)
        data = request.data
        noun = next((word.lower() for word in context.after if not _adjectival(word.lower())), "")
        collective = data["collective_numerals"].get(digits)
        nominative = features.case in (None, "nominative")
        persons = collective and noun in data["collective_persons"]
        if persons and (features.case == "accusative" or (nominative and not _subject_place(context))):
            raise DeclinedReading(f"no accusative reading of {digits} before {noun}")
        if (persons and nominative) or (collective and noun in data["pluralia_tantum"]
                                        and (nominative or features.case == "accusative")):
            words = collective
        else:
            words = SPELLER.cardinal(digits, features, request)
    words = _signed(words, fields["sign"], request)
    return f"{request.data['leads'][fields['lead']]} {words}" if fields["lead"] else words


def speak_decimal(span: Span, context: SpanContext) -> str:
    fields, request = span.fields, context.request
    words = SPELLER.decimal(fields["integer"], fields["fraction"], Features(case=governed_case(context)), request)
    return _signed(words, fields["sign"], request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields, request = span.fields, context.request
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(case=governed_case(context)),
                             request)
    return _signed(words, fields["sign"], request)


def speak_percent(span: Span, context: SpanContext) -> str:
    return _counted_amount(span, span.fields["amount"], context.request.data["percent"]["noun"], context)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The amounts that the dimension word or the range word join, and the unit, which agrees with the last."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    noun = request.data["units"][span.fields["unit"]]
    case = governed_case(context)
    words = [_amount(amount, GrammaticalGender(noun["gender"]), case, request) for amount in amounts]
    link = request.data["dimension_word" if span.fields["relation"] == "dimension" else "range_word"]
    return f"{f' {link} '.join(words)} {counted(noun, _written(amounts[-1]), case, request)}"


def _number_and_noun(digits: str, noun: FrozenMap, case: str, request: Request) -> str:
    words = SPELLER.cardinal(digits, Features(gender=GrammaticalGender(noun["gender"]), case=case), request)
    return f"{words} {counted(noun, digits, case, request)}"


def speak_money(span: Span, context: SpanContext) -> str:
    """Two decimal digits read as the minor unit: "пять долларов пятьдесят центов". After a scale word the currency
    takes the genitive plural: "пять миллионов долларов"."""
    request, fields = context.request, span.fields
    currency = request.data["currencies"][fields["currency"]]
    major, minor = currency["major"], currency["minor"]
    amount = FrozenMap({**fields["amount"], "sign": ""})
    case = governed_case(context)
    if fields["scale"]:
        scale = request.data["scale_nouns"][request.data["scales"][fields["scale"]]]
        words = (f"{_amount(amount, GrammaticalGender(scale['gender']), case, request)} "
                 f"{counted(scale, _written(amount), case, request)} {major['plural'][1]}")
    elif len(amount["fraction"]) == 2:
        integer, cents = amount["integer"] or "0", str(int(amount["fraction"]))
        parts = [(integer, major)] if cents == "0" else [(cents, minor)] if bounded_integer(integer) == 0 \
            else [(integer, major), (cents, minor)]
        words = " ".join(_number_and_noun(digits, noun, case, request) for digits, noun in parts)
    else:
        words = _counted_amount(span, amount, major, context)
    return _signed(words, fields["amount"]["sign"], request)


def speak_time(span: Span, context: SpanContext) -> str:
    """The hour and the minutes as numbers in the case of the preposition: "в двенадцать ноль-ноль" (Розенталь
    § 45, п. 7). Minutes 1 to 9 read "ноль" and the number."""
    request, fields = context.request, span.fields
    case = governed_case(context)
    words = [SPELLER.cardinal(str(fields["hour"]), Features(case=case), request)]
    minute = SPELLER.cardinal(str(fields["minute"]), Features(case=case), request)
    if fields["minute"] == 0 and fields["second"] is None:
        words.append(request.data["zero_minutes"])
    else:
        words.append(f"{request.data['digit_words'][0]} {minute}" if fields["minute"] < 10 else minute)
    if fields["second"] is not None:
        words.append(SPELLER.cardinal(str(fields["second"]), Features(case=case), request))
    return " ".join(words)


def date_case(span: Span, context: SpanContext) -> str:
    """The case of the day of a date. After a preposition it is the case that the preposition governs. A date that
    closes its clause reads in the nominative in two places. The first is after a label colon, which the span holds
    as its lead, where the date names the day (Грамматика-80 § 1167: "называющая форма в заголовках, подписях").
    The second is where the date is the subject of a form of `copulas` or of `onset_verbs`: "Было шесть часов вечера,
    конец мая" (§ 2536), "Сегодня воскресенье" (§ 2539), "Наступила осень" (§ 2681). There the clause holds no word
    before the date but those verbs and the words of `date_adverbs`: "Вот и наступило первое сентября", "Сегодня уже
    первое мая", and a date alone in its clause, which is a nominative sentence (§ 2522, § 2524: "Двадцать первое.
    Ночь. Понедельник."). A date closes its clause when only "года", closing quotes and a mark
    of `_FINAL_MARKS` or the end of the clause follow it. A comma does not close it, because the clause often goes
    on after the comma: "Первого мая, в субботу, мы поехали на дачу". Only the words after the last colon or opening
    quote before the date count: "Он сказал: «Сегодня первое мая»". Every other date says when
    something happens and reads in the genitive: "встреча пятого мая" (§ 1168), "Лето наступило первого июня",
    "Было первого мая подписано соглашение". A pronoun "это" before the copula is the subject (Розенталь § 189,
    п. 3: "это была хрестоматия"), so "Это было первого мая" says when something happened. The particle "ли" asks a
    question and leaves the subject in the nominative: "Падают ли овцы?" (§ 1693, § 1949). The words of `date_particles`
    alone give no nominative: "да" opens a reply and "а" a follow-up question, and such a reply as "Да, первого мая"
    takes its form from the question (§ 1954), which the window does not see. Other particles and conjunctions keep
    the nominative sentence: "но весна, весна" (§ 2524), so "Почему магазин закрыт? Ведь первое мая!"."""
    if context.hint is not None and context.hint.case is not None:
        return context.hint.case
    data = context.request.data
    after = context.after[1:] if context.after and context.after[0].lower() in data["year_noun"] else context.after
    words = [word.lower() for word in context.before]
    scope = context.request.memo.get(_SCOPE, {}).get(span.start, len(words))
    words = words[len(words) - min(scope, len(words)):]
    closed = not after or span.trail[-1:] in _FINAL_MARKS
    if span.lead == ":" and closed:
        return "nominative"
    before = words[-1] if words else ""
    if before in data["governed_cases"] or " ".join(words[-2:]) in data["governed_cases"] \
            or before in data["case_choices"]:
        return governed_case(context)
    subject = set(data["copulas"]) | set(data["onset_verbs"]) | set(data["date_adverbs"])
    named = not words or any(word not in data["date_particles"] for word in words)
    return "nominative" if closed and named and all(word in subject for word in words) else "genitive"


def speak_date(span: Span, context: SpanContext) -> str:
    """"двенадцатое марта две тысячи двадцать четвёртого года": the day a neuter ordinal in the case of
    `date_case`, the month in the genitive ("Первое мая", Розенталь § 20) and the year a genitive ordinal of which
    only the last word declines (Розенталь § 164, п. 2). A form of "год" that the text writes after the date
    stands in place of "года". The first day of a range in one month has no month of its own: "с первого по
    десятое мая". After a label colon the reading starts with the space that the span holds."""
    request, fields = context.request, span.fields
    words = []
    if fields["day"] is not None:
        words.append(SPELLER.ordinal(str(fields["day"]), Features(gender=N, case=date_case(span, context)), request))
    if fields["month"] is not None:
        words.append(request.data["months"][fields["month"] - 1])
    if fields["year"] is not None:
        words.append(SPELLER.year(str(fields["year"]), Features(case="genitive"), request))
        if fields["suffix"] or not (context.after and context.after[0].lower() in request.data["year_noun"]):
            words.append(request.data["year_noun"][1])
    return (" " if span.lead else "") + " ".join(words)


def speak_year(span: Span, context: SpanContext) -> str:
    """The case of a year comes from the form of "год" after it: "в 2024 году" is the prepositional, "к 2024
    году" the dative, "2024 года" the genitive. After `г.` the preposition gives the case, and the span reads the
    form of "год" in that case. The first year of a range, which has no form of "год", takes the case of its
    preposition: "с две тысячи первого по две тысячи пятый год" (Розенталь § 164, п. 2)."""
    request = context.request
    nouns = request.data["year_noun"]
    if span.fields["suffix"]:
        case = "prepositional" if context.before and context.before[-1].lower() in ("в", "во") \
            else governed_case(context)
        words = SPELLER.year(span.fields["digits"], Features(case=case), request)
        return f"{words} {nouns[CASES.index(case)]}"
    noun = context.after[0].lower() if context.after else ""
    case = CASES[nouns.index(noun)] if noun in nouns else governed_case(context)
    if noun == nouns[5] and governed_case(context) != "dative":
        case = "prepositional"
    return SPELLER.year(span.fields["digits"], Features(case=case), request)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """`5-го`, `20-й`, `135-м` (Правила-2006 § 111, п. 4): the letters after the hyphen end the ordinal and give
    its gender, number and case. `-й` is the masculine nominative, or the feminine in another case after a
    preposition. `-е` is the neuter, or the plural before a noun in -ы, -и and for a decade with no noun, as in
    `90-е`. `-м` is the masculine prepositional, or the instrumental after a preposition of the instrumental."""
    request = context.request
    digits, ending = span.fields["digits"], span.fields["marker"][1:]
    following = context.after[0].lower() if context.after else ""
    case = governed_case(context, following, "one")
    if ending == "й":
        features = Features(gender=M) if case in ("nominative", "accusative") else Features(gender=F, case=case)
    elif ending == "я":
        features = Features(gender=F)
    elif ending == "е":
        plural = following.endswith(("ы", "и")) or (not following and digits.endswith("0") and len(digits) > 1)
        features = Features(number="plural") if plural else Features(gender=N)
    elif ending == "х":
        features = Features(number="plural", case="genitive")
    elif ending == "ми":
        features = Features(number="plural", case="instrumental")
    elif ending == "м":
        features = Features(gender=M, case="instrumental" if case == "instrumental" else "prepositional")
    elif ending == "ю":
        features = Features(gender=F, case="accusative")
    else:
        features = Features(gender=M, case="genitive" if ending == "го" else "dative")
    return SPELLER.ordinal(digits, features, request)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """A graphic abbreviation reads as the word it shortens (Правила-2006, Графические сокращения, § 209, § 210,
    § 111, п. 1). `млн` and `млрд` after a number agree with it as nouns (Грамматика-80 § 1371), and after a
    decimal they take the genitive singular: "35,5 процента" (Розенталь § 164, п. 8)."""
    data, key = context.request.data, span.fields["key"]
    if key in data["scales"]:
        number = re.search("[0-9]+(?:[.,][0-9]+)?$", fold_digits(context.before[-1])).group().replace(",", ".")
        case = governed_case(replace(context, before=context.before[:-1]))
        return counted(data["scale_nouns"][data["scales"][key]], number, case, context.request)
    return data["titles"].get(key) or data["abbreviations"][key]


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """The core attachment, but a suffix `г.` after a year is the abbreviation of "год", which the verbalizer of
    the year or the date reads."""
    return prefix + spoken + ("" if suffix.lstrip() == "г." else suffix)


_FINAL_MARKS = (".", "!", "?", "…")
_CLOSING_QUOTES = ("»", "”", '"', ")")
"""A date closes its clause before a mark of `_FINAL_MARKS`, and closing quotes may stand between them."""
_OPENING_QUOTES = ("«", "“", '"')
_SCOPE = "ru_date_scope"
"""The key of `Request.memo` that maps the start of a date span to the number of words between the last colon or
opening quote and the date, where one stands among the three words before the date."""


def _scope(text: str, words: Sequence[Word], start: int) -> int | None:
    """The number of context words between the last colon or opening quote and text[start], if one stands among the
    three context words before it. The words are those of the call's tokens, as `SpanContext.before` holds them. A
    colon before a digit of the text before the date is part of a clock time. A quote opens only after a space or at
    the start of the text, and only when no closing quote stands between it and the date, so a quoted title such as
    "газету «Завтра»" leaves the window whole."""
    index = bisect_right(words, start, key=lambda word: word.end)
    window = words[max(0, index - 3):index]
    if not window:
        return None
    for position in range(start - 1, window[0].start - 1, -1):
        char = text[position]
        colon = char == ":" and not text[position + 1:min(position + 2, start)].isdigit()
        quote = (char in _OPENING_QUOTES and (position == 0 or text[position - 1].isspace())
                 and not any(closing in text[position + 1:start] for closing in ("»", "”", char)))
        if colon or quote:
            return sum(word.start > position for word in window)
    return None


def _framed(text: str, span: Span, words: Sequence[Word], request: Request) -> Span:
    """The date span with the punctuation around it that `date_case` reads. A colon of a label before it, as in
    `Дата: 9 мая`, is the lead, and the one space after the colon is in the span. The closing quotes and the mark
    of `_FINAL_MARKS` after the date, or after "года" after its year, are the trail, and the span holds that "года"
    too. A mark that a letter or a digit follows is no trail, so that a second pass reads the text the same way. The
    lead and the trail hold only punctuation (design section 5.1). The scope of `_scope` goes into `Request.memo`;
    `words` are the context words of the call's tokens."""
    if text[max(0, span.start - 2):span.start] == ": ":
        span = replace(span, start=span.start - 2, lead=":")
    scope = _scope(text, words, span.start)
    if scope is not None:
        request.memo.setdefault(_SCOPE, {})[span.start] = scope
    if span.trail:
        return span
    end, noun = span.end, request.data["year_noun"][1]
    if span.fields["year"] is not None and not span.fields["suffix"] and text[end:end + 1] in (" ", "\u00a0") \
            and text.startswith(noun, end + 1):
        end += 1 + len(noun)
    stop = end
    while text[stop:stop + 1] in _CLOSING_QUOTES:
        stop += 1
    following = text[stop + 1:stop + 2]
    if text[stop:stop + 1] not in _FINAL_MARKS or (following and is_word_char(following)):
        return span
    return replace(span, end=stop + 1, trail=text[end:stop + 1])


def _sentence_end(text: str, end: int) -> bool:
    following = next_visible(text, end)
    return following == "" or following.isupper()


@dataclass(frozen=True)
class Clock:
    """`в 14:30`, `до 9:05`, `с 8:00:15`: an hour 0-23 and two minute digits, and seconds the same way, after a
    word of `time_words`. Russian writes no day period with a time, so the time word is the one evidence."""
    name: str = "clock"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        time_words = request.data["time_words"]
        for match in re.finditer("([0-9][0-9]?):([0-9][0-9])(?::([0-9][0-9]))?", fold_digits(text)):
            start, end = match.span()
            before = text[:start].rstrip().rsplit(maxsplit=1)
            if not (is_bounded(text, start, end) and one_digit_set(text[start:end]) and before
                    and before[-1].lower() in time_words and text[start - 1].isspace()) \
                    or text.startswith(":", end):
                continue
            fields = clock_fields(*match.groups())
            if fields is not None:
                hour, minute, second = fields
                yield Span(start, end, Form.TIME, FrozenMap({"hour": hour, "minute": minute, "second": second,
                                                             "period": None, "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Year:
    """Four digits from 1000 to 2999 before a form of "год", as in `в 2024 году` and `2024 года`, or before `г.`,
    which the span holds: `в 1965 г.`. The first year of a range that `по` or `до` joins to such a year is a year
    too: `с 2001 по 2005 год`."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        nouns = "|".join(sorted(set(request.data["year_noun"]), key=len, reverse=True))
        year = f"[  ](?:{nouns})(?![^ .,;:!?)])|[  ]г[.]"
        pattern = f"([0-9]{{4}})(?:[  ](?:{nouns})(?![^ .,;:!?)])|([  ]г[.])|(?=[  ](?:по|до)[  ][0-9]{{4}}(?:{year})))"
        for match in re.finditer(pattern, fold_digits(text)):
            start = match.start()
            end = match.end() if match.group(2) else match.end(1)
            if not (is_bounded(text, start, match.end(1)) and one_digit_set(text[start:match.end(1)])
                    and 1000 <= int(match.group(1)) <= 2999) or (start and text[start - 1] in ".,/-"):
                continue
            suffix = match.group(2) or ""
            yield Span(start, end, Form.YEAR, FrozenMap({"digits": match.group(1), "suffix": suffix}),
                       trail="." if suffix and _sentence_end(text, end) else "", recognizer=self.name)


@dataclass(frozen=True)
class DateNamed:
    """`12 марта`, `12 марта 2024`, `9 мая 1945 г.`: a day, a month in the genitive and a year of four digits.
    The span holds `г.` after the year. In a range of days of one month, as in `с 1 по 10 мая`, the first day is a
    date with no month or year of its own, and the month of the second day must hold it."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months, words = request.data["months"], context_words(tokens)
        folded = fold_digits(text)
        ranges = f"([0-9][0-9]?)[  ](?:по|до)[  ]([0-9][0-9]?)[  ]({'|'.join(months)})(?:[  ]([0-9]{{4}}))?"
        for match in re.finditer(ranges, folded):
            start, end = match.span(1)
            first, last = int(match.group(1)), int(match.group(2))
            month = months.index(match.group(3)) + 1
            year = int(match.group(4)) if match.group(4) else None
            if is_bounded(text, start, end) and one_digit_set(text[start:end]) and 0 < first < last \
                    and is_valid(year, month, last) and not (start and text[start - 1] in ".,/-"):
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": None, "month": None, "day": first, "written_order": "DMY",
                                      "month_written": "name", "prefix": "", "suffix": ""}), recognizer=self.name)
        pattern = f"([0-9][0-9]?)[  ]({'|'.join(months)})(?:[  ]([0-9]{{4}})([  ]г[.])?)?"
        for match in re.finditer(pattern, folded):
            start, end = match.span()
            day, month = int(match.group(1)), months.index(match.group(2)) + 1
            year = int(match.group(3)) if match.group(3) else None
            if not (is_bounded(text, start, end if match.group(4) else end) and one_digit_set(text[start:end])
                    and is_valid(year, month, day)) or (start and text[start - 1] in ".,/-"):
                continue
            suffix = match.group(4) or ""
            yield _framed(text, Span(start, end, Form.DATE,
                                     FrozenMap({"year": year, "month": month, "day": day, "written_order": "DMY",
                                                "month_written": "name", "prefix": "", "suffix": suffix}),
                                     trail="." if suffix and _sentence_end(text, end) else "", recognizer=self.name),
                          words, request)


@dataclass(frozen=True)
class LabelledDateNumeric(DateNumeric):
    """The shared numeric date, `Дата: 09.05.1945`, with the punctuation around it that `_framed` adds."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        words = context_words(tokens)
        for span in super().find(text, tokens, request):
            yield _framed(text, span, words, request)


@dataclass(frozen=True)
class HyphenOrdinal:
    """`5-го`, `20-й`, `1990-х`, `10 000-й`: digits, a hyphen and an ending of `ordinal_endings` (Правила-2006
    § 111, п. 4). Other letters after the hyphen, as in `25-процентный` (§ 111, п. 3), make a word that no rule
    here reads, so the whole run stays as written."""
    name: str = "hyphen_ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer("([0-9]{1,3}(?:[ \u00a0][0-9]{3})+|[0-9]+)-", fold_digits(text)):
            start, stop = match.span()
            end = stop
            while end < len(text) and is_letter(text[end]):
                end += 1
            if end == stop or not is_bounded(text, start, end) or not one_digit_set(text[start:stop - 1]) \
                    or (start and text[start - 1] in ".,/-"):
                continue
            yield Span(start, end, Form.ORDINAL,
                       FrozenMap({"digits": re.sub("[ \u00a0]", "", match.group(1)), "marker": text[stop - 1:end],
                                  "prefix": "", "suffix": "",
                                  "script": "Latn"}),
                       recognizer=self.name, keep=text[stop:end] not in request.data["ordinal_endings"])


@dataclass(frozen=True)
class SpacedNumber:
    """`1 000 000`: groups of three digits that a plain space joins, as Russian text writes them (ru.wikipedia.org,
    Десятичный разделитель). The group mark of `number_marks` is the no-break space, because a plain space also
    stands between two numbers, as in `$5 1/2`. A run with a sign, a decimal part, a symbol or a unit next to it
    stays as written, because the shared recognizers of those forms do not read it."""
    name: str = "spaced_number"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        marks = (*data["symbols"], *data["units"])
        for match in re.finditer("[0-9]{1,3}(?: [0-9]{3})+", fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end):
                continue
            after = text[end:].lstrip(" \u00a0")
            before = text[:start].rstrip(" \u00a0")
            keep = (after.startswith(marks) or before.endswith((*data["symbols"], "-", "−", "+"))
                    or re.match("[.,][0-9]", text[end:end + 2]) is not None)
            yield Span(start, end, Form.CARDINAL,
                       FrozenMap({"digits": match.group().replace(" ", ""), "sign": "", "lead": "", "prefix": "",
                                  "suffix": "", "script": "Latn"}), recognizer=self.name, keep=keep)


@dataclass(frozen=True)
class ScaledMoney:
    """`1,5 млн ₽`, `-1,5 млн ₽`, `5 млрд $`: a number with its sign, `млн` or `млрд` and a currency symbol after
    them. The shared money recognizer reads a scale word only after a number that follows its symbol, as in
    `$1,5 млн`, and it reads no sign before a number with the symbol after it, so `+5 $` and `-5 ₽` are read here
    too."""
    name: str = "scaled_money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        symbols = {symbol: code for code, currency in data["currencies"].items() for symbol in currency["symbols"]}
        pattern = re.compile(f"[ \u00a0](?:({'|'.join(data['scales'])})[ \u00a0]?)?"
                             f"({'|'.join(map(re.escape, symbols))})")
        for number in numbers_in(text, request):
            match = pattern.match(text, number.end)
            if match and (match.group(1) or number.sign) and is_bounded(text, number.start, match.end()):
                yield Span(number.start, match.end(), Form.MONEY,
                           FrozenMap({"amount": number.amount(), "currency": symbols[match.group(2)],
                                      "written_symbol": match.group(2), "scale": match.group(1) or "", "prefix": "",
                                      "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised word, an abbreviation of the `abbreviations` table, and `млн` or `млрд` after a
    number. A full stop that ends the sentence stays after the reading. Правила-2006 § 209 writes `млн` and `млрд`
    with no full stop, but a text may add one, as in `1,5 млн. рублей`. The span holds that stop, so that no stop
    stays inside the sentence."""
    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for table in ("titles", "abbreviations", "scales"):
            for key in data[table]:
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    after_number = re.search("[0-9][  ]$", fold_digits(text[max(0, position - 2):position]))
                    wanted = {"titles": next_visible(text, end).isupper(), "abbreviations": True,
                              "scales": after_number is not None}[table]
                    if wanted and is_bounded(text, position, end):
                        stop = table == "scales" and text[end:end + 1] == "."
                        trail = "." if table != "titles" and (key.endswith(".") or stop) \
                            and _sentence_end(text, end + stop) else ""
                        yield Span(position, end + stop, Form.ABBREVIATION, FrozenMap({"key": key}), trail=trail,
                                   recognizer=self.name)
                    position = text.find(key, end)


@dataclass(frozen=True)
class OtherDecimalMark:
    """`3.5` when the decimal mark is the comma, and `3,5` when it is the full stop. The run may be a version number
    or a list, so it stays as written (design section 4.2)."""
    name: str = "other_decimal_mark"
    form: Form = Form.DECIMAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        other = "." if request.params.decimal_mark == "," else ","
        for match in re.finditer("[0-9]+(?:[.,][0-9]+)+", fold_digits(text)):
            start, end = match.span()
            if other in match.group() and is_bounded(text, start, end):
                integer, fraction = re.split("[.,]", match.group(), maxsplit=1)
                yield Span(start, end, Form.DECIMAL,
                           FrozenMap({"integer": integer, "fraction": fraction, "sign": "", "prefix": "",
                                      "suffix": "", "script": "Latn"}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class ExpressionGuard:
    """`5+3`, `2×2=4`: numbers that an operator joins. The file reads no operator, so the run stays as written."""
    name: str = "expression_guard"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer("[0-9]+(?: ?[+=÷] ?[0-9]+)+", fold_digits(text)):
            start, end = match.span()
            if is_bounded(text, start, end):
                yield Span(start, end, Form.CARDINAL,
                           FrozenMap({"digits": re.match("[0-9]+", match.group()).group(), "sign": "", "lead": "",
                                      "prefix": "", "suffix": "", "script": "Latn"}),
                           recognizer=self.name, keep=True)


LANGUAGE = LanguageSpec(
    code="ru",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], DateNamed(), LabelledDateNumeric(), Clock(), Year(), HyphenOrdinal(),
                 SpacedNumber(), ScaledMoney(), SHARED["money"], SHARED["percent"], SHARED["measure"],
                 ExpressionGuard(), SHARED["fraction"], Abbreviation(), OtherDecimalMark(), SHARED["decimal"],
                 SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.YEAR: speak_year,
        Form.ORDINAL: speak_ordinal, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.FRACTION: speak_fraction, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
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
        "scale": frozenset({"short"}),
        "default_gender": frozenset({"masculine", "feminine", "neuter"}),
    },
    not_applicable=frozenset({"register", "phone_regions"}),
)
