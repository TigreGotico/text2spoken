"""The errors and warnings of text2spoken."""
from __future__ import annotations


class Text2SpokenError(ValueError):
    """The base of every text2spoken error."""


class InvalidLanguageTagError(Text2SpokenError):
    """The tag does not parse as BCP 47."""


class TokenizerError(Text2SpokenError):
    """A token does not match the text, is out of order, or overlaps another."""


class InvalidHintError(Text2SpokenError):
    """Strict mode: a hint key with no span that starts at that offset."""


class UnsupportedParameterError(Text2SpokenError):
    """Strict mode: an option value that the language cannot produce."""


class InvalidLexiconError(Text2SpokenError):
    """A lexicon value in which a recognizer claims a span."""


class UndefinedGrammaticalGender(UnsupportedParameterError):
    """A gender, animacy, noun class or numeral system that the language does not define."""

    def __init__(self, lang: str, value: str, defined: frozenset[str]):
        self.lang = lang
        self.value = value
        self.defined = defined
        super().__init__(f"{lang!r} does not define {value!r}; it defines {sorted(defined)}")


class DeclinedReading(Text2SpokenError):
    """A speller cannot read this number, so the span stays as written (design section 10)."""


class UnreadFormError(Text2SpokenError):
    """Strict mode: a written form stays in the output."""

    def __init__(self, unread: tuple[str, ...], reason: str = ""):
        self.unread = unread
        super().__init__(f"unread: {list(unread)}" + (f" ({reason})" if reason else ""))


class Text2SpokenWarning(UserWarning):
    """The base of every text2spoken warning."""


class ParameterNotHonouredWarning(Text2SpokenWarning):
    """An option value that the language cannot produce; the language default applies."""


class HintWarning(Text2SpokenWarning):
    """A hint key with no span that starts at that offset."""
