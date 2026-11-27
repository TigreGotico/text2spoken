"""Danish: da-DK.

Cardinals and decimals come from numtag. sproget.dk (Dansk Sprognævn and DSL), "Et eller flere ord", section
"Talord", gives the spacing: "Talord under 100 skrives i ét ord: halvtreds femogfirs", and "Talord over 100 skrives
i to eller flere ord: to hundred(e) fire tusind(e) (og) tre hundred(e) (og) treoghalvfems". sproget.dk, "Den 101.
dalmatiner", names "de to valgfrie bogstavskrevne former hundrede og hundred" of 100.

sproget.dk, "Den 101. dalmatiner", gives the two forms of 1: "én/ét". A number with no word after it ends in "en",
the form of counting: da.wikipedia, "Betydende cifre": "1.001 (et tusinde og en)", "10,11 (ti komma en en)". A
number before a word ends in "et", the neuter, through `noun_one`: the file reads no noun gender, so 1 before a
common-gender noun, as "1 bil", reads "et" too.

A decimal reads its decimals digit by digit after "komma", with the zeros at the end. da.wikipedia, "Betydende
cifre": "10,11 (ti komma en en)", "100,0 (Et hundrede komma nul)". The decimal mark is the comma and the group mark
is the full stop, as in "1.234 (et tusinde to hundrede og fire og tredive)" of that article.

`digit_words` holds the words of 0 to 9. The sources above give "nul", "en", "to", "tre", "fire", "fem" and
"syv"; "seks", "otte" and "ni" are the words of numtag. The sign word of the minus sign is "minus".

Money, percentages, measures, numeric dates, fractions and ordinals stay as written, as for a language with no file
(design section 6.1). A say-as ordinal and a say-as date read as in a language with no file: the ordinal through the
RBNF `da` rule set `spellout-ordinal-common`, with the corrections of `data/rbnf_corrections.json`, and the date by
the CLDR `long` pattern.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import replace

from text2spoken.errors import DeclinedReading
from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (CARDINAL, LEXICON, SHARED, OrdinalStop, Written, speak_cardinal,
                                          speak_cldr_date, speak_decimal, speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Span, SpanContext
from text2spoken.core.spellers import NumtagSpeller, RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, Form, freeze

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "minus"},
    "digit_words": ["nul", "en", "to", "tre", "fire", "fem", "seks", "syv", "otte", "ni"],
    "leads": {},
    "noun_one": {"en": "et"},
})

KEPT_FIELDS = freeze(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


class Kept(Written):
    """`Written` with cardinal spans: the language file contract (design section 5.2) asks that each span has the
    form of its recognizer."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in self.shape.find(text, tokens, request):
            yield replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=self.name, keep=True)


class DaSpeller(NumtagSpeller):
    """numtag, with the decimals digit by digit."""

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """numtag drops the zeros at the end of the decimals, which "Betydende cifre" says."""
        digits = " ".join(self.cardinal(digit, Features(), request) for digit in fraction)
        return f"{self.cardinal(integer or '0', features, request)} komma {digits}"


SPELLER = DaSpeller({})


def speak_da_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal whose last word changes by `noun_one` before a word."""
    words = speak_cardinal(span, context)
    if context.after and context.after[0][:1].isalpha():
        *head, last = words.split(" ")
        words = " ".join([*head, context.request.data["noun_one"].get(last, last)])
    return words
class DaOrdinalSpeller(RbnfSpeller):
    """CLDR gives the cardinal "tusinde" as the ordinal of 1000, so a span with that reading declines."""

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        words = super().ordinal(digits, features, request)
        if words == self.cardinal(digits, features, request):
            raise DeclinedReading(f"the CLDR da ordinal of {digits} is its cardinal")
        return words


ORDINAL = DaOrdinalSpeller(cardinal={Features(): "spellout-cardinal-common"},
                           ordinal={Features(): "spellout-ordinal-common"})

LANGUAGE = LanguageSpec(
    code="da",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("da-DK"),),
    data=DATA,
    recognizers=(LEXICON, *map(Kept, (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
                                       SHARED["fraction"], OrdinalStop(bare_stop=True))),
                 SHARED["decimal"], CARDINAL),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_da_cardinal, Form.DECIMAL: speak_decimal,
                 Form.DATE: speak_cldr_date},
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.ORDINAL: ORDINAL},
    writers=("numtag", "unicode-rbnf"),
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={},
    not_applicable=frozenset(OPTIONS),
)
