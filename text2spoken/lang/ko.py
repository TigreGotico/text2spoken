"""Korean: ko-KR.

The number words come from the CLDR RBNF rule sets of `ko` (`common/rbnf/ko.xml`, as unicode-rbnf ships it). A
number reads through `spellout-numbering`, whose rule "1: =%spellout-cardinal-sinokorean=;" reads every number from
1 up in the Sino-Korean numerals, as `123456789` reads 일억 이천삼백사십오만 육천칠백팔십구, and whose rule "0: 공;"
reads zero. A decimal reads through the rule "x.x: ←←점→→→;" of the same rule set: `3.5` reads 삼점오. The decimal
mark `.` and the group mark `,` come from the CLDR 49 number symbols of `ko`.

Korean writes a number in digits right before its counter, with no space: the Hangul Orthography (한글 맞춤법),
article 43, "단위를 나타내는 명사는 띄어 쓴다", and "다만, 순서를 나타내는 경우나 숫자와 어울리어 쓰이는 경우에는 붙여 쓸 수 있다", with
"1446년 10월 9일", "80원" and "10개". The cardinal recognizer reads the text with each Hangul syllable as a space
so that it finds the number, and the words after the number decide its reading. A number reads with a
counter of `counters` right after it, alone or after one space, and the counter reads after one space, as article 43
writes it: `23개` reads 스물세 개. The longest counter counts, so that `3개월` is no 개, and the Hangul after the
counter must be empty or start with a word of `counter_followers`; it stays as written after the counter, so that
`3명이` reads 세 명이. Any other Hangul right after the number keeps the number as written, as it stays on dev, and so
does Hangul right before it, as in `제3`, and a range mark next to it, as in `3~4개`. A number before a space and a
word that is no counter reads as a plain number.

The counter decides the numerals. The Standard Korean Language Dictionary (표준국어대사전) gives each:

- `native`, the attributive native numeral of RBNF `spellout-cardinal-native-attributive` ("1: 한;", "2: 두;", "3: 세;",
  "4: 네;", "20: 스무;", "21: 스물[→→];"), which the dictionary heads "「관형사」 ((일부 단위를 나타내는 말 앞에 쓰여))", as
  "두": "사과 두 개" and "스무": "스무 살. 스무 명. 스무 개. 스무 마리쯤 되는 닭". 개 ("사탕 한 개"), 명 ("한 명", "열댓 명"),
  마리 ("소 한 마리. 새 두 마리. 모기 다섯 마리"), 살 ("((주로 고유어 수 뒤에 쓰여)) 나이를 세는 단위. 두 살 먹은 꼬마") and
  시간 ("두 시간 동안 책을 읽다", and "네": "네 시간"). The native numerals end at 99 (아흔아홉), and the dictionary gives no
  reading of 100 and up before these counters, so such a number stays as written; so does 0. 명 also counts in the
  Sino-Korean numerals ("학생 삼십 명"), and the file reads the native ones, which the dictionary gives first.
- `hour`, 시 for the hour of a clock: "지금은 세 시가 조금 넘었다. 정각 열 시에 만납시다", and article 43: "두 시 삼십 분 오
  초". It reads the native numeral from 1 to 12; the dictionary gives no hour of a 24-hour clock, so 13 and up stays as
  written.
- `sino`, the Sino-Korean numeral of `spellout-numbering`, the plain reading. 년 ("((주로 한자어 수 뒤에 쓰여)) 해를 세는
  단위", "팔 년"), 일 ("((한자어 수 뒤에 쓰여)) 날을 세는 단위. 삼 일 동안"), 개월 ("((한자어 수 뒤에 쓰여)) 달을 세는 단위",
  "삼 개월"), 원 ("칠": "칠 원", "십": "십 원", "원": "천 원으로 과자를 사 먹었다") and 층 ("삼": "교실은 삼 층에 있다",
  article 43: "육 층").
- `minute`, 분 after an hour: article 43, "두 시 삼십 분", and "분": "한 시간의 60분의 1". 분 also counts honoured persons
  in the native numerals ("손님 다섯 분", "선생님 두 분"), so 분 reads only right after a number and 시, as in `3시 20분`,
  and stays as written elsewhere.
- `month`, 월 after a number from 1 to 12, which reads the month name of `months`, as in a date: `6월` reads 유월.

A counter with a minus stays as written. The words of `counter_followers` are case particles and suffixes of the
dictionary that follow a noun: 이, 가, 을, 를, 은, 는, 의, 에, 와, 과, 로, 으로, 도, 만, 까지, 부터 (each a 「조사」), the
서술격 조사 "이다", and the suffixes "-쯤", "-씩" ("((수량을 나타내는 말 뒤에 붙어))", "두 사람씩", "다섯 마리씩") and "-째"
("두 잔째").

A minus reads 마이너스 before the number, by the rule "-x: 마이너스 →→;" of `spellout-cardinal-sinokorean`, the rule
set that `spellout-numbering` reads from 1 up: `-5` reads 마이너스 오 and `-3.5` 마이너스 삼점오. The Standard Korean
Language Dictionary of the National Institute of Korean Language (표준국어대사전, 국립국어원), "마이너스", sense
「4」: "『수학』 뺄셈의 부호 ‘-’를 이르는 말", and sense 「5」: "『수학』 어떤 수가 0보다 작은 일". A minus that may mark
something else keeps the number as written, as for a language with no file (design section 6.1): a range or a code
after a number or a dash, as `5 -10`, and an amount next to a currency sign, as `-50 ₩`.

Money, percentages, measures, numeric dates, fractions and ordinals with a full stop stay as written, as for a
language with no file (design section 6.1).

A say-as `ordinal` reads the native ordinal, through the RBNF rule set `spellout-ordinal-native`: 1 첫째, 2 둘째, 3 셋째,
11 열한째, 12 열두째, 20 스무째, 22 스물두째. The Standard Korean Language Dictionary gives each of these words as a
수사 "순서가 … 번째가 되는 차례", as "셋째": "순서가 세 번째가 되는 차례". The suffix "-째" makes the ordinal of a
numeral: "((수량, 기간을 나타내는 명사 또는 명사구 뒤와 수사 뒤에 붙어)) ‘차례’나 ‘등급’의 뜻을 더하는 접미사. 몇째. 두 잔째.
여덟 바퀴째. 둘째. 셋째". The Standard Language Rules (표준어 규정), article 6, keep 둘째, 셋째 and 넷째 and write 두째 after a
ten: "다만, ‘둘째’는 십 단위 이상의 서수사에 쓰일 때에 ‘두째’로 한다", with "열두째" and "스물두째"; the RBNF rule set writes the
same. The native numerals end at 99 (아흔아홉), and RBNF reads 100 and up with Sino-Korean hundreds, as "백한째", which no
source gives, so an ordinal of 0 or of 100 and up declines to the plain reading.

A say-as `date` reads in the CLDR 49 `long` date pattern of `ko`, `y년 MMMM d일`. The year and the day read as cardinals,
and the month reads its name from `months`. CLDR writes the month names `1월` to `12월`, and each reads its Sino-Korean
numeral and 월, except June and October. The Hangul Orthography (한글 맞춤법), article 52: "한자어에서 본음으로도 나고
속음으로도 나는 것은 각각 그 소리에 따라 적는다", with "오뉴월, 유월(六月)" and "시방정토(十方淨土), 시왕(十王), 시월(十月)" in the column
of the 속음. The Standard Korean Language Dictionary, "유월": "‘유월(六月)’에서 ‘六’은 본음이 ‘륙’이지만 ‘육월’로 적지 않고
‘유월’로 적는다", and "시월": "‘十’은 본음이 ‘십’이지만 ‘십월’로 적지 않고 ‘시월’로 적는다". So `2026-06-10` reads 이천이십육년
유월 십일 and `2026-10-06` 이천이십육년 시월 육일.
"""
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import long_date
from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (RBNF_DECIMAL, SHARED, OrdinalStop, RbnfCardinal, signed, speak_decimal,
                                          speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Recognizer, Span, SpanContext
from text2spoken.core.tokens import Token
from text2spoken.core.spellers import RbnfSpeller, bounded_integer
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, Form, FrozenMap, freeze

SPELLER = RbnfSpeller(cardinal={Features(): "spellout-numbering"}, ordinal={Features(): "spellout-numbering"},
                      decimal="spellout-numbering")

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
    "sign_words": {"-": "마이너스"},
    "leads": {},
    "counters": {"개": "native", "명": "native", "마리": "native", "살": "native", "시간": "native", "시": "hour",
                 "년": "sino", "일": "sino", "개월": "sino", "원": "sino", "층": "sino", "분": "minute", "월": "month"},
    "counter_followers": ["이", "가", "을", "를", "은", "는", "의", "에", "와", "과", "로", "으로", "도", "만", "까지", "부터",
                          "쯤", "씩", "째"],
    "months": ["일월", "이월", "삼월", "사월", "오월", "유월", "칠월", "팔월", "구월", "시월", "십일월", "십이월"],
})


NATIVE = RbnfSpeller(cardinal={Features(): "spellout-cardinal-native-attributive"},
                     ordinal={Features(): "spellout-cardinal-native-attributive"})
"""The attributive native numerals, which a native counter reads."""


class OrdinalSpeller(RbnfSpeller):
    """The native ordinal of RBNF `spellout-ordinal-native`, from 1 to 99."""

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or not 1 <= value <= 99 or digits[0] == "0":
            raise DeclinedReading("a native ordinal reads a number from 1 to 99")
        return super().ordinal(digits, features, request)


ORDINAL = OrdinalSpeller(cardinal={Features(): "spellout-numbering"},
                         ordinal={Features(): "spellout-ordinal-native"})

SHAPES = (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"], SHARED["fraction"],
          OrdinalStop())
"""The forms that stay as written. The RBNF data of `ko` has its own rule set `digits-ordinal`, so a full stop after
a number is no ordinal mark alone (`OrdinalStop` with no `bare_stop`), as for a language with no file."""

HANGUL_SPACES = dict.fromkeys(range(ord("가"), ord("힣") + 1), " ")
"""Each precomposed Hangul syllable as a space, for `str.translate`."""

RANGE_MARKS = "~～-–"
"""The marks that join two numbers into a range, as in `3~4개`."""

LIMITS = {"native": 99, "hour": 12, "month": 12}
"""The largest number that each kind of counter reads."""


def is_hangul(char: str) -> bool:
    return "가" <= char <= "힣"


def _reading(text: str, span: Span, data) -> tuple[Span, str | None]:
    """The span with its counter and the counter, the span and "" for a plain number, or None to keep it as written."""
    start = span.start + len(span.fields["prefix"])
    rest = text[span.end:]
    if is_hangul(text[start - 1:start]) or (rest[1:2].isdecimal() and rest[0] in RANGE_MARKS) \
            or (start > 1 and text[start - 1] in RANGE_MARKS and text[start - 2].isdecimal()):
        return span, None
    gap = 1 if rest[:1] == " " and is_hangul(rest[1:2]) else 0
    counter = max((word for word in data["counters"] if rest.startswith(word, gap)), key=len, default="")
    end = gap + len(counter)
    while counter and is_hangul(rest[end:end + 1]):
        end += 1
    after = rest[gap + len(counter):end]
    if not counter or (after and not after.startswith(data["counter_followers"])):
        return span, (None if is_hangul(rest[:1]) else "")
    kind = data["counters"][counter]
    value = bounded_integer(span.fields["digits"])
    hour = text[max(span.start - 4, 0):span.start].removesuffix(" ")
    if span.fields["sign"] or not value or value > LIMITS.get(kind, value) or (kind == "minute" and not (
            hour.endswith("시") and hour[:-1].removesuffix(" ")[-1:].isdecimal())):
        return span, None
    return replace(span, end=span.end + end, fields=FrozenMap({**span.fields, "suffix": after})), counter


@dataclass(frozen=True)
class KoCardinal(RbnfCardinal):
    """The core cardinal, found with Hangul as spaces, with the counter after it in the recognizer name."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text.translate(HANGUL_SPACES), tokens, request):
            if span.keep:
                yield span
                continue
            span, counter = _reading(text, span, request.data)
            if counter is None:
                yield replace(span, keep=True)
            else:
                yield replace(span, recognizer=f"{self.name}:{counter}" if counter else self.name)


KEPT_FIELDS = FrozenMap(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


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
        return (replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)
                for span in self.shape.find(text, tokens, request))


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal after the word of its sign, or a number and its counter in the numerals of the counter. Minus zero
    declines: the `-x` rule reads no sign for zero."""
    request, digits, sign = context.request, span.fields["digits"], span.fields["sign"]
    if sign and not digits.strip("0"):
        raise DeclinedReading("minus zero has no sign word")
    counter = span.recognizer.partition(":")[2]
    if not counter:
        return signed(SPELLER.cardinal(digits, Features(), request), sign, request)
    kind = request.data["counters"][counter]
    if kind == "month":
        return request.data["months"][int(digits) - 1]
    speller = NATIVE if kind in ("native", "hour") else SPELLER
    return f"{speller.cardinal(digits, Features(), request)} {counter}"


def speak_date(span: Span, context: SpanContext) -> str:
    """A date in the CLDR long date pattern of `ko`, with the month name of `months`."""
    request, fields = context.request, span.fields
    words = {"year": SPELLER.cardinal(str(fields["year"]), Features(), request),
             "month_name": request.data["months"][fields["month"] - 1],
             "day": SPELLER.cardinal(str(fields["day"]), Features(), request)}
    return "".join(literal if name == "text" else words[name] for name, literal in long_date("ko")[0])


LANGUAGE = LanguageSpec(
    code="ko",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("ko-KR"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], *map(Kept, SHAPES), KoCardinal(), RBNF_DECIMAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DECIMAL: speak_decimal,
                 Form.DATE: speak_date},
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.ORDINAL: ORDINAL},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={},
    not_applicable=frozenset(OPTIONS),
)
