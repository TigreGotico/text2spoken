"""LanguageSpec, Variety, Request, the loader and CLDR locale mapping (design sections 5.2, 5.3, 6)."""
from __future__ import annotations

import re
import sys
import warnings
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field, replace
from decimal import Decimal, getcontext, localcontext
from functools import cache, lru_cache
from importlib import import_module
from importlib.resources import files
from typing import TYPE_CHECKING

from text2spoken.errors import (DeclinedReading, InvalidLanguageTagError, InvalidLexiconError,
                                ParameterNotHonouredWarning, UndefinedGrammaticalGender, UnsupportedParameterError,
                                require_type)
from text2spoken.params import OPTIONS, Animacy, FrozenMap, Form, GrammaticalGender, NormalizationParams, freeze

if TYPE_CHECKING:
    from text2spoken.core.say_as import ResolvedSayAs, SayAs
    from text2spoken.core.spans import Features, Recognizer, Span, Verbalizer
    from text2spoken.core.spellers import NumberSpeller


def concatenate(spoken: str, prefix: str, suffix: str) -> str:
    """The core attachment: the prefix joins the first spoken word and the suffix joins the last."""
    return prefix + spoken + suffix


def drop_affixes(spoken: str, prefix: str, suffix: str) -> str:
    """The attachment of a language whose verbalizers already say each affix that it declares: the spoken words
    alone."""
    return spoken


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
    say_as: ResolvedSayAs | None = None
    """The say-as that the call reads (section 17), or None."""

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
def cldr_number_marks() -> FrozenMap:
    """The CLDR decimal and group marks of each locale, by the script of the digits, from
    `data/cldr/number-marks.json`. A language holds its marks under its subtag, and another locale holds them under
    its CLDR id only where they differ from the marks of its language (`scripts/extract_number_marks.py`)."""
    import json

    table = json.loads((files("text2spoken") / "data" / "cldr" / "number-marks.json").read_text(encoding="utf-8"))
    return freeze(table["marks"])


def _number_marks(marks: Mapping[str, Mapping[str, str]]) -> FrozenMap:
    """CLDR marks as the `number_marks` data of a language file: one entry for each script."""
    return FrozenMap({script: (entry,) for script, entry in marks.items()})


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
    """The CLDR plural category of a written ASCII number, such as `1.0` or `5`, in the variety of the request.

    The operands come from the fixed-point form of the number. `get_plural_category` of unicode_rbnf reads them
    from `str(Decimal)`, which writes `0.0000001` as `1E-7`: it then finds no fraction digits, and `1.0E-7` raises
    `ValueError`. So this function evaluates the rules of unicode_rbnf with operands of its own.

    The rule runs at the precision of the number. Each operand of a CLDR rule has at most as many digits as the
    number, and the quotient of `i % m` has at most as many digits as `i`, so that precision keeps the rule exact.
    The default context rounds at 28 digits: `10**28 + 1` then takes the category of `10**28`, and `i % 10` raises
    `InvalidOperation` from 10**29. A number can reach this function before a speller checks `DIGIT_BOUND`, so the
    precision follows the number.

    The plural operands `f` and `t` convert the fraction digits to an `int` from a string, and Python refuses a
    string of more digits than `sys.get_int_max_str_digits()`. So a number whose fraction has more digits than that
    limit raises `DeclinedReading`, and its span stays as written. An integer part of more digits than the limit
    declines too, for another cause: the operand `i` comes from `int(Decimal)`, which has no limit, so the check
    declines early what a speller declines later at `DIGIT_BOUND`, and saves the time of `int(Decimal)`. A limit of
    0 is no limit."""
    from unicode_rbnf.plural_rules import PluralType, _eval_condition, _load

    locale = cldr_locale(request.tag, plural_locales(), request.language)
    if locale is None:
        raise LookupError(f"no CLDR plural rules for {request.tag!r}")
    number = Decimal(written)
    _, digits, exponent = number.as_tuple()
    fraction = max(-exponent, 0)
    integer = max(len(digits) - fraction, 0)
    limit = sys.get_int_max_str_digits()
    if limit and max(fraction, integer) > limit:
        raise DeclinedReading(f"a number of {integer} integer and {fraction} fraction digits passes the int string "
                              f"limit of {limit} digits, so it has no plural category")
    with localcontext(prec=max(len(digits), getcontext().prec)):
        n = abs(number)
        visible = format(n, "f").partition(".")[2]
        trimmed = visible.rstrip("0")
        operands = {"n": n, "i": Decimal(int(n)), "v": Decimal(len(visible)), "w": Decimal(len(trimmed)),
                    "f": Decimal(int(visible or "0")), "t": Decimal(int(trimmed or "0")), "c": Decimal(0),
                    "e": Decimal(0)}
        rules = _load(PluralType.CARDINAL)[locale]
        return next((category for category in ("zero", "one", "two", "few", "many") for rule, condition in rules
                     if rule == category and _eval_condition(condition, operands)), "other")


@cache
def core_language(code: str) -> LanguageSpec:
    """The language of a code with no file: cardinals through ovos-number-parser where it has a writer of its own
    for the language, else through RBNF where RBNF has the locale (section 6.1). `RBNF_HELD` names the languages with
    a writer that read through RBNF for now.

    A minus before a number reads when the speller reads it. The parser reads it when its reading of -1 has a word
    that its reading of 1 does not have. RBNF reads it when the cardinal rule set has a `-x` rule, in the rule set or
    in the rule set that its 0 rule names. `sign_words` holds that word, and `speak_rbnf_cardinal` reads the number
    through the speller. `RBNF_CARDINAL` keeps as written a minus that may be no minus.

    An ordinal reads through the speller of the cardinals when it reads ordinals: the parser when it reads the
    ordinal of 1 (`writer_ordinals`), RBNF when the locale has an ordinal rule set (`rbnf_ordinals`). A language
    whose parser reads no ordinal reads them through RBNF, and a language of `RBNF_HELD` with no RBNF ordinal rule
    set reads them through the parser, because `RBNF_HELD` names a class of cardinals. The ordinal speller
    is the `ORDINAL` speller of the language, which a say-as ordinal reads through (section 17.5); no recognizer of
    the language claims an ordinal. Where the ordinal speller reads more than one gender, `genders` holds them, and
    `default_gender` chooses the gender.

    A decimal reads in the marks of CLDR for the locale (`cldr_number_marks`), when the speller reads it. The parser
    reads it when it reads 1.5. RBNF reads it when the cardinal rule set has an `x.x` rule, in the rule set or in
    the rule set that its 0 rule names. Each other CLDR locale of the language whose marks differ is a variety.

    A numeric date stays as written, and a say-as `date` reads through the `DATE` verbalizer (section 17.5): the
    `spoken_date` of ovos-date-parser when it reads the language, else the CLDR `long` date pattern of the locale
    (`speak_cldr_date`), when `long_date` gives its parts and the language has an ordinal speller for an ordinal
    day."""
    from unicode_rbnf import RbnfEngine
    from unicode_rbnf.engine import RbnfSpecialRule, TextRulePart

    from text2spoken.core import parsers, recognizers
    from text2spoken.core.dates import date_locales, long_date
    from text2spoken.core.spans import Features
    from text2spoken.core.spellers import CARDINAL_RULE_SETS, RBNF_HELD, OvosNumberSpeller, RbnfSpeller, rbnf_engine, words
    import linguatag

    tag = linguatag.with_default_region(code)
    bare = LanguageSpec(code=code, serves=(), cldr_aliases=(), varieties=(Variety(tag),), data=FrozenMap(),
                        recognizers=(recognizers.LEXICON,), verbalizers={Form.LEXICON: recognizers.speak_lexicon},
                        spellers={}, genders=frozenset(), default_gender=None, animacies=frozenset(),
                        noun_classes=frozenset(), numeral_systems=frozenset(), context_words=True, options={},
                        not_applicable=frozenset(OPTIONS))
    locale = cldr_locale(tag, rbnf_locales(), bare)
    if code in parsers.number_writer_languages() and code not in RBNF_HELD:
        speller = OvosNumberSpeller({})
        one = words(parsers.pronounce_number(1, tag)).split()
        try:
            negative = words(parsers.pronounce_number(-1, tag)).split()
        except (ValueError, NotImplementedError):
            negative = []
        minus = " ".join(word for word in negative if word not in one)
        sign_words = {"-": minus} if minus else {}
        ordinal_speller, genders = writer_ordinals(tag)
        ordinals = rbnf_ordinals(locale) if ordinal_speller is None and locale is not None else {}
        if ordinals:
            ordinal_speller = RbnfSpeller(cardinal={Features(): "spellout-numbering"}, ordinal=ordinals)
        try:
            decimals = bool(words(parsers.pronounce_number(1.5, tag, places=1)))
        except (ValueError, NotImplementedError):
            decimals = False
    elif locale is None:
        return bare
    else:
        names = rbnf_engine(locale).rulesets
        cardinal = next(name for name in CARDINAL_RULE_SETS if name in names)
        ordinals = rbnf_ordinals(locale)
        decimal = _special_rule_set(names, cardinal, RbnfSpecialRule.IMPROPER_FRACTION)
        speller = RbnfSpeller(cardinal={Features(): cardinal}, ordinal=ordinals or {Features(): cardinal},
                              decimal=decimal)
        ordinal_speller, genders = speller if ordinals else None, frozenset()
        if not ordinals and code in parsers.number_writer_languages():
            ordinal_speller, genders = writer_ordinals(tag)
        minus = names[cardinal].find_special_rule(RbnfSpecialRule.NEGATIVE_NUMBER, names)
        sign_words = {} if minus is None else {
            "-": "".join(part.text for part in minus.parts if isinstance(part, TextRulePart)).strip()}
        decimals = decimal is not None
    own_ordinal = locale is not None and any(
        "digits-ordinal" in RbnfEngine.for_language(name).rulesets
        for name in (locale, locale.split("_")[0]) if name in rbnf_locales())
    verbalizers = {Form.LEXICON: recognizers.speak_lexicon, Form.CARDINAL: recognizers.speak_rbnf_cardinal}
    try:
        parsers.spoken_date(tag, day=1, month=1, year=2000)
        verbalizers[Form.DATE] = recognizers.speak_spoken_date
    except NotImplementedError:
        date_locale = cldr_locale(tag, date_locales(), bare)
        pattern = None if date_locale is None else long_date(date_locale)
        if pattern is not None and (ordinal_speller is not None or ("ordinal_day", "") not in pattern[0]):
            verbalizers[Form.DATE] = recognizers.speak_cldr_date
    shapes = (recognizers.SHARED["money"], recognizers.SHARED["percent"], recognizers.SHARED["measure"],
              recognizers.SHARED["date_numeric"], recognizers.SHARED["fraction"],
              recognizers.OrdinalStop(bare_stop=not own_ordinal))
    table = cldr_number_marks()
    data = {**recognizers.written_shapes(), "sign_words": FrozenMap(sign_words)}
    if code in table:
        data["number_marks"] = _number_marks(table[code])
    varieties = (Variety(tag), *(Variety(name.replace("_", "-"), FrozenMap({"number_marks": _number_marks(marks)}))
                                 for name, marks in table.items() if name.startswith(code + "_")))
    numbers = (recognizers.RBNF_CARDINAL, recognizers.RBNF_DECIMAL) if decimals else (recognizers.RBNF_CARDINAL,)
    spellers = {Form.CARDINAL: speller}
    if decimals:
        verbalizers[Form.DECIMAL] = recognizers.speak_rbnf_decimal
        spellers[Form.DECIMAL] = speller
    if ordinal_speller:
        spellers[Form.ORDINAL] = ordinal_speller
    return replace(bare, varieties=varieties, data=FrozenMap(data),
                   recognizers=(recognizers.LEXICON, *map(recognizers.Written, shapes), *numbers),
                   verbalizers=verbalizers, spellers=spellers,
                   genders=genders | {features.gender for features in ordinals if features.gender is not None})


WRITER_GENDERS = FrozenMap({GrammaticalGender.MASCULINE: "masculine", GrammaticalGender.FEMININE: "feminine",
                            GrammaticalGender.NEUTER: "neutral"})
"""The `gender` argument of ovos-number-parser for each gender that it reads."""

NEUTER_READS_MASCULINE = frozenset({"ro"})
"""Languages whose neuter ordinal is the masculine one, which ovos-number-parser reads with no article in the neuter,
as Romanian "al treilea", masculine and neuter (Wiktionary, "treilea")."""


def writer_ordinals(tag: str) -> tuple[NumberSpeller | None, frozenset[GrammaticalGender]]:
    """The writer ordinal speller, or None when the writer reads no ordinal of 1, and its genders: those whose
    ordinals of 1 to 3 differ from the masculine ones, with the masculine, as Polish "trzeci", "trzecia", "trzecie"."""
    from text2spoken.core import parsers
    from text2spoken.core.spellers import OvosNumberSpeller, words

    try:
        if not parsers.pronounce_ordinal(1, tag):
            return None, frozenset()
    except NotImplementedError:
        return None, frozenset()

    def readings(gender: GrammaticalGender) -> tuple[str, ...]:
        argument = parsers.GrammaticalGender(WRITER_GENDERS[gender])
        return tuple(words(parsers.pronounce_ordinal(number, tag, gender=argument)) for number in (1, 2, 3))

    masculine = readings(GrammaticalGender.MASCULINE)
    others = frozenset(gender for gender in WRITER_GENDERS
                       if gender is not GrammaticalGender.MASCULINE and readings(gender) != masculine)
    gender_arg = WRITER_GENDERS
    if tag.split("-")[0] in NEUTER_READS_MASCULINE:
        gender_arg = {**WRITER_GENDERS, GrammaticalGender.NEUTER: "masculine"}
    return OvosNumberSpeller(gender_arg), (others | {GrammaticalGender.MASCULINE}) if others else frozenset()


def rbnf_ordinals(locale: str) -> dict[Features, str]:
    """The ordinal rule sets of an RBNF locale, by gender: `spellout-ordinal`, else the masculine, else the common
    rule set reads with no gender. A gender keys its rule set only where RBNF has rule sets for more than one gender.
    Empty when the locale has none of them."""
    from text2spoken.core.spans import Features
    from text2spoken.core.spellers import rbnf_engine

    names = rbnf_engine(locale).rulesets
    default = next((n for n in ("spellout-ordinal", "spellout-ordinal-masculine", "spellout-ordinal-common")
                    if n in names), None)
    if default is None:
        return {}
    gendered = {Features(gender=gender): f"spellout-ordinal-{gender}" for gender in GrammaticalGender
                if f"spellout-ordinal-{gender}" in names}
    return {Features(): default, **(gendered if len(gendered) > 1 else {})}


def _special_rule_set(names: Mapping, name: str, rule) -> str | None:
    """The rule set that holds the special rule `rule` for the rule set `name`: the rule set itself, or the rule
    set that its 0 rule names, as `RbnfRuleSet.find_special_rule` looks it up."""
    from unicode_rbnf.engine import ReplaceRulePart

    while name is not None:
        if rule in names[name].special_rules:
            return name
        zero = names[name].numeric_rules.get(0)
        name = zero.parts[0].ruleset_name if zero and zero.parts and isinstance(zero.parts[0], ReplaceRulePart) \
            else None
    return None


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
        tokens = cut_tokens(default_tokenizer(spoken, request.tag), emoji_view(spoken, request.memo))
        for claimed in classify(spoken, tokens, (), request):
            if not (claimed.form is Form.LEXICON and claimed.fields["spoken"] == spoken[claimed.start:claimed.end]):
                raise InvalidLexiconError(
                    f"the lexicon value {spoken!r} of {written!r} holds {spoken[claimed.start:claimed.end]!r}, "
                    f"which the {claimed.recognizer} recognizer reads, so a second pass would change it")


def resolve(lang: str, params: NormalizationParams, say_as: SayAs | None = None) -> Request:
    tag, language, variety = select(lang)
    resolved = None
    if say_as is not None:
        from text2spoken.core.say_as import read

        resolved, read_params = read(say_as, tag, language, merged_data(language.data, variety.data), params)
        effective = _effective(tag, language, variety, read_params)
        if resolved is not None and read_params is not params:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                resolved = replace(resolved, plain=_effective(tag, language, variety, params))
        elif resolved is not None:
            resolved = replace(resolved, plain=effective)
    else:
        effective = _effective(tag, language, variety, params)
    request = Request(tag, variety, language, effective, say_as=resolved)
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
