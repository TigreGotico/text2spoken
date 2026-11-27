"""Kabyle: kab-DZ.

Cardinals come from numtag. Its words agree with the French Wiktionary, "Modèle:cardinaux/kab" (oldid 39522335):
"1 yiwen", "2 sin", "7 sebɛa", "10 ɛecṛa", "21 waḥed u ɛecrin", "99 tesɛa u tesɛin", "100 mya", "200 mitin",
"900 tesɛa-mya", "1 000 alef", "2 000 juǧ alaf", "3 000 telt-alaf", "amelyun". The English Wikipedia, "Kabyle
grammar" (oldid 1383353682), section Numerotation: "Only the first two numbers are Berber; for higher numbers,
Arabic is used. They are yiwen (f. yiwet) "one", sin (f. snat) "two"."

The file reads no noun, so 1 and 2 read in the masculine, "yiwen" and "sin", before a noun of each gender.

`digit_words` holds the Wiktionary words of 0 to 9, "ilem" to "tesɛa". The group mark is the no-break space of
CLDR `kab`.

numtag reads no Kabyle decimal and no minus sign, and the file adds no word that no source gives, so `3,5` and `-5`
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

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ",", "group": " "}]},
    "sign_words": {},
    "digit_words": ["ilem", "yiwen", "sin", "tlata", "ṛebɛa", "xemsa", "setta", "sebɛa", "tmanya", "tesɛa"],
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
    code="kab",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("kab-DZ"),),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=True))),
                 CARDINAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: NumtagSpeller({})},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
