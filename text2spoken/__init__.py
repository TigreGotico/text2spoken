"""text2spoken rewrites written forms into the words a speaker says.

`normalize(text, lang, params)` is the one API for a caller. `analyze` and `render` serve a frontend with
tokenizer context, `supports` tells what a language reads, and `effective_params` gives the params that apply.
"""
from text2spoken.core.language import Support, effective_params, supports
from text2spoken.core.pipeline import analyze, normalize
from text2spoken.core.spans import Analysis, Features, Span, render
from text2spoken.core.tokens import Token, Tokenizer, default_tokenizer
from text2spoken.errors import (DeclinedReading, HintWarning, InvalidHintError, InvalidLanguageTagError,
                                InvalidLexiconError, ParameterNotHonouredWarning, Text2SpokenError, Text2SpokenWarning,
                                TokenizerError, UndefinedGrammaticalGender, UnreadFormError, UnsupportedParameterError)
from text2spoken.params import Animacy, Form, FrozenMap, GrammaticalGender, NormalizationParams

__all__ = [
    "normalize", "analyze", "render", "supports", "effective_params",
    "Form", "GrammaticalGender", "Animacy", "NormalizationParams", "FrozenMap", "Features", "Span", "Analysis",
    "Support", "Token", "Tokenizer", "default_tokenizer",
    "Text2SpokenError", "InvalidLanguageTagError", "TokenizerError", "InvalidHintError", "UnsupportedParameterError",
    "InvalidLexiconError", "UndefinedGrammaticalGender", "UnreadFormError", "DeclinedReading", "Text2SpokenWarning",
    "ParameterNotHonouredWarning", "HintWarning",
]

