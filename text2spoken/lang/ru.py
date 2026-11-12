"""Russian: ru-RU, the one variety, which every other ru-* tag selects through closest_lang.

Nominative cardinals and ordinals come from ovos-number-parser, and the other cases from CLDR RBNF, with one rule
set for each gender and case (design section 5.4). A number agrees in gender and case with the noun it counts, and
a preposition before it gives the case. The rules cite these sources:

- Грамматика-80: Русская грамматика, т. I, АН СССР, 1980, by paragraph (rusgram.narod.ru).
- Розенталь: Д. Э. Розенталь, Справочник по правописанию и литературной правке, 4-е изд., 1985, by paragraph.
- Правила-2006: Правила русской орфографии и пунктуации. Полный академический справочник, 2006, by paragraph
  (orfo.ruslang.ru).

Number words take the letter ё, as Грамматика-80 § 1374 writes "трёх", "четырёх", "трём", so that a reader says
them right (Правила-2006 § 5).
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.recognizers import SHARED, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller, bounded_integer
from text2spoken.core.times import clock_fields
from text2spoken.core.tokens import Token, fold_digits, is_bounded, is_letter, next_visible, one_digit_set
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
    "sign_words": {"-": "минус"},
    "digit_words": ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"],
    "leads": {"№": "номер", "№ ": "номер"},
    "range_word": "—",
    "range_marks": ["-", "–", "—"],
    "dimension_marks": ["×"],
    "dimension_word": "на",
    "time_words": ["в", "во", "к", "ко", "до", "с", "со", "после", "около", "по", "от"],
    "zero_minutes": "ноль-ноль",
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
        "свыше": "genitive", "к": "dative", "ко": "dative", "согласно": "dative", "вопреки": "dative",
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
"""Unit symbols, `млн` and `млрд` take no full stop (Правила-2006 § 209). The unit names are those of the
International System of Units in Russian (ru.wikipedia.org, Международная система единиц). `°С` holds a Cyrillic С,
which Russian text also writes. A graphic abbreviation reads as the word it shortens (Правила-2006, Графические
сокращения, before § 209)."""

VARIETIES = (Variety("ru-RU"),)

_ONE_WORDS = ("один", "одна", "одно", "одну", "одного", "одной", "одному", "одним", "одном")
_SCALE_WORD = re.compile("(?:тысяч|миллион|миллиард|триллион|квадриллион)")
_YO = (("трех", "трёх"), ("четырех", "четырёх"), ("четырем", "четырём"), ("четверт", "четвёрт"))
_ORDINAL_ENDINGS = ("ый", "ий", "ой", "ая", "ья", "ое", "ье", "ые", "ьи", "ых", "их", "ьих", "ого", "его", "ьего",
                    "ому", "ему", "ьему", "ым", "им", "ьим", "ом", "ем", "ьем", "ую", "ью", "ей", "ьей", "ыми", "ими",
                    "ьими")
_ADJECTIVE_PLURAL = ("ых", "их", "ые", "ие", "ыми", "ими")
_RBNF_CASE = {"nominative": "", "genitive": "-genitive", "dative": "-dative", "accusative": "-accusative",
              "instrumental": "-ablative", "prepositional": "-locative"}


def standard(words: str) -> str:
    """A reading in the standard form. The number 1 is not said before "тысяча" or "миллион" at the start, as
    Грамматика-80 § 1378 declines "тысяча двести восемьдесят семь" and Розенталь § 164, п. 2 writes "в тысяча
    девятьсот шестьдесят пятом году". The number words take ё (Грамматика-80 § 1374, Правила-2006 § 5)."""
    first, _, rest = words.partition(" ")
    if first in _ONE_WORDS and _SCALE_WORD.match(rest):
        words = rest
    for written, spelled in _YO:
        words = words.replace(written, spelled)
    return " ".join(f"трём{word[4:]}" if word.startswith("трем") and not word.startswith("тремя") else word
                    for word in words.split())


def _rule_sets(kind: str) -> dict[Features, str]:
    """The RBNF rule set of each gender and case. The masculine and the neuter decline the same in the oblique
    cases (Грамматика-80 § 1374, § 1378), and the masculine cardinal of the prepositional takes the neuter rule set,
    because the masculine one keeps the tens in the nominative: "двадцать одном" for "двадцати одном"."""
    names = {Features(): f"spellout-{kind}-masculine"}
    for case, suffix in _RBNF_CASE.items():
        masculine = "neuter" if (kind, case) == ("cardinal", "prepositional") else "masculine"
        names[Features(case=case)] = f"spellout-{kind}-{masculine}{suffix}"
        for gender in (M, F, N):
            name = masculine if gender is M else gender.value
            names[Features(gender=gender, case=case)] = f"spellout-{kind}-{name}{suffix}"
    return names


class RussianSpeller:
    """ovos-number-parser for the nominative, and CLDR RBNF for the other cases and the plural ordinals."""

    def __init__(self):
        self.nominative = OvosNumberSpeller({M: "masculine", F: "feminine", N: "neutral"})
        self.cases = RbnfSpeller(cardinal=_rule_sets("cardinal"), ordinal=_rule_sets("ordinal"))
        self.plural = RbnfSpeller(cardinal={Features(): "spellout-cardinal-plural"},
                                  ordinal={Features(): "spellout-ordinal-plural"}
                                  | {Features(case=case): f"spellout-ordinal-plural{suffix}"
                                     for case, suffix in _RBNF_CASE.items()})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        if features.case in (None, "nominative"):
            words = self.nominative.cardinal(digits, Features(gender=features.gender), request)
        else:
            words = self.cases.cardinal(digits, features, request)
        return standard(words)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """RBNF reads no ordinal of 10 000 and above: it gives a cardinal such as "десять тысяч". A reading whose
        last word has no ending of an ordinal declines."""
        if features.number == "plural":
            words = self.plural.ordinal(digits, Features(case=features.case), request)
        elif features.case in (None, "nominative"):
            words = self.nominative.ordinal(digits, Features(gender=features.gender), request)
        else:
            words = self.cases.ordinal(digits, features, request)
        if not words.endswith(_ORDINAL_ENDINGS):
            raise DeclinedReading(f"no ordinal reading of {len(digits)} digits")
        return standard(words)

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
    genitive singular: "35,5 процента" (Розенталь § 164, п. 8; Грамматика-80 § 1367)."""
    category = plural_category(request, written)
    index = CASES.index(case)
    if category == "other":
        form = noun["singular"][1]
    elif case in ("nominative", "accusative"):
        form = {"one": noun["singular"][index], "few": noun["singular"][1]}.get(category, noun["plural"][1])
    else:
        form = noun["singular" if category == "one" else "plural"][index]
    return form + noun["tail"]


def governed_case(context: SpanContext, word_after: str = "", category: str = "many") -> str:
    """The case of a hint, else the case that the preposition before a number governs. A preposition of one case
    gives it (Грамматика-80 § 1657, § 1658). A preposition of two or three cases takes the one that the ending of
    the noun after the number shows: a plural ending, or after the category one a singular ending of the
    prepositional or the instrumental. With no such ending, the first case of `case_choices` applies."""
    if context.hint is not None and context.hint.case is not None:
        return context.hint.case
    data = context.request.data
    preposition = context.before[-1].lower() if context.before else ""
    if preposition in data["governed_cases"]:
        return data["governed_cases"][preposition]
    choices = data["case_choices"].get(preposition)
    if choices is None:
        return "nominative"
    word = word_after.lower()
    shown = next((case for ending, case in data["plural_endings"].items() if word.endswith(ending)), None)
    if category == "one":
        if preposition == "по":
            shown = "dative"
        elif word.endswith(("е", "и")):
            shown = "prepositional"
        elif word.endswith(("ом", "ем", "ём", "ой", "ей", "ью")):
            shown = "instrumental"
    return shown if shown in choices else choices[0]


def noun_gender(word: str, case: str, category: str) -> GrammaticalGender | None:
    """The gender that the ending of the word after a number shows (Грамматика-80 § 1134). In the nominative an
    adjective ends in -ая (feminine), -ое (neuter) or -ый, -ий, -ой (masculine); a noun with no ending is
    masculine, a noun in -а, -я feminine and a noun in -о, -е, -ё neuter, and a noun in -ь has either gender. After
    the category few the noun takes the genitive singular (Грамматика-80 § 1371), where -ы, -и mark the feminine
    and -а, -я the masculine and the neuter, which both read "два"."""
    word = word.lower()
    if not word or not all(is_letter(char) for char in word):
        return None
    if category == "one" and case in ("nominative", "accusative"):
        if word.endswith(("ая", "яя")) or (case == "accusative" and word.endswith(("ую", "юю", "у", "ю"))):
            return F
        if word.endswith(("ое", "ее", "о", "е", "ё")):
            return N
        if word.endswith(("ый", "ий", "ой")) or word[-1] not in "аяеёоиыуюэь":
            return M
        return F if word.endswith(("а", "я")) else None
    if (category, case) in (("one", "genitive"), ("few", "nominative"), ("few", "accusative")):
        return F if word.endswith(("ы", "и")) else M if word.endswith(("а", "я")) else None
    if category == "one" and case == "instrumental":
        return F if word.endswith(("ой", "ей", "ью")) else M if word.endswith(("ом", "ем", "ём")) else None
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
    case = governed_case(context, word, category)
    default = request.params.default_gender.get(request.language.code) or request.language.default_gender
    return Features(gender=noun_gender(word, case, category) or default, case=case)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


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
    case = governed_case(context)
    words = _amount(amount, GrammaticalGender(noun["gender"]), case, request)
    if span.trail.strip() == request.data["range_word"]:
        return words
    return f"{words} {counted(noun, _written(amount), case, request)}"


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal in the gender and the case of its context. Digits with a leading zero after a lead read one by
    one."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = " ".join(request.data["digit_words"][int(digit)] for digit in digits)
    else:
        words = SPELLER.cardinal(digits, agreement(digits, context), request)
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


def speak_date(span: Span, context: SpanContext) -> str:
    """"двенадцатое марта две тысячи двадцать четвёртого года": the day a neuter ordinal in the case of the
    preposition, the month in the genitive ("Первое мая", Розенталь § 20) and the year a genitive ordinal of which
    only the last word declines (Розенталь § 164, п. 2). A form of "год" that the text writes after the date
    stands in place of "года"."""
    request, fields = context.request, span.fields
    words = []
    if fields["day"] is not None:
        words.append(SPELLER.ordinal(str(fields["day"]), Features(gender=N, case=governed_case(context)), request))
    words.append(request.data["months"][fields["month"] - 1])
    if fields["year"] is not None:
        words.append(SPELLER.year(str(fields["year"]), Features(case="genitive"), request))
        if fields["suffix"] or not (context.after and context.after[0].lower() in request.data["year_noun"]):
            words.append(request.data["year_noun"][1])
    return " ".join(words)


def speak_year(span: Span, context: SpanContext) -> str:
    """The case of a year comes from the form of "год" after it: "в 2024 году" is the prepositional, "к 2024
    году" the dative, "2024 года" the genitive. After `г.` the preposition gives the case, and the span reads the
    form of "год" in that case."""
    request = context.request
    nouns = request.data["year_noun"]
    if span.fields["suffix"]:
        case = "prepositional" if context.before and context.before[-1].lower() in ("в", "во") \
            else governed_case(context)
        words = SPELLER.year(span.fields["digits"], Features(case=case), request)
        return f"{words} {nouns[CASES.index(case)]}"
    noun = context.after[0].lower() if context.after else ""
    case = CASES[nouns.index(noun)] if noun in nouns else "nominative"
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
    § 111, п. 1). `млн` and `млрд` after a number agree with it as nouns (Грамматика-80 § 1371)."""
    data, key = context.request.data, span.fields["key"]
    if key in data["scales"]:
        number = context.before[-1]
        case = governed_case(replace(context, before=context.before[:-1]))
        return counted(data["scale_nouns"][data["scales"][key]], number, case, context.request)
    return data["titles"].get(key) or data["abbreviations"][key]


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """The core attachment, but a suffix `г.` after a year is the abbreviation of "год", which the verbalizer of
    the year or the date reads."""
    return prefix + spoken + ("" if suffix.lstrip() == "г." else suffix)


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
    which the span holds: `в 1965 г.`."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        nouns = "|".join(sorted(set(request.data["year_noun"]), key=len, reverse=True))
        pattern = f"([0-9]{{4}})(?:[  ](?:{nouns})(?![^ .,;:!?)])|([  ]г[.]))"
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
    The span holds `г.` after the year."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months = request.data["months"]
        pattern = f"([0-9][0-9]?)[  ]({'|'.join(months)})(?:[  ]([0-9]{{4}})([  ]г[.])?)?"
        for match in re.finditer(pattern, fold_digits(text)):
            start, end = match.span()
            day, month = int(match.group(1)), months.index(match.group(2)) + 1
            year = int(match.group(3)) if match.group(3) else None
            if not (is_bounded(text, start, end if match.group(4) else end) and one_digit_set(text[start:end])
                    and is_valid(year, month, day)) or (start and text[start - 1] in ".,/-"):
                continue
            suffix = match.group(4) or ""
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year, "month": month, "day": day, "written_order": "DMY",
                                  "month_written": "name", "prefix": "", "suffix": suffix}),
                       trail="." if suffix and _sentence_end(text, end) else "", recognizer=self.name)


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
class Abbreviation:
    """A title before a capitalised word, an abbreviation of the `abbreviations` table, and `млн` or `млрд` after a
    number. A full stop that ends the sentence stays after the reading."""
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
                        trail = "." if table != "titles" and key.endswith(".") and _sentence_end(text, end) else ""
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}), trail=trail,
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
    recognizers=(SHARED["lexicon"], DateNamed(), SHARED["date_numeric"], Clock(), Year(), HyphenOrdinal(),
                 SpacedNumber(), SHARED["money"], SHARED["percent"], SHARED["measure"], ExpressionGuard(),
                 SHARED["fraction"], Abbreviation(), OtherDecimalMark(), SHARED["decimal"], SHARED["cardinal"]),
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
