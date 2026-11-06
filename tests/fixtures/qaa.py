"""A gendered test language under the private-use code `qaa`, for the core rules that English cannot show.

Its words are a table of this file, so a test reads its expected value here and not from the core.
"""
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import SHARED, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.params import Form, FrozenMap, GrammaticalGender, freeze

WORDS = {"1": {"masculine": "um", "feminine": "uma"}, "2": {"masculine": "dois", "feminine": "duas"}}
NOUN_GENDER = {"casa": GrammaticalGender.FEMININE, "casas": GrammaticalGender.FEMININE}


class TableSpeller:
    def cardinal(self, digits, features, request):
        return WORDS[digits][features.gender]

    def ordinal(self, digits, features, request):
        raise NotImplementedError

    year = decimal = fraction = ordinal


SPELLER = TableSpeller()


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """The agreement order of design section 5.6: the hint, the noun after the number, the params, the file."""
    if context.hint is not None and context.hint.gender is not None:
        gender = context.hint.gender
    else:
        noun = NOUN_GENDER.get(context.after[0]) if context.after else None
        gender = noun or context.request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender
    return SPELLER.cardinal(span.fields["digits"], Features(gender=gender), context.request)


LANGUAGE = LanguageSpec(
    code="qaa", serves=("qab",), cldr_aliases=("pt",), varieties=(Variety("qaa"),),
    data=freeze({"defaults": {}}), recognizers=(SHARED["lexicon"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER},
    genders=frozenset({GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE}),
    default_gender=GrammaticalGender.MASCULINE, animacies=frozenset(), noun_classes=frozenset(),
    numeral_systems=frozenset(), context_words=True, options={"default_gender": frozenset({"masculine", "feminine"})},
    not_applicable=frozenset({"date_order", "clock", "minute_style", "decimal_mark", "scale", "register",
                              "phone_regions"}),
)
