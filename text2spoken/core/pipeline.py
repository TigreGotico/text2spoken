"""`analyze` and `normalize`: the pipeline from text to the spans of a call and to the spoken text."""
from __future__ import annotations

import unicodedata
from dataclasses import replace

from text2spoken.core.emoji import emoji_view
from text2spoken.core.language import resolve
from text2spoken.core.numbers import declared_marks
from text2spoken.core.say_as import SayAs
from text2spoken.core.spans import LOG, Analysis, classify, render
from text2spoken.core.tokens import (Tokenizer, check_tokens, cut_tokens, default_tokenizer, join_split_words,
                                     protect_blocks)
from text2spoken.errors import ArgumentTypeError, UnreadFormError, require_type
from text2spoken.params import SCRIPT_NAMES, FrozenMap, NormalizationParams


def analyze(text: str, lang: str, params: NormalizationParams | None = None,
            tokenizer: Tokenizer | None = None, *, say_as: SayAs | None = None) -> Analysis:
    """The spans of the text. With `say_as`, the form that it names reads first (design section 17). When no span of
    that form reads, the call gives the analysis with no say-as, and logs a warning, or raises `UnreadFormError`
    in strict mode."""
    require_type(text, "text", str)
    require_type(lang, "lang", str)
    if params is not None:
        require_type(params, "params", NormalizationParams)
    if tokenizer is not None and not callable(tokenizer):
        raise ArgumentTypeError(f"tokenizer must be callable, not {type(tokenizer).__name__}")
    if say_as is not None:
        require_type(say_as, "say_as", SayAs)
    request = resolve(lang, params or NormalizationParams(), say_as)
    raw = (tokenizer or default_tokenizer)(text, request.tag)
    joined = join_split_words(check_tokens(raw, text), text, declared_marks(request.data))
    tokens = cut_tokens(joined, emoji_view(text, request.memo))
    blocks = protect_blocks(text)
    spans = classify(text, tokens, blocks, request)
    if request.say_as is not None and not request.say_as.read_in(spans, request):
        reason = f"the say-as {request.say_as.value!r} finds no reading in {text!r} for {request.tag}"
        if request.params.strict:
            raise UnreadFormError((text,), reason)
        LOG.warning("%s; the text reads as if no say-as were given", reason)
        return analyze(text, lang, params, tokenizer)
    return Analysis(text=text, blocks=blocks, tokens=tokens, spans=spans, request=request)


def normalize(text: str, lang: str, params: NormalizationParams | None = None,
              tokenizer: Tokenizer | None = None, *, say_as: SayAs | None = None) -> str:
    """The spoken text. With `params.script_languages`, each run of a mapped script reads in its language, and the
    rest reads in `lang`."""
    if not isinstance(params, NormalizationParams) or not params.script_languages:
        return render(analyze(text, lang, params, tokenizer, say_as=say_as))
    plain = replace(params, script_languages=FrozenMap())
    return "".join(render(analyze(run, params.script_languages.get(script, lang), plain, tokenizer, say_as=say_as))
                   for script, run in script_runs(text))


def _script(char: str) -> str | None:
    """The script of a letter in the table, else None: an ordinal indicator, a micro sign or a length mark joins the
    runs around it as a digit does."""
    return SCRIPT_NAMES.get(unicodedata.name(char, "").split(" ", 1)[0]) if char.isalpha() else None


def script_runs(text: str) -> list[tuple[str | None, str]]:
    """The text cut where the script of its letters changes. A combining mark stays with the letter before it. A
    stretch with no letter of the table, such as a number and its spaces, joins the run of the next letter, as a
    number comes before the noun that it counts ("25 كتاب", "1999 people"). At the end of the text it joins the run
    before it."""
    runs: list[list] = []
    pending = ""
    for char in text:
        script = _script(char)
        if script is None and not pending and runs and unicodedata.category(char).startswith("M"):
            runs[-1][1] += char
        elif script is None:
            pending += char
        elif runs and runs[-1][0] == script:
            runs[-1][1] += pending + char
            pending = ""
        else:
            runs.append([script, pending + char])
            pending = ""
    if pending:
        if runs:
            runs[-1][1] += pending
        else:
            runs.append([None, pending])
    return [(script, run) for script, run in runs]
