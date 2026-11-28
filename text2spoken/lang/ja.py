"""Japanese: ja-JP.

The file reads what the core reads for a language with no file (design section 6.1), and it reads the decimal mark
as 点.

The number words come from the CLDR RBNF rule set `spellout-cardinal` of `ja` (unicode-rbnf 2.5.0, `ja.xml`): "0:
〇;", "1: 一;", "100: 百[→→];", "1000: 千[→→];", "10000: ←←万[→→];", and the minus rule "-x: マイナス→→;". The decimal
and group marks are the full stop and the comma, the CLDR number symbols of `ja`.

The decimal mark reads 点. The English Wiktionary, "小数点", Japanese, Usage notes: "A decimal point itself is
pronounced as てん (ten, literally “dot”). For example, 9.58 is pronounced as きゅうてんごーはち (kyū ten gō hachi,
literally “nine point five eight”) and 19.19 is pronounced as じゅうきゅうてんいちきゅう (jū-kyū ten ichi kyū,
literally “ten-nine point one nine”)." Its Etymology: "From 小数(しょうすう) (shōsū, “decimal”) + 点(てん) (ten, “point,
dot”)." The CLDR rule set `spellout-cardinal-financial` of `ja` writes the same word, "x.x: ←←点→→→;". The rule set
`spellout-cardinal` writes the mark as ・ ("x.x: ←←・→→→;"), a sign with no reading, so the speller writes 点 in its
place. The digits after the mark read one by one, as the rule `→→→` writes them: 3.14 reads 三点一四.

A number next to a kanji or a kana, as in 3個, 2024年 and 3.5キロ, stays as written, as for a language with no file.
The Japanese phonemizer of the speech stack, pyopenjtalk-plus (0.4.1.post10), reads such a number with the sound of
its counter (3本 サンボン, 1杯 イッパイ). In kanji numerals it reads some numbers as other words: 八百 as ヤオ, 九十九 as
ツクモ and 千歳 as チトセ.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (LEXICON, RBNF_CARDINAL, RBNF_DECIMAL, SHARED, OrdinalStop, Written,
                                          speak_cldr_date, speak_lexicon, speak_rbnf_cardinal, speak_rbnf_decimal,
                                          written_shapes)
from text2spoken.core.spans import FIELDS, Features, Span
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, Form, freeze

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
    "sign_words": {"-": "マイナス"},
    "leads": {},
})


class JaSpeller(RbnfSpeller):
    """`spellout-cardinal` of `ja`, with 点 for the mark ・ of its `x.x` rule."""

    def _decimal(self, integer: str, fraction: str, request: Request, sign: int) -> str:
        return super()._decimal(integer, fraction, request, sign).replace("・", "点")


SPELLER = JaSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"},
                    decimal="spellout-cardinal")

KEPT_FIELDS = freeze(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


class Kept(Written):
    """`Written` with cardinal spans: the language file contract (design section 5.2) asks that each span has the
    form of its recognizer."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in self.shape.find(text, tokens, request):
            yield replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)


# `ja` has the RBNF rule set `digits-ordinal`, so a number with a full stop after it is no ordinal.
LANGUAGE = LanguageSpec(
    code="ja",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("ja-JP"),),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=False))),
                 RBNF_CARDINAL, RBNF_DECIMAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_rbnf_cardinal, Form.DECIMAL: speak_rbnf_decimal,
                 Form.DATE: speak_cldr_date},
    writers=("unicode-rbnf",),
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.ORDINAL: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
