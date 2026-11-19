"""Korean: ko-KR.

The number words come from the CLDR RBNF rule sets of `ko` (`common/rbnf/ko.xml`, as unicode-rbnf ships it). A
number reads through `spellout-numbering`, whose rule "1: =%spellout-cardinal-sinokorean=;" reads every number from
1 up in the Sino-Korean numerals, as `123456789` reads 일억 이천삼백사십오만 육천칠백팔십구, and whose rule "0: 공;"
reads zero. A decimal reads through the rule "x.x: ←←점→→→;" of the same rule set: `3.5` reads 삼점오. The decimal
mark `.` and the group mark `,` come from the CLDR 49 number symbols of `ko`.

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
from text2spoken.core.recognizers import (RBNF_CARDINAL, RBNF_DECIMAL, SHARED, OrdinalStop, signed, speak_decimal,
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
    "months": ["일월", "이월", "삼월", "사월", "오월", "유월", "칠월", "팔월", "구월", "시월", "십일월", "십이월"],
})


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
    """A cardinal after the word of its sign. Minus zero declines: the `-x` rule reads no sign for zero."""
    request, digits, sign = context.request, span.fields["digits"], span.fields["sign"]
    if sign and not digits.strip("0"):
        raise DeclinedReading("minus zero has no sign word")
    return signed(SPELLER.cardinal(digits, Features(), request), sign, request)


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
    recognizers=(SHARED["lexicon"], *map(Kept, SHAPES), RBNF_CARDINAL, RBNF_DECIMAL),
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
