"""`analyze` and `normalize`: the pipeline from text to the spans of a call and to the spoken text."""
from __future__ import annotations

from text2spoken.core.language import resolve
from text2spoken.core.numbers import declared_marks
from text2spoken.core.spans import Analysis, classify, render
from text2spoken.core.tokens import Tokenizer, check_tokens, default_tokenizer, join_split_words, protect_blocks
from text2spoken.errors import ArgumentTypeError, require_type
from text2spoken.params import NormalizationParams


def analyze(text: str, lang: str, params: NormalizationParams | None = None,
            tokenizer: Tokenizer | None = None) -> Analysis:
    require_type(text, "text", str)
    require_type(lang, "lang", str)
    if params is not None:
        require_type(params, "params", NormalizationParams)
    if tokenizer is not None and not callable(tokenizer):
        raise ArgumentTypeError(f"tokenizer must be callable, not {type(tokenizer).__name__}")
    request = resolve(lang, params or NormalizationParams())
    raw = (tokenizer or default_tokenizer)(text, request.tag)
    tokens = join_split_words(check_tokens(raw, text), text, declared_marks(request.data))
    blocks = protect_blocks(text)
    return Analysis(text=text, blocks=blocks, tokens=tokens, spans=classify(text, tokens, blocks, request),
                    request=request)


def normalize(text: str, lang: str, params: NormalizationParams | None = None,
              tokenizer: Tokenizer | None = None) -> str:
    return render(analyze(text, lang, params, tokenizer))
