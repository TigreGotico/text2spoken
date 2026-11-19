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
language with no file (design section 6.1). A say-as `date` reads in the CLDR 49 `long` date pattern of `ko`,
`y년 MMMM d일`, with the month names of the CLDR `ko` Gregorian calendar (`speak_cldr_date`).
"""
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (RBNF_CARDINAL, RBNF_DECIMAL, SHARED, OrdinalStop, signed, speak_cldr_date,
                                          speak_decimal, speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Recognizer, Span, SpanContext
from text2spoken.core.tokens import Token
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, Form, FrozenMap, freeze

SPELLER = RbnfSpeller(cardinal={Features(): "spellout-numbering"}, ordinal={Features(): "spellout-numbering"},
                      decimal="spellout-numbering")

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
    "sign_words": {"-": "마이너스"},
    "leads": {},
})

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


LANGUAGE = LanguageSpec(
    code="ko",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("ko-KR"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], *map(Kept, SHAPES), RBNF_CARDINAL, RBNF_DECIMAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DECIMAL: speak_decimal,
                 Form.DATE: speak_cldr_date},
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={},
    not_applicable=frozenset(OPTIONS),
)
