"""LanguageSpec, Variety, Request, the loader and CLDR locale mapping (design sections 5.2, 5.3, 6)."""
from __future__ import annotations

import re
import warnings
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field, replace
from decimal import Decimal
from functools import cache, lru_cache
from importlib import import_module
from importlib.resources import files
from typing import TYPE_CHECKING

from text2spoken.errors import (InvalidLanguageTagError, InvalidLexiconError, ParameterNotHonouredWarning,
                                UndefinedGrammaticalGender, UnsupportedParameterError, require_type)
from text2spoken.params import OPTIONS, Animacy, FrozenMap, Form, GrammaticalGender, NormalizationParams

if TYPE_CHECKING:
    from text2spoken.core.spans import Recognizer, Span, Verbalizer
    from text2spoken.core.spellers import NumberSpeller


def concatenate(spoken: str, prefix: str, suffix: str) -> str:
    """The core attachment: the prefix joins the first spoken word and the suffix joins the last."""
    return prefix + spoken + suffix


def infix_range(span: Span, following: Span, range_word: str) -> tuple[Span, Span]:
    """The core range join: the first span takes the mark between the two spans and a trail of the range word,
    so the range word stands between the two readings. With no range word, the pair stays as written."""
    if not range_word:
        return span, following
    return replace(span, end=following.start, trail=f" {range_word} "), following


@dataclass(frozen=True)
class Variety:
    tag: str
    data: FrozenMap = field(default_factory=FrozenMap)


@dataclass(frozen=True, eq=False, kw_only=True)
class LanguageSpec:
    code: str
    serves: tuple[str, ...]
    cldr_aliases: tuple[str, ...]
    varieties: tuple[Variety, ...]
    data: FrozenMap
    recognizers: tuple[Recognizer, ...]
    verbalizers: Mapping[Form, Verbalizer]
    spellers: Mapping[Form, NumberSpeller]
    genders: frozenset[GrammaticalGender]
    default_gender: GrammaticalGender | None
    animacies: frozenset[Animacy]
    noun_classes: frozenset[str]
    numeral_systems: frozenset[str]
    context_words: bool
    options: Mapping[str, frozenset[str]]
    not_applicable: frozenset[str]
    attach: Callable[[str, str, str], str] = concatenate
    join_range: Callable[[Span, Span, str], tuple[Span, Span]] = infix_range


def _merge(base, override):
    if isinstance(base, Mapping) and isinstance(override, Mapping):
        merged = dict(base)
        for key, value in override.items():
            merged[key] = _merge(base[key], value) if key in base else value
        return FrozenMap(merged)
    return override


@lru_cache(maxsize=128)
def merged_data(language_data: FrozenMap, variety_data: FrozenMap) -> FrozenMap:
    """The language data with the variety data merged in, key by key at every depth."""
    return _merge(language_data, variety_data)


@dataclass(frozen=True, eq=False)
class Request:
    tag: str
    variety: Variety
    language: LanguageSpec
    params: NormalizationParams
    memo: dict = field(default_factory=dict, repr=False)
    """Results computed for one call, such as the numbers of a text; a request lives for one call."""

    @property
    def data(self) -> FrozenMap:
        return merged_data(self.language.data, self.variety.data)


@dataclass(frozen=True, kw_only=True)
class Support:
    tag: str
    code: str
    forms: frozenset[Form]
    genders: frozenset[GrammaticalGender]
    animacies: frozenset[Animacy]
    noun_classes: frozenset[str]
    numeral_systems: frozenset[str]
    options: FrozenMap
    not_applicable: frozenset[str]
    context_words: bool


_LANGUAGE = "(?:[a-z][a-z][a-z]?(?:-[a-z][a-z][a-z]){0,3}|[a-z][a-z][a-z][a-z][a-z]?[a-z]?[a-z]?[a-z]?)"
_TAG = re.compile(
    _LANGUAGE
    + "(?:-[a-z][a-z][a-z][a-z])?"
    + "(?:-(?:[a-z][a-z]|[0-9][0-9][0-9]))?"
    + "(?:-(?:[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]?[a-z0-9]?[a-z0-9]?|[0-9][a-z0-9][a-z0-9][a-z0-9]))*"
    + "(?:-[0-9a-wy-z](?:-[a-z0-9][a-z0-9][a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?)+)*"
    + "(?:-x(?:-[a-z0-9][a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?[a-z0-9]?)+)?"
)
"""RFC 5646 `langtag`, lower case. The check belongs in linguatag; it leaves when the linguatag floor has it."""


def check_tag(tag: str) -> str:
    """The standardized tag, or InvalidLanguageTagError when the tag does not parse as BCP 47."""
    import linguatag

    if not isinstance(tag, str) or not _TAG.fullmatch(tag.replace("_", "-").lower()):
        raise InvalidLanguageTagError(f"not a BCP 47 language tag: {tag!r}")
    return linguatag.standardize_lang(tag)


def primary_subtag(tag: str) -> str:
    return tag.split("-")[0].lower()


@cache
def _registry() -> dict[str, LanguageSpec]:
    """Every language file in `text2spoken.lang`, by its code and by each code it serves."""
    index: dict[str, LanguageSpec] = {}
    names = sorted(entry.name[:-3] for entry in files("text2spoken.lang").iterdir()
                   if entry.name.endswith(".py") and not entry.name.startswith("_"))
    for name in names:
        spec = import_module(f"text2spoken.lang.{name}").LANGUAGE
        for code in (spec.code, *spec.serves):
            if code in index:
                raise RuntimeError(f"two language files read {code!r}: {index[code].code} and {spec.code}")
            index[code] = spec
    return index


def language_file(code: str) -> LanguageSpec | None:
    """The language file whose code is `code` or whose `serves` lists it."""
    return _registry().get(code)


@cache
def rbnf_locales() -> frozenset[str]:
    from unicode_rbnf import RbnfEngine

    return frozenset(RbnfEngine.get_supported_languages())


@cache
def plural_locales() -> frozenset[str]:
    """The locales with CLDR plural rules. `_load` is the one place in unicode_rbnf that holds the list."""
    from unicode_rbnf.plural_rules import PluralType, _load

    return frozenset(_load(PluralType.CARDINAL))


def subtags(tag: str) -> tuple[str, str | None, str | None]:
    """The language, script and region subtags of a standardized tag."""
    parts = tag.split("-")
    rest = parts[1:parts.index("x")] if "x" in parts else parts[1:]
    script = next((s.title() for s in rest[:1] if len(s) == 4 and s.isalpha()), None)
    at = 1 if script else 0
    region = next((s.upper() for s in rest[at:at + 1]
                   if (len(s) == 2 and s.isalpha()) or (len(s) == 3 and s.isdigit())), None)
    return parts[0].lower(), script, region


def cldr_locale(tag: str, available: Collection[str], language: LanguageSpec) -> str | None:
    """The first CLDR locale id that `available` holds: from the tag, then the file code, then its aliases."""
    lang, script, region = subtags(tag)
    candidates = []
    if script and region:
        candidates.append(f"{lang}_{script}_{region}")
    if script:
        candidates.append(f"{lang}_{script}")
    if region:
        candidates.append(f"{lang}_{region}")
    candidates += [lang, language.code, *language.cldr_aliases]
    return next((c for c in candidates if c in available), None)


def plural_category(request: Request, written: str) -> str:
    """The CLDR plural category of a written ASCII number, such as `1.0` or `5`, in the variety of the request."""
    from unicode_rbnf.plural_rules import get_plural_category

    locale = cldr_locale(request.tag, plural_locales(), request.language)
    if locale is None:
        raise LookupError(f"no CLDR plural rules for {request.tag!r}")
    return str(get_plural_category(locale, Decimal(written)))


@cache
def core_language(code: str) -> LanguageSpec:
    """The language of a code with no file: cardinals through RBNF where RBNF has the locale (section 6.1)."""
    from text2spoken.core import recognizers
    from text2spoken.core.spans import Features
    from text2spoken.core.spellers import RbnfSpeller, rbnf_engine
    import linguatag

    tag = linguatag.with_default_region(code)
    bare = LanguageSpec(code=code, serves=(), cldr_aliases=(), varieties=(Variety(tag),), data=FrozenMap(),
                        recognizers=(recognizers.LEXICON,), verbalizers={Form.LEXICON: recognizers.speak_lexicon},
                        spellers={}, genders=frozenset(), default_gender=None, animacies=frozenset(),
                        noun_classes=frozenset(), numeral_systems=frozenset(), context_words=True, options={},
                        not_applicable=frozenset(OPTIONS))
    locale = cldr_locale(tag, rbnf_locales(), bare)
    if locale is None:
        return bare
    names = rbnf_engine(locale).rulesets
    cardinal = next(n for n in ("spellout-cardinal", "spellout-cardinal-masculine", "spellout-numbering") if n in names)
    ordinal = next((n for n in ("spellout-ordinal", "spellout-ordinal-masculine") if n in names), cardinal)
    speller = RbnfSpeller(cardinal={Features(): cardinal}, ordinal={Features(): ordinal})
    own_ordinal = any("digits-ordinal" in rbnf_engine(name).rulesets
                      for name in (locale, locale.split("_")[0]) if name in rbnf_locales())
    shapes = (recognizers.SHARED["money"], recognizers.SHARED["percent"], recognizers.SHARED["measure"],
              recognizers.SHARED["date_numeric"], recognizers.OrdinalStop(bare_stop=not own_ordinal))
    return replace(bare, data=recognizers.written_shapes(),
                   recognizers=(recognizers.LEXICON, *map(recognizers.Written, shapes), recognizers.CARDINAL),
                   verbalizers={Form.LEXICON: recognizers.speak_lexicon, Form.CARDINAL: recognizers.speak_cardinal},
                   spellers={Form.CARDINAL: speller})


def select(tag: str) -> tuple[str, LanguageSpec, Variety]:
    """The standardized tag with its region, the language file and the variety (section 6, steps 1 to 5)."""
    import linguatag

    tag = linguatag.with_default_region(check_tag(tag))
    code = primary_subtag(tag)
    language = language_file(code) or core_language(code)
    match = linguatag.closest_lang(tag, [v.tag for v in language.varieties], lects="dialect")
    variety = next((v for v in language.varieties if v.tag == match), language.varieties[0])
    return tag, language, variety


def _not_honoured(lang: str, option: str, asked, applied, strict: bool):
    message = f"{lang!r} cannot produce {option}={asked!r}; {applied!r} applies"
    if strict:
        raise UnsupportedParameterError(message)
    warnings.warn(message, ParameterNotHonouredWarning, stacklevel=4)
    return applied


def _effective(tag: str, language: LanguageSpec, variety: Variety, params: NormalizationParams) -> NormalizationParams:
    defaults = merged_data(language.data, variety.data).get("defaults", FrozenMap())
    changes = {}
    for option in OPTIONS:
        if option in language.not_applicable or option == "default_gender":
            continue
        asked = getattr(params, option)
        default = defaults.get(option)
        if option == "phone_regions":
            region = subtags(tag)[2]
            default = frozenset({region}) if region in language.options[option] else frozenset()
            if asked is None:
                changes[option] = default
            elif not asked <= language.options[option]:
                changes[option] = _not_honoured(tag, option, asked, default, params.strict)
        elif asked is None:
            changes[option] = default
        elif asked not in language.options[option]:
            changes[option] = _not_honoured(tag, option, asked, default, params.strict)
    entry = params.default_gender.get(language.code)
    if entry is not None and language.genders and entry not in language.genders:
        raise UndefinedGrammaticalGender(tag, str(entry), frozenset(str(g) for g in language.genders))
    return replace(params, **changes)


@lru_cache(maxsize=128)
def lexicon_entries(tag: str, lexicon: FrozenMap) -> FrozenMap:
    """The entries of the primary subtag, then those of the full tag, which replace them key by key."""
    by_tag = {check_tag(key): entries for key, entries in lexicon.items()}
    return FrozenMap({**by_tag.get(primary_subtag(tag), {}), **by_tag.get(tag, {})})


def _check_lexicon(request: Request) -> None:
    """A lexicon value that a recognizer reads would change on a second pass (section 11). An entry that keeps
    its key, such as `{"MIX": "MIX"}`, is allowed: its span reads the value as written.

    The check depends on the tag, the language, the variety and the params, so it runs once for each of them. A
    check that raises is not cached, so each call with that lexicon raises again."""
    if request.params.lexicon:
        _check_lexicon_once(request.tag, request.variety, request.language, request.params)


@lru_cache(maxsize=128)
def _check_lexicon_once(tag: str, variety: Variety, language: LanguageSpec, params: NormalizationParams) -> None:
    from text2spoken.core.emoji import emoji_view
    from text2spoken.core.spans import classify
    from text2spoken.core.tokens import cut_tokens, default_tokenizer

    request = Request(tag, variety, language, params)
    for written, spoken in lexicon_entries(request.tag, request.params.lexicon).items():
        tokens = cut_tokens(default_tokenizer(spoken, request.tag), emoji_view(spoken))
        for claimed in classify(spoken, tokens, (), request):
            if not (claimed.form is Form.LEXICON and claimed.fields["spoken"] == spoken[claimed.start:claimed.end]):
                raise InvalidLexiconError(
                    f"the lexicon value {spoken!r} of {written!r} holds {spoken[claimed.start:claimed.end]!r}, "
                    f"which the {claimed.recognizer} recognizer reads, so a second pass would change it")


def resolve(lang: str, params: NormalizationParams) -> Request:
    tag, language, variety = select(lang)
    request = Request(tag, variety, language, _effective(tag, language, variety, params))
    _check_lexicon(request)
    return request


def supports(lang: str) -> Support:
    require_type(lang, "lang", str)
    tag, language, _ = select(lang)
    forms = frozenset(r.form for r in language.recognizers) & frozenset(language.verbalizers)
    return Support(tag=tag, code=language.code, forms=forms, genders=language.genders, animacies=language.animacies,
                   noun_classes=language.noun_classes, numeral_systems=language.numeral_systems,
                   options=FrozenMap(language.options), not_applicable=language.not_applicable,
                   context_words=language.context_words)


def effective_params(lang: str, params: NormalizationParams | None = None) -> NormalizationParams:
    require_type(lang, "lang", str)
    if params is not None:
        require_type(params, "params", NormalizationParams)
    tag, language, variety = select(lang)
    return _effective(tag, language, variety, params or NormalizationParams())
