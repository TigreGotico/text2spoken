"""Bengali: bn-BD, the default variety, and bn-IN.

Cardinals come from numtag. Its words agree with the English Wiktionary, "Appendix:Bengali numerals" (oldid
95460450): "২১ একুশ", "৩৪ চৌত্রিশ", "৬৭ সাতষট্টি", "১,০০০ হাজার", "১,০০,০০০ লাখ", "১,০০,০০,০০০ কোটি".
Hanne-Ruth Thompson, *Bengali* (2012), Appendices, p. 373 to 374, gives the same numbers in Roman letters, with the
hundred and the thousand after a number word: "100 ek so", "200 du so", "1000 ek hajar", "100.000 ek lakh". numtag
writes the hundred apart, as Thompson does: 100 reads "এক শ". Wiktionary also writes "একশ" in one word.

`digit_words` holds the Wiktionary words of 0 to 9, "শূন্য" to "নয়".

A number reads in Latin digits and in Bengali digits (U+09E6 to U+09EF): the tokens read a digit by its Unicode
value. The group mark is the comma, in the Indian grouping of Wiktionary, "১,০০,০০০".

A numeral classifier joins the number, with no space, as in `3টি`: Thompson 2012, section 5.2.4, p. 53: "Classifiers
are attachments. They never occur alone", "singular: ta, ti, khana, khani", and the animate classifier jon. Section
5.2.5, pp. 54 to 56, joins each to numbers: "carta Sari four sarees, hajarta prosn6é a thousand questions, pécista
narikel gach twenty-five coconut trees" (ta), "tinti boi three books, pacti caméc five spoons" (ti), "tinjon nay6k three
actors, dosjan chatr6 ten students", "duijan montri two ministers" (jon), "tar duikhani hat both her hands", "khata
carkhana the four notebooks" (khana, khani). The Bangla Academy, *Adhunik Bangla Abhidhan* (2016), gives the Bengali
script: টি "সংখ্যানির্দেশক বাংলা প্রত্যয় (দুটি পাখি)", জন "ব্যক্তির সংখ্যা নির্দেশ করে এমন (পাঁচজন)". A number with a
word of `classifiers` after it reads the cardinal and the classifier as one word: `3টি` reads তিনটি.

Two joins with দুই are one word of their own, and the table of each classifier gives it. The Bangla Academy headwords
দুটা "দুই সংখ্যক" and দুটি "দুটা'র আদরার্থক রূপ"; Thompson writes "duti" and "duto". `harmony_classifiers` holds the
two allomorphs of ta, which Thompson, section 5.2.5.1, p. 54, gives only with some numbers: "ta has two allomorphs to
and te which are used, mainly in West Bengal, for vowel harmony. duto two, tinte three, carte four". The Bangla
Academy headwords দুটো "দুটা'-র কথ্য রূপ" and চারটে "চারটা'-র কথ্য রূপ", and তিনটে under তিনটা, give their script.
টো and টে after another number stay as written. গুলো and গুলি stay as written after a number: Thompson, section
5.2.5.5, p. 57, adds them "to nouns, possessive and deictic pronouns, quantifiers and other adjectives, but never to
numbers". A cardinal of two or more words, as এক শ, and a classifier with a case ending after it, as `3টিতে`, stay
as written, because no source gives the joined form.

numtag reads no Bengali decimal and no minus sign, and the file adds no word that no source gives, so `3.5` and `-5`
stay as written. Money, percentages, measures, numeric dates, fractions and ordinals stay as written, as for a
language with no file (design section 6.1).
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.core.language import LanguageSpec, Request, Variety, drop_affixes
from text2spoken.core.recognizers import (LEXICON, SHARED, Cardinal, OrdinalStop, Written, speak_cardinal,
                                          speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Span, SpanContext
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
    "classifiers": {"টি": {"2": "দুটি"}, "টা": {"2": "দুটা"}, "জন": {}, "খানা": {}, "খানি": {}},
    "harmony_classifiers": {"টো": {"2": "দুটো"}, "টে": {"3": "তিনটে", "4": "চারটে"}},
    "case_suffixes": ["টি", "টা", "জন", "খানা", "খানি", "টো", "টে"],
})

KEPT_FIELDS = freeze(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


class Kept(Written):
    """`Written` with cardinal spans: the language file contract (design section 5.2) asks that each span has the
    form of its recognizer."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in self.shape.find(text, tokens, request):
            yield replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)


class BnCardinal(Cardinal):
    """The core cardinal, with a numeral classifier joined after it. A classifier with no form for the number
    keeps the number as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            suffix = span.fields["suffix"]
            if suffix and classified(span.fields["digits"], suffix, request) is None:
                yield replace(span, keep=True)
            else:
                yield span


def classified(digits: str, classifier: str, request: Request) -> str | None:
    """The number and the classifier as one word, or None when no source gives the form."""
    data = request.data
    if classifier in data["harmony_classifiers"]:
        return data["harmony_classifiers"][classifier].get(digits)
    if classifier not in data["classifiers"]:
        return None
    joined = data["classifiers"][classifier].get(digits)
    if joined:
        return joined
    words = request.language.spellers[Form.CARDINAL].cardinal(digits, Features(), request)
    return None if " " in words else words + classifier


def speak_classified(span: Span, context: SpanContext) -> str:
    suffix = span.fields["suffix"]
    return classified(span.fields["digits"], suffix, context.request) if suffix else speak_cardinal(span, context)


LANGUAGE = LanguageSpec(
    code="bn",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("bn-BD"), Variety("bn-IN")),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=True))),
                 BnCardinal()),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_classified},
    spellers={Form.CARDINAL: NumtagSpeller({})},
    writers=("numtag",),
    attach=drop_affixes,
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
