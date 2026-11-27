"""Bengali: bn-BD, the default variety, and bn-IN.

Cardinals come from numtag. Its words agree with the English Wiktionary, "Appendix:Bengali numerals" (oldid
95460450): "২১ একুশ", "৩৪ চৌত্রিশ", "৬৭ সাতষট্টি", "১,০০০ হাজার", "১,০০,০০০ লাখ", "১,০০,০০,০০০ কোটি".
Hanne-Ruth Thompson, *Bengali* (2012), Appendices, p. 373 to 374, gives the same numbers in Roman letters, with the
hundred and the thousand after a number word: "100 ek so", "200 du so", "1000 ek hajar", "100.000 ek lakh". numtag
writes the hundred apart, as Thompson does: 100 reads "এক শ". Wiktionary also writes "একশ" in one word.

`digit_words` holds the Wiktionary words of 0 to 9, "শূন্য" to "নয়".

A number reads in Latin digits and in Bengali digits (U+09E6 to U+09EF): the tokens read a digit by its Unicode
value. The group mark is the comma, in the Indian grouping of Wiktionary, "১,০০,০০০".

numtag reads no Bengali decimal and no minus sign, and the file adds no word that no source gives, so `3.5` and `-5`
stay as written. Money, percentages, measures, numeric dates, fractions and ordinals stay as written, as for a
language with no file (design section 6.1).
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (CARDINAL, LEXICON, SHARED, OrdinalStop, Written, speak_cardinal,
                                          speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Span
from text2spoken.core.spellers import NumtagSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, Form, freeze

MARKS = [{"decimal": ".", "group": ",", "secondary_grouping": 2}]

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": MARKS, "Beng": MARKS},
    "sign_words": {},
    "digit_words": ["শূন্য", "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়"],
    "leads": {},
})

KEPT_FIELDS = freeze(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


class Kept(Written):
    """`Written` with cardinal spans: the language file contract (design section 5.2) asks that each span has the
    form of its recognizer."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in self.shape.find(text, tokens, request):
            yield replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)


LANGUAGE = LanguageSpec(
    code="bn",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("bn-BD"), Variety("bn-IN")),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=True))),
                 CARDINAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: NumtagSpeller({})},
    writers=("numtag",),
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
