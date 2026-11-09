"""A stub language under the private-use code `qac`, which the row tests of every language file also run on.

It reads cardinals digit by digit from the `digit_words` table of its data, so dropping an entry of any of its
tables changes a row of `qac.tsv`. Its words are invented, and each expected value of `qac.tsv` comes from the
tables of this file.
"""
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import SHARED, speak_cardinal, speak_lexicon
from text2spoken.core.spellers import DigitSpeller
from text2spoken.params import OPTIONS, Form, freeze

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}]},
    "digit_words": ["ze", "wa", "tu", "ri", "fo", "fa", "si", "se", "ei", "ni"],
    "sign_words": {"-": "minu"},
    "leads": {"#": "numo"},
    "symbols": {},
})


class TableSpeller:
    """One word per digit, read from the data of the request, so a mutation of the table reaches the output."""

    def cardinal(self, digits, features, request):
        return DigitSpeller(request.data["digit_words"]).cardinal(digits, features, request)

    def ordinal(self, digits, features, request):
        raise NotImplementedError

    year = decimal = fraction = ordinal


LANGUAGE = LanguageSpec(
    code="qac", serves=(), cldr_aliases=(), varieties=(Variety("qac"),), data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: TableSpeller()}, genders=frozenset(), default_gender=None, animacies=frozenset(),
    noun_classes=frozenset(), numeral_systems=frozenset(), context_words=True, options={},
    not_applicable=frozenset(OPTIONS),
)
