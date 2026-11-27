"""Hindi: hi-IN.

Cardinals come from numtag. Its words follow the standard forms of Kendriya Hindi Nideshalaya, *Devanagari Lipi
tatha Hindi Vartani ka Manakikaran* (2016). Section 5.1, p. 52, lists the standard word of each number from one to a
hundred, as "इक्कीस" for 21 and "निन्यानवे" for 99. The same section, p. 53, names the scale words "हज़ार, लाख,
करोड़, अरब (सौ करोड़ नहीं)": 10^9 reads "अरब", not "सौ करोड़". The CLDR RBNF rule set `spellout-cardinal` of `hi`
(unicode-rbnf, `hi.xml`) writes 99 "निन्यानबे", which is not the standard form.

A number reads in Latin digits and in Devanagari digits (U+0966 to U+096F): the tokens read a digit by its Unicode
value. The group mark is the comma, in the Indian grouping of the CLDR pattern `#,##,##0.###`.

A minus sign reads "ऋण", the `-x: ऋण →→;` rule of the same rule set. A decimal reads its `x.x: ←← दशमलव →→;` rule:
the whole part, "दशमलव", then each digit of the decimal part, so `2.75` reads "दो दशमलव सात पाँच".

`digit_words` holds the words of 0 to 9 of the same rule set, "0: शून्य;" to "9: नौ;". An ordinal of an SSML say-as
reads the rule sets `spellout-ordinal-masculine` and `spellout-ordinal-feminine`, by gender, and a say-as date the
CLDR `long` date pattern, as with no file. Money, percentages, measures, numeric dates, fractions and ordinals in
plain text stay as written, as for a language with no file (design section 6.1).
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (CARDINAL, LEXICON, RBNF_DECIMAL, SHARED, OrdinalStop, Written,
                                          speak_cardinal, speak_cldr_date, speak_lexicon, speak_rbnf_decimal,
                                          written_shapes)
from text2spoken.core.spans import FIELDS, Features, Span
from text2spoken.core.spellers import NumtagSpeller, RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, Form, GrammaticalGender, freeze

M, F = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE

MARKS = [{"decimal": ".", "group": ",", "secondary_grouping": 2}]

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": MARKS, "Deva": MARKS},
    "sign_words": {"-": "ऋण"},
    "digit_words": ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"],
    "leads": {},
})

KEPT_FIELDS = freeze(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


class Kept(Written):
    """`Written` with cardinal spans: the language file contract (design section 5.2) asks that each span has the
    form of its recognizer."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in self.shape.find(text, tokens, request):
            yield replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)


RBNF = RbnfSpeller(cardinal={Features(): "spellout-cardinal"},
                   ordinal={Features(): "spellout-ordinal-masculine", Features(gender=M): "spellout-ordinal-masculine",
                            Features(gender=F): "spellout-ordinal-feminine"},
                   decimal="spellout-cardinal")

LANGUAGE = LanguageSpec(
    code="hi",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("hi-IN"),),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=True))),
                 CARDINAL, RBNF_DECIMAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DECIMAL: speak_rbnf_decimal,
                 Form.DATE: speak_cldr_date},
    spellers={Form.CARDINAL: NumtagSpeller({}), Form.DECIMAL: RBNF, Form.ORDINAL: RBNF},
    genders=frozenset({M, F}),
    default_gender=M,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={"default_gender": frozenset({"masculine", "feminine"})},
    not_applicable=frozenset(OPTIONS) - {"default_gender"},
)
