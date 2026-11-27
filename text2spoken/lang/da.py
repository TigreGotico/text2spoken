"""Danish: da-DK.

Cardinals and decimals come from numtag. sproget.dk (Dansk Sprognævn and DSL), "Et eller flere ord", section
"Talord", gives the spacing: "Talord under 100 skrives i ét ord: halvtreds femogfirs", and "Talord over 100 skrives
i to eller flere ord: to hundred(e) fire tusind(e) (og) tre hundred(e) (og) treoghalvfems". sproget.dk, "Den 101.
dalmatiner", names "de to valgfrie bogstavskrevne former hundrede og hundred" of 100.

The file reads no noun, so 1 reads "en" before a noun of each gender. "en" is the form of counting: da.wikipedia,
"Betydende cifre": "1.001 (et tusinde og en)", "10,11 (ti komma en en)". sproget.dk, "Den 101. dalmatiner", gives
the two forms of 1: "én/ét".

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

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (CARDINAL, LEXICON, SHARED, OrdinalStop, Written, speak_cardinal,
                                          speak_cldr_date, speak_decimal, speak_lexicon, written_shapes)
from text2spoken.core.spans import FIELDS, Features, Span
from text2spoken.core.spellers import NumtagSpeller, RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.params import OPTIONS, Form, freeze

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "minus"},
    "digit_words": ["nul", "en", "to", "tre", "fire", "fem", "seks", "syv", "otte", "ni"],
    "leads": {},
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
ORDINAL = RbnfSpeller(cardinal={Features(): "spellout-cardinal-common"},
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
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DECIMAL: speak_decimal,
                 Form.DATE: speak_cldr_date},
    spellers={Form.CARDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.ORDINAL: ORDINAL},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={},
    not_applicable=frozenset(OPTIONS),
)
