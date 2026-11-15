"""Portuguese with the e-mail and web address tables of `text2spoken/lang/_pt_electronic.py` and no other form.

The rows of `tests/data/electronic/pt.tsv` run on this language, so they test the address reading of pt-PT and
pt-BR apart from the other forms of `pt.py`. The digit words are those of the `digit_words` table of `pt.py`.
"""
from text2spoken.core.electronic import ELECTRONIC, speak_electronic
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import SHARED, speak_lexicon
from text2spoken.lang import _pt_electronic
from text2spoken.params import OPTIONS, Form, freeze

DATA = freeze({
    **_pt_electronic.ELECTRONIC,
    "digit_words": ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"],
})

LANGUAGE = LanguageSpec(
    code="pt", serves=(), cldr_aliases=(),
    varieties=tuple(Variety(tag, freeze(data)) for tag, data in _pt_electronic.VARIETIES.items()), data=DATA,
    recognizers=(SHARED["lexicon"], ELECTRONIC),
    verbalizers={Form.LEXICON: speak_lexicon, Form.ELECTRONIC: speak_electronic},
    spellers={}, genders=frozenset(), default_gender=None, animacies=frozenset(), noun_classes=frozenset(),
    numeral_systems=frozenset(), context_words=True, options={}, not_applicable=frozenset(OPTIONS),
)
