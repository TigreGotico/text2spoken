"""`distributions(lang)` and `revision(lang)`: the distributions on the output path of `normalize` for a language, and
their installed versions (design section 12.1)."""
from __future__ import annotations

import importlib.metadata

from text2spoken.core import parsers
from text2spoken.core.language import select
from text2spoken.errors import require_type

FORMAT = "t2s2"
"""The prefix of a revision. It changes when the encoding of the revision changes."""

CORE = ("text2spoken", "linguatag", "quebra-frases", "unicode-rbnf")
"""The distributions on the output path of every language: the library, the tag rules, the default tokenizer and the
CLDR plural rules."""


def distributions(lang: str) -> tuple[str, ...]:
    """The distribution names on the output path of `normalize(text, lang)`, with `text2spoken` first. A writer that
    is not installed, as `tugalex` without the `pt` extra, is not in the tuple."""
    require_type(lang, "lang", str)
    tag, language, _ = select(lang)
    names = [parsers.date_distribution(tag) if name == parsers.DATES else name for name in language.writers]
    return tuple(name for name in dict.fromkeys((*CORE, *names)) if _installed(name))


def revision(lang: str) -> str:
    """`"t2s2:"` and the `name==version` of each of `distributions(lang)`, joined with `;`. A caller that keeps
    spoken text keeps the revision with it; a different revision tells which distribution to install."""
    return f"{FORMAT}:" + ";".join(f"{name}=={importlib.metadata.version(name)}" for name in distributions(lang))


def _installed(name: str) -> bool:
    try:
        importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return False
    return True
