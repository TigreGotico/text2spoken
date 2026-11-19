"""Chinese (Mandarin): zh-CN, the default variety, in Simplified characters, and zh-TW, in Traditional characters.

The sources are CLDR 49 (the RBNF rules `rbnf/zh.xml` and `rbnf/zh_Hant.xml`, and the cldr-json number, unit,
currency and calendar data of `zh` and `zh-Hant`) and English Wiktionary, Chinese section of each entry named below.

Chinese writes a number next to the word that follows it, with no space: CLDR 49 `zh` writes the unit pattern
"{0}千克" and the long date pattern "y年M月d日". The shared recognizers find a number only between word boundaries,
so each recognizer of this file reads the text with every Han character (a CJK unified or compatibility ideograph)
as a space (`han_view`). A Latin letter next to a number still keeps it as written, as in `5G` and `G20`.

The number words come from CLDR RBNF. A plain number reads through `spellout-cardinal`, which writes "2: 二" and "0:
零", the decimal rule "x.x: <<点>>>" (zh_Hant "<<點>>>") and the minus rule "-x: 负>>" (zh_Hant "負>>"). Wiktionary
"零" writes zero inside a number: "七 百 零 三 | seven hundred and three". Wiktionary "點" gives the decimal point:
"三 點 二 四 | three point two four".

A number before a measure word reads through `spellout-cardinal-alternate2`, which writes "2: 两" (zh_Hant "2: 兩")
and keeps "20: =%spellout-numbering=", so 22 is 二十二. Wiktionary "兩", usage notes: "In many lects, including
Standard Mandarin, 兩 is used when counting things with a measure word, 二 is used in numbers", with the examples "兩
個 人", "兩 年", "兩 百", "兩 千" for 兩 and "二十", "二 百", "第二" for 二, "But not *二個人", and the table row
"三十兩 | thirty-two | Mandarin -". The words of `number_words` with the value `counter` are the measure words. Each
has a classifier sense in its Wiktionary entry, in the Traditional form; the Simplified form is the same entry:
個 个 "people or for things lacking specific classifiers", 位 "persons", 本 "books, periodicals, files", 隻 只 "one of
a pair", 張 张 "objects that can be expanded", 條 条 "long and thin objects or animals", 件 "things which can be
numerically counted", 次 "times, as in frequency", 天 "day (24 hours)" (classifier), 種 种 "varieties", 歲 岁 "age (of
a person or animal)", 頭 头 "livestock", 輛 辆 "wheeled vehicles", 臺 台 "machines, vehicles or electronic devices",
家 "Classifier for families, businesses and companies", 座 "buildings, mountains and similar immovable objects", 塊 块
"piece of something", 元 "yuan or dollars", 角 "money", 噸 吨 "metric ton", 秒 "time | second", 倍 "the number of
times a value is multiplied", 份 "things that are part of a whole", 雙 双 "a pair of objects", 對 对 "pairs of
objects", 句 "sentences", 首 "songs and poems", 篇 "written items", 部 "works of literature, films, machines", 架
"planes, large vehicles", 棵 "plants", 朵 "flowers, clouds", 片 "flat objects", 杯 "cups/glasses of drinks/food", 碗
"the quantity of a bowl", 瓶 "bottled objects", 遍 "occurrences of events", 場 场 "sporting or recreational
activities", 年 "years" ("兩 年 前 | two years ago"), and the classifier entries 公斤, 千克, 公里, 千米, 釐米 厘米, 毫米,
公分 and 小時 小时. 點 点 reads "o'clock, following the numbered hour" (Wiktionary "點", usage notes), and Wiktionary
"兩點" is "two o'clock". 分 is "minute (unit of time)", as in "十二點三十分" of the same note. The numerals 百, 千, 萬 万
and 億 亿 after a number take the same form: Wiktionary "兩 百", "兩 千", and the CLDR rules "10000: <<万[...]" and
"100000000: <<亿[...]" of `spellout-cardinal-alternate2`, whose multiplier 2 reads 两.

A number before a word of `number_words` with the value `label` names an item and reads as a plain number: 月
(Wiktionary "月", "month", counted with the measure word 個, and "二月", "February"), 號 号 ("number", "day of the
month"), 年代 ("a decade of a century") and 分之 (below). Before 日 the number is the day of the month after a month,
as "5月1日" (Wiktionary "日", "day of the month"). Elsewhere it may count days (Wiktionary "日", classifier "days"),
so the next rule applies. 年級 年级 ("grade; year") starts with the measure word 年 but is a word of its own, and the
next rule applies to it too. A number before any other Han character reads only where both rule sets give the same
words, so `3人` reads 三人 and `2人` stays as written: the file has no source for which form the word takes. A number
with a minus before a measure word follows the same rule.

A number after 第 is an ordinal: Wiktionary "第", "Ordinal number marker, used before a number to make the number
ordinal", "第二 | second". CLDR 49 `spellout-ordinal` writes "0: 第=%spellout-numbering=;", so the number reads
through `spellout-numbering` and the text keeps 第.

A year reads by the CLDR 49 rule set `spellout-numbering-year`: "1000: =%%spellout-numbering-year-digits=;" with
"10: <<>>>; 100: <<>>>; 1000: <<>>>;", so each digit of a year from 1000 to 9999 reads through `spellout-numbering`,
whose zero is "0: 〇;". 2023 reads 二〇二三. Wiktionary "〇" names the sign a zero digit, "Used to express a zero digit
in a number since at least the (c.) 12th century". A year below 1000 or above 9999 reads through `spellout-numbering`.
zh_Hant reads a round thousand through `spellout-numbering` ("2000: =%spellout-numbering=; 2001:
=%%spellout-numbering-year-digits=;"), so the zh-TW year 2000 is 二千. unicode-rbnf drops the zeros of this rule set
(2023 gives "二二三"), so the file applies the rule itself, with the digit words of `spellout-numbering`.

A number before 年 ("years", above) is a year or a count of years. It is a year after a word of `year_words`:
Wiktionary "公元", "anno Domini (AD); Common Era (CE)", "西元", "(Taiwan, Hong Kong) anno Domini", and "民國", "the
Republic of China era". A number of four digits is a year, and so is one before 年代. A round hundred of four digits,
as `2000年`, can also count years, as in 有2000年的历史, so it is a year only when a month follows, as `2000年5月`; else
it stays as written. Any other number before 年 counts years.

A percentage reads 百分之 and the number: Wiktionary "百分之", "In Chinese, percentages are written in the format 百分之
[number of hundredths]", "百分之 八 | eight percent". A fraction reads the denominator, 分之 and the numerator: Wiktionary
"分之", "In Chinese, fractions are written in the format denominator 分之 numerator", "三 分之 一 | a third". A
fraction reads where the shared `fraction` recognizer reads it: a proper fraction with a denominator from 2 to 100.

Currency names come from CLDR 49 (`currencies.json` of `zh` and `zh-Hant`), after the amount, which reads as a
number before a measure word: US$5 reads 五美元. The renminbi and the New Taiwan dollar read 元, Wiktionary "元",
classifier "yuan or dollars", "一 元 人民幣 | one Chinese yuan", where CLDR names the currency (人民币, 新台幣). An
amount with decimals, or with a numeral after it, as `¥3亿`, stays as written.

Units come from CLDR 49 (`cldr-units-full`, the `long` pattern of the variety): `5kg` reads 五千克 in zh-CN. The
letter `g` alone is no unit, because it ends names such as `802.11g`. zh-Hant writes no Latin symbol for most units,
so zh-TW reads only the units whose symbol is no word, as `°C`, "攝氏 {0} 度".

A numeric date with the year first, as `2023-05-01`, reads in the CLDR 49 `zh` long date pattern "y年M月d日", with the
year read as a year. Any other order stays as written, unless say-as markup gives the order of the
fields. A time, as `12:30`, stays as written.

The number words come from the CLDR locale of the tag: `zh` for zh-CN, and `zh_Hant` for a tag with the script
Hant, as zh-Hant-TW, which writes 兩, 點, 萬, 億 and 負. CLDR 49 likelySubtags gives "zh-TW": "zh-Hant-TW", and the
CLDR currency and unit data of the variety zh-TW follow it (`scripts/extract_cldr.py`).
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.dates import date_locales, long_date
from text2spoken.core.language import LanguageSpec, Request, Variety, cldr_locale
from text2spoken.core.recognizers import (SHARED, Cardinal, DateNumeric, Decimal, Fraction, Measure, Money, Percent,
                                          speak_lexicon)
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import RbnfSpeller, bounded_integer
from text2spoken.core.tokens import Token, is_digit
from text2spoken.core.units import unit_reading
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, Form, freeze

COUNTERS = (
    "個 个 位 本 隻 只 張 张 條 条 件 次 天 種 种 歲 岁 頭 头 輛 辆 臺 台 家 座 塊 块 元 角 噸 吨 秒 倍 份 雙 双 對 对 句 首 篇 部 架 棵 朵 片 杯 "
    "碗 瓶 遍 場 场 年 點 点 分 公斤 千克 公里 千米 釐米 厘米 毫米 公分 小時 小时 百 千 萬 万 億 亿"
).split()

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
    "sign_words": {"-": "负"},
    "leads": {},
    "symbols": {"%": "percent", "％": "percent", "¥": "money", "￥": "money", "$": "money", "€": "money", "£": "money",
                "°": "measure"},
    "percent": {"signs": ["%", "％"], "position": "after", "word": "百分之"},
    "fraction_word": "分之",
    "ordinal_marker": "第",
    "currency_symbols": [],
    "currencies": {"CNY": {"other": "元"}, "TWD": {"other": "元"}},
    "scales": {},
    "unit_symbols": ["kg"],
    "dimension_marks": [],
    "number_words": {**{word: "counter" for word in COUNTERS},
                     "月": "label", "號": "label", "号": "label", "年代": "label", "分之": "label", "日": "day",
                     "年級": "word", "年级": "word"},
    "year_words": ["公元", "公元前", "西元", "西元前", "民國", "民国"],
    "round_thousand_years": "digits",
})

VARIETIES = (
    Variety("zh-CN"),
    Variety("zh-TW", freeze({"round_thousand_years": "numbering"})),
)

NUMERALS = frozenset("百千萬万億亿兆")
"""The numerals that may follow a number written in digits, as in `3万`."""

SPACES = "   　"
"""The space, the no-break space, the narrow no-break space and the ideographic space."""


def is_han(char: str) -> bool:
    """Whether the character is a Han character: a CJK unified ideograph or a CJK compatibility ideograph."""
    return unicodedata.name(char, "").startswith(("CJK UNIFIED IDEOGRAPH", "CJK COMPATIBILITY IDEOGRAPH"))


def han_view(text: str, memo: dict) -> str:
    """The text with each Han character as a space. The length and every offset stay the same. `memo`, the memo of
    the request, keeps the view for the rest of the call."""
    key = ("zh han view", text)
    if key not in memo:
        memo[key] = "".join(" " if is_han(char) else char for char in text)
    return memo[key]


class ZhSpeller:
    """The number words of CLDR RBNF `zh` and `zh_Hant`: `plain` reads a number, `counted` a number before a measure
    word, and `numbering` the digits of a year."""

    def __init__(self):
        self.plain = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"},
                                 decimal="spellout-cardinal")
        self.counted = RbnfSpeller(cardinal={Features(): "spellout-cardinal-alternate2"},
                                   ordinal={Features(): "spellout-cardinal-alternate2"})
        self.numbering = RbnfSpeller(cardinal={Features(): "spellout-numbering"},
                                     ordinal={Features(): "spellout-numbering"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.plain.cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.plain.ordinal(digits, features, request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or (len(digits) > 1 and digits[0] == "0"):
            raise DeclinedReading("a year is a number with no leading zero")
        round_thousand = value % 1000 == 0 and request.data["round_thousand_years"] == "numbering"
        if 1000 <= value <= 9999 and not round_thousand:
            return "".join(self.numbering.cardinal(digit, features, request) for digit in digits)
        return self.numbering.cardinal(digits, features, request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        return self.plain.decimal(integer, fraction, features, request)

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        cardinal = self.plain.cardinal
        return cardinal(denominator, features, request) + request.data["fraction_word"] + cardinal(numerator, features,
                                                                                                    request)


SPELLER = ZhSpeller()


def _year(written: str, digits: str, before: str, after: str, data) -> str | None:
    """`year`, `kept` or None (no year) for a number before 年: the rules of the module docstring."""
    if any(before.endswith(word) for word in data["year_words"]) and len(digits) <= 4:
        return "year"
    if len(digits) != 4 or written != digits or digits[0] == "0":
        return None
    if after.startswith("年代") or int(digits) % 100:
        return "year"
    month = after[1:].lstrip("0123456789０１２３４５６７８９")
    return "year" if month.startswith("月") and len(after) - 1 - len(month) in (1, 2) else "kept"


def _differs(digits: str, request: Request) -> bool:
    """Whether a number reads in other words before a measure word."""
    try:
        return SPELLER.plain.cardinal(digits, Features(), request) != SPELLER.counted.cardinal(digits, Features(),
                                                                                                request)
    except DeclinedReading:
        return True


def _role(text: str, span: Span, request: Request) -> tuple[Span, str]:
    """The span of a number with the Han character after it when a digit follows that character, and the role of
    the number: `ordinal`, `year`, `counted`, `plain` or `kept`. A span of a number that a single Han character joins
    to another number holds that character, so that the core does not hold the two numbers as one run."""
    data = request.data
    digits, sign = span.fields["digits"], span.fields["sign"]
    before = text[:span.start].rstrip(SPACES)
    rest = text[span.end:]
    gap = len(rest) - len(rest.lstrip(SPACES))
    after = rest[gap:]
    kind = data["number_words"].get(max((word for word in data["number_words"] if after.startswith(word)), key=len,
                                        default=""))
    year = None if sign or not after.startswith("年") else _year(text[span.start:span.end], digits, before, after,
                                                                  data)
    if not sign and before.endswith(data["ordinal_marker"]):
        role = "ordinal"
    elif year is not None:
        role = year
    elif kind == "counter":
        role = "kept" if sign and _differs(digits, request) else "counted"
    elif kind == "label" or (kind == "day" and text[:span.start].endswith("月")):
        role = "plain"
    elif after[:1] and is_han(after[0]) and _differs(digits, request):
        role = "kept"
    else:
        role = "plain"
    if role != "kept" and not gap and len(after) > 1 and is_han(after[0]) and is_digit(after[1]):
        span = replace(span, end=span.end + 1, fields=freeze({**span.fields, "suffix": after[0]}))
    return span, role


def numbers(text: str, tokens: Sequence[Token], request: Request) -> tuple[tuple[Span, str], ...]:
    """Each whole number of the text that the shared `cardinal` recognizer finds in `han_view`, with its role."""
    key = ("zh numbers", text)
    if key not in request.memo:
        found = SHARED["cardinal"].find(han_view(text, request.memo), tokens, request)
        request.memo[key] = tuple(_role(text, span, request) for span in found)
    return request.memo[key]


class ZhCardinal(Cardinal):
    """A number that reads as a cardinal: `counted` before a measure word, else `plain`. A number of another role
    stays as written when the form of that role is off."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span, role in numbers(text, tokens, request):
            if role in ("counted", "plain"):
                yield replace(span, recognizer=f"{self.name}:{role}")
            else:
                yield replace(span, keep=True)


class ZhYear:
    name = "zh_year"
    form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span, role in numbers(text, tokens, request):
            if role == "year":
                yield Span(span.start, span.end, Form.YEAR,
                           freeze({"digits": span.fields["digits"], "suffix": span.fields["suffix"]}),
                           recognizer=self.name)


class ZhOrdinal:
    name = "zh_ordinal"
    form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span, role in numbers(text, tokens, request):
            if role == "ordinal":
                fields = span.fields
                yield Span(span.start, span.end, Form.ORDINAL,
                           freeze({"digits": fields["digits"], "marker": request.data["ordinal_marker"], "prefix": "",
                                   "suffix": fields["suffix"], "script": fields["script"]}), recognizer=self.name)


class ZhDecimal(Decimal):
    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return super().find(han_view(text, request.memo), tokens, request)


class ZhPercent(Percent):
    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return super().find(han_view(text, request.memo), tokens, request)


class ZhFraction(Fraction):
    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return super().find(han_view(text, request.memo), tokens, request)


class ZhDate(DateNumeric):
    """A numeric date with the year first. Any other order stays as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(han_view(text, request.memo), tokens, request):
            if span.fields["written_order"] == "YMD":
                yield span


class ZhMeasure(Measure):
    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return super().find(han_view(text, request.memo), tokens, request)


class ZhMoney(Money):
    """An amount with a numeral after it, as `¥3亿`, stays as written: the numeral belongs to the number."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(han_view(text, request.memo), tokens, request):
            yield replace(span, keep=True) if text[span.end:span.end + 1] in NUMERALS else span


def _signed(digits: str, sign: str, speller: RbnfSpeller, request: Request) -> str:
    if sign == "-":
        return speller.negative_cardinal(digits, Features(), request)
    if sign:
        raise DeclinedReading(f"no sign word for {sign!r}")
    return speller.cardinal(digits, Features(), request)


def _amount(amount, speller: RbnfSpeller, request: Request) -> str:
    """A `DECIMAL` record: a decimal through `spellout-cardinal`, an integer through the speller."""
    integer, fraction, sign = amount["integer"] or "0", amount["fraction"], amount["sign"]
    if len(integer) > 1 and integer[0] == "0":
        raise DeclinedReading("a number with a leading zero")
    if not fraction:
        return _signed(integer, sign, speller, request)
    if sign == "-":
        return SPELLER.plain.negative_decimal(integer, fraction, Features(), request)
    if sign:
        raise DeclinedReading(f"no sign word for {sign!r}")
    return SPELLER.plain.decimal(integer, fraction, Features(), request)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    speller = SPELLER.counted if span.recognizer.endswith(":counted") else SPELLER.plain
    return _signed(span.fields["digits"], span.fields["sign"], speller, context.request)


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """The number after 第, which stays in the text: `spellout-ordinal` without its 第."""
    return SPELLER.numbering.cardinal(span.fields["digits"], Features(), context.request)


def speak_year(span: Span, context: SpanContext) -> str:
    return SPELLER.year(span.fields["digits"], Features(), context.request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _amount(span.fields, SPELLER.plain, context.request)


def speak_percent(span: Span, context: SpanContext) -> str:
    request = context.request
    amount = span.fields["amount"]
    if amount["sign"]:
        raise DeclinedReading("the file has no source for a signed percentage")
    return request.data["percent"]["word"] + _amount(amount, SPELLER.plain, request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields = span.fields
    if fields["whole"] or fields["sign"]:
        raise DeclinedReading("the file has no source for a mixed or signed fraction")
    return SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request)


def speak_money(span: Span, context: SpanContext) -> str:
    request, fields = context.request, span.fields
    amount = fields["amount"]
    if amount["fraction"] or amount["sign"] or fields["scale"]:
        raise DeclinedReading("the file has no source for the reading of this amount")
    name = currency_name(currency_table(request)[fields["currency"]], "other")
    return _amount(amount, SPELLER.counted, request) + name


def speak_measure(span: Span, context: SpanContext) -> str:
    request, fields = context.request, span.fields
    if fields["relation"]:
        raise DeclinedReading("the file reads one amount and its unit")
    pattern, _ = unit_reading(request, fields["unit"], "other")
    return pattern.replace("{0}", _amount(fields["amount"], SPELLER.counted, request))


DATE_FIELDS = {"year": SPELLER.year, "month": SPELLER.cardinal, "day": SPELLER.cardinal}
"""The reading of each field of the long date pattern."""


def speak_date(span: Span, context: SpanContext) -> str:
    """A date in the parts of the CLDR long date pattern."""
    request, fields = context.request, span.fields
    parts, _ = long_date(cldr_locale(request.tag, date_locales(), request.language))
    if any(name not in DATE_FIELDS and name != "text" for name, _ in parts):
        raise DeclinedReading("the long date pattern holds a field that the file does not read")
    return "".join(literal if name == "text" else DATE_FIELDS[name](str(fields[name]), Features(), request)
                   for name, literal in parts)


LANGUAGE = LanguageSpec(
    code="zh",
    serves=("cmn",),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], ZhMoney(), ZhPercent(), ZhMeasure(), ZhFraction(), ZhDate(), ZhDecimal(),
                 ZhYear(), ZhOrdinal(), ZhCardinal()),
    verbalizers={Form.LEXICON: speak_lexicon, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
                 Form.MEASURE: speak_measure, Form.FRACTION: speak_fraction, Form.DATE: speak_date,
                 Form.DECIMAL: speak_decimal, Form.YEAR: speak_year, Form.ORDINAL: speak_ordinal,
                 Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.YEAR: SPELLER, Form.DECIMAL: SPELLER,
              Form.FRACTION: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
