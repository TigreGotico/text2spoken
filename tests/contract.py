"""The checks of the language file contract (design section 5.2), one function per clause.

Each check takes the module name and the LanguageSpec, and raises AssertionError on a breach. test_contract.py
runs them over every file in `text2spoken/lang/`, and over broken specs to show that each check bites.
"""
import ast
import json
import re
import subprocess
import sys
from functools import cache
from importlib.metadata import requires
from importlib.resources import files
from importlib.util import find_spec
from pathlib import Path
from re import _parser
from types import ModuleType

import linguatag
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from tests.data_keys import ALTERNATIVES, OPTIONAL, PHONE_SHAPE_KEYS, READERS, SHAPES
from text2spoken import Features, NormalizationParams
from text2spoken.core import language as loader
from text2spoken.core import recognizers
from text2spoken.core.language import LanguageSpec, Request, check_tag, cldr_locale, plural_locales, rbnf_locales
from text2spoken.core.spans import FIELDS, Span
from text2spoken.core.recognizers import SHARED, speak_cardinal, speak_lexicon
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller, rbnf_engine
from text2spoken.core.tokens import default_tokenizer
from text2spoken.params import OPTIONS, Form, FrozenMap

FORM_METHOD = {Form.CARDINAL: "cardinal", Form.ORDINAL: "ordinal", Form.YEAR: "year", Form.DECIMAL: "decimal",
               Form.FRACTION: "fraction"}
METHOD_ARGS = {"cardinal": ("2",), "ordinal": ("2",), "year": ("2024",), "decimal": ("2", "5"),
               "fraction": ("1", "2")}
ALLOWED_IMPORTS = {"linguatag", "ovos_number_parser", "ovos_date_parser", "ovos_color_parser", "unicode_rbnf",
                   "quebra_frases"}
LAZY_ONLY = {"tugalex"}
DISTRIBUTIONS = {"linguatag": "linguatag", "ovos_number_parser": "ovos-number-parser",
                 "ovos_date_parser": "ovos-date-parser", "ovos_color_parser": "ovos-color-parser",
                 "unicode_rbnf": "unicode-rbnf", "quebra_frases": "quebra-frases", "tugalex": "tugalex"}
"""The distribution that installs each allowed import."""
SPELLER_DISTRIBUTIONS = {OvosNumberSpeller: "ovos-number-parser", RbnfSpeller: "unicode-rbnf"}
"""The distribution that each core speller imports when it speaks."""
PATTERN_REFUSED = re.compile(r"\\[dDwWsSbB1-9]|\(\?(?!:)")
DIGIT_RUN = [(_parser.IN, [(_parser.RANGE, (ord("0"), ord("9")))])]
"""`[0-9]`, as the parser reads it."""
REPEATS = (_parser.MAX_REPEAT, _parser.MIN_REPEAT)
"""A greedy or a lazy repeat, as the parser reads it."""


def language_files() -> list[str]:
    return sorted(e.name[:-3] for e in files("text2spoken.lang").iterdir()
                  if e.name.endswith(".py") and not e.name.startswith("_"))


def request_for(spec: LanguageSpec, variety_index: int = 0) -> Request:
    return Request(spec.varieties[variety_index].tag, spec.varieties[variety_index], spec, NormalizationParams())


def clause_1(name: str, spec: LanguageSpec) -> None:
    assert isinstance(spec, LanguageSpec), f"{name} defines no LANGUAGE"
    assert spec.code == name, f"LANGUAGE.code {spec.code!r} differs from the file name {name!r}"


def clause_2(name: str, spec: LanguageSpec) -> None:
    for tag in (spec.code, *(v.tag for v in spec.varieties)):
        assert check_tag(tag) == tag and linguatag.standardize_lang(tag) == tag, f"{tag!r} is not a standard tag"


def clause_3(name: str, spec: LanguageSpec, registry: dict | None = None) -> None:
    registry = loader._registry() if registry is None else registry
    served = {code for code, other in registry.items() if other is spec}
    assert served == {spec.code, *spec.serves}, f"{name} reads {sorted(served)}, not {[spec.code, *spec.serves]}"
    for code in spec.serves:
        assert re.fullmatch("[a-z][a-z][a-z]?", code) and check_tag(code) == code, f"serves {code!r} is no subtag"


def clause_4(name: str, spec: LanguageSpec) -> None:
    for recognizer in spec.recognizers:
        assert recognizer.form in spec.verbalizers, f"{recognizer.name} claims {recognizer.form} with no verbalizer"
    for form, method in FORM_METHOD.items():
        if form in spec.verbalizers:
            assert form in spec.spellers, f"{form} has a verbalizer and no speller"
    for form, speller in spec.spellers.items():
        method = FORM_METHOD[form]
        for index in range(len(spec.varieties)):
            try:
                words = getattr(speller, method)(*METHOD_ARGS[method], Features(), request_for(spec, index))
            except NotImplementedError:
                raise AssertionError(f"the {form} speller of {name} does not offer {method}")
            assert words and words == " ".join(words.split()), f"{method} gives {words!r}"


def samples(name: str) -> list[str]:
    from tests.conftest import rows

    return [row["text"] for row in rows(name)]


def _record_fields(value: FrozenMap) -> None:
    assert set(value) == FIELDS[Form.DECIMAL], f"amount record fields {sorted(value)}"


def check_span_fields(span: Span) -> None:
    assert set(span.fields) == FIELDS[span.form], f"{span.recognizer} emits {sorted(span.fields)} for {span.form}"
    if span.form in (Form.MONEY, Form.PERCENT, Form.MEASURE):
        amount = span.fields["amount"]
        for record in amount if isinstance(amount, tuple) else (amount,):
            _record_fields(record)


def clause_5(name: str, spec: LanguageSpec, texts: list[str] | None = None) -> None:
    texts = samples(name) if texts is None else texts
    seen = set()
    for index in range(len(spec.varieties)):
        request = request_for(spec, index)
        for text in texts:
            tokens = default_tokenizer(text, request.tag)
            for recognizer in spec.recognizers:
                for span in recognizer.find(text, tokens, request):
                    assert span.form is recognizer.form, f"{recognizer.name} emits {span.form}"
                    check_span_fields(span)
                    seen.add(recognizer.name)
    silent = {r.name for r in spec.recognizers} - seen - {"lexicon"}
    assert not silent, f"no sample sentence reaches the recognizers {sorted(silent)}"


def _json_only(value, where: str) -> None:
    if isinstance(value, FrozenMap):
        for key, item in value.items():
            assert type(key) is str, f"{where}: key {key!r} is not a str"
            _json_only(item, f"{where}.{key}")
    elif isinstance(value, tuple):
        for i, item in enumerate(value):
            _json_only(item, f"{where}[{i}]")
    else:
        assert value is None or type(value) in (str, int, float, bool), f"{where}: {value!r} is not a JSON value"


def check_data_keys(data: FrozenMap, where: str) -> None:
    """Each key of `data` that the core reads has the shape that `tests/data_keys.py` declares."""
    for key, shape in SHAPES.items():
        if key in data:
            shape(data[key], f"{where}.{key}")


SHARED_VERBALIZERS = {"speak_cardinal": speak_cardinal, "speak_lexicon": speak_lexicon}
"""The verbalizers of the core that a file can name, by their name in `READERS`."""


def required_keys(spec: LanguageSpec) -> set[str]:
    """The keys that the shared recognizers of the file read, by class, so that a subclass counts too, and the keys
    that the shared verbalizers of the file read."""
    used = {name for name, shared in SHARED.items() for r in spec.recognizers if isinstance(r, type(shared))}
    used |= {name for name, verbalizer in SHARED_VERBALIZERS.items() if verbalizer in spec.verbalizers.values()}
    return set().union(*(READERS[name] for name in used)) - OPTIONAL


def clause_6(name: str, spec: LanguageSpec) -> None:
    from text2spoken.params import freeze, thaw

    for where, data in (("data", spec.data), *((v.tag, v.data) for v in spec.varieties)):
        _json_only(data, where)
        assert freeze(json.loads(json.dumps(thaw(data)))) == data, f"{where} does not round-trip through JSON"
    required = required_keys(spec)
    for index, variety in enumerate(spec.varieties):
        data = request_for(spec, index).data
        check_data_keys(data, variety.tag)
        missing = required - set(data)
        for keys in ALTERNATIVES:
            missing -= keys
            if keys & required and not keys & set(data):
                missing.add(" or ".join(sorted(keys)))
        assert not missing, f"{variety.tag}: no {sorted(missing)}, which its shared recognizers and verbalizers read"


def check_pattern(pattern: str) -> None:
    refused = PATTERN_REFUSED.search(pattern)
    assert refused is None, f"{pattern!r} uses {refused.group()!r}, outside the portable subset"
    re.compile(pattern)


def routed_patterns(name: str, spec: LanguageSpec) -> set[re.Pattern]:
    """Each pattern that reaches `digit_run_matches` while the recognizers of the file read its samples, in each
    variety. For the run, each module that holds the helper holds a recording wrapper in its place. The wrapper
    gives no matches for a pattern without the shape, so no recognizer reads a match that the helper misreads."""
    helper = recognizers.digit_run_matches
    routed = set()

    def recording(pattern, folded):
        routed.add(re.compile(pattern))
        return helper(pattern, folded) if has_digit_run_shape(pattern) else iter(())

    holders = [vars(m) for m in list(sys.modules.values())
               if isinstance(m, ModuleType) and vars(m).get("digit_run_matches") is helper]
    for holder in holders:
        holder["digit_run_matches"] = recording
    try:
        for index in range(len(spec.varieties)):
            request = request_for(spec, index)
            for text in samples(name):
                tokens = default_tokenizer(text, request.tag)
                for recognizer in spec.recognizers:
                    list(recognizer.find(text, tokens, request))
    finally:
        for holder in holders:
            holder["digit_run_matches"] = helper
    return routed


def _no_digit_character(items: list) -> bool:
    """Whether the parsed items are one character, or one class of characters, with no digit."""
    if len(items) != 1 or items[0][0] not in (_parser.LITERAL, _parser.IN):
        return False
    op, arg = items[0]
    return all(o is _parser.LITERAL and not "0" <= chr(a) <= "9"
               or o is _parser.RANGE and (a[1] < ord("0") or a[0] > ord("9"))
               for o, a in ([items[0]] if op is _parser.LITERAL else arg))


def _starts_with_digit_run(items: list) -> bool:
    """Whether the parsed items start with an optional character that is no digit and then a greedy `[0-9]+`, or
    with an alternation whose every branch does. A lazy run can end a match inside a digit run, and the helper
    tries one match for each run."""
    if items and items[0][0] is _parser.BRANCH:
        return all(_starts_with_digit_run(list(branch)) for branch in items[0][1][1])
    if items and items[0][0] in REPEATS and items[0][1][:2] == (0, 1) and _no_digit_character(list(items[0][1][2])):
        items = items[1:]
    return (bool(items) and items[0][0] is _parser.MAX_REPEAT and items[0][1][:2] == (1, _parser.MAXREPEAT)
            and list(items[0][1][2]) == DIGIT_RUN)


def _ends_at_a_run_end(items: list) -> bool:
    """Whether each match of the parsed items ends at the end of a digit run or after a character that is no digit.
    The helper tries one match for each digit run, so a match that ends inside a run hides the next match there. An
    item that can match nothing passes the question on to the item before it."""
    for op, arg in reversed(items):
        if op in REPEATS and arg[0] == 0:
            if not _ends_at_a_run_end(list(arg[2])):
                return False
        elif op is _parser.MAX_REPEAT and arg[1] == _parser.MAXREPEAT and list(arg[2]) == DIGIT_RUN:
            return True
        elif op in REPEATS:
            return _ends_at_a_run_end(list(arg[2]))
        elif op is _parser.BRANCH:
            return all(_ends_at_a_run_end(list(branch)) for branch in arg[1])
        elif op is _parser.SUBPATTERN:
            return _ends_at_a_run_end(list(arg[3]))
        else:
            return _no_digit_character([(op, arg)])
    return False


@cache
def has_digit_run_shape(pattern: re.Pattern | str) -> bool:
    """`digit_run_matches` gives the matches of `finditer` only for a pattern that starts with an optional character
    that is no digit and then `[0-9]+`, or for an alternation of such patterns, and whose every match ends at the end
    of a digit run or after a character that is no digit. The check reads the parsed pattern."""
    pattern = re.compile(pattern)
    items = list(_parser.parse(pattern.pattern, pattern.flags))
    return _starts_with_digit_run(items) and _ends_at_a_run_end(items)


def check_digit_run_pattern(pattern: re.Pattern | str) -> None:
    assert has_digit_run_shape(pattern), (
        f"{re.compile(pattern).pattern!r} reaches digit_run_matches, and does not start with an optional character"
        " that is no digit and then a greedy [0-9]+, or can end a match inside a digit run")


def clause_7(name: str, spec: LanguageSpec) -> None:
    """Every table that holds regexes: `patterns`, and the phone shape tables, which the core compiles. A pattern
    that reaches `digit_run_matches` also has the shape that the helper reads."""
    for data in (spec.data, *(v.data for v in spec.varieties)):
        for pattern in (*data.get("patterns", FrozenMap()).values(),
                        *(shape for key in PHONE_SHAPE_KEYS for shape in data.get(key, ()))):
            check_pattern(pattern)
    for pattern in routed_patterns(name, spec):
        check_digit_run_pattern(pattern)


def clause_8(name: str, spec: LanguageSpec) -> None:
    for option in OPTIONS:
        assert (option in spec.options) != (option in spec.not_applicable), f"{option} is in both or in neither"
    assert set(spec.options) | spec.not_applicable == set(OPTIONS), "an option that NormalizationParams lacks"
    if not spec.genders:
        assert "default_gender" in spec.not_applicable and spec.default_gender is None
    else:
        assert spec.default_gender in spec.genders, f"default_gender {spec.default_gender} is not in genders"
    for index in range(len(spec.varieties)):
        defaults = request_for(spec, index).data.get("defaults", FrozenMap())
        for option, values in spec.options.items():
            if option in ("default_gender", "phone_regions"):
                continue
            assert defaults.get(option) in values, f"{spec.varieties[index].tag}: no valid default for {option}"


def clause_9(name: str, spec: LanguageSpec, expected_cells: list[str] | None = None) -> None:
    from tests.conftest import rows

    cells = [row["expected"] for row in rows(name)] if expected_cells is None else expected_cells
    speller = spec.spellers.get(Form.CARDINAL)
    request = request_for(spec)
    # Values may differ in one case only, as German masculine "einen" and neuter "ein" in the accusative, so the
    # check also reads each case that an RBNF cardinal map of the file names.
    cases = (None, *sorted({key.case for s in _rbnf_spellers(spec) for key in s.cardinal_sets if key.case}))
    keys = [(n, case) for n in ("1", "2") for case in cases]
    for field, values in (("gender", spec.genders), ("animacy", spec.animacies), ("noun_class", spec.noun_classes),
                          ("numeral_system", spec.numeral_systems)):
        def spoken(value) -> dict:
            return {(n, case): speller.cardinal(n, Features(**{field: value}, case=case), request) for n, case in keys}
        for value in values:
            words = spoken(value)
            for other in values - {value}:
                others = spoken(other)
                assert any(words[k] != others[k] for k in words), f"{value} and {other} give the same words"
            distinct = [w for k, w in words.items() if all(w != spoken(o)[k] for o in values - {value})]
            assert any(any(w in cell.split() for cell in cells) for w in distinct), f"no row holds a {value} word"


def clause_10(name: str, spec: LanguageSpec) -> None:
    if spec.context_words:
        return
    from tests.conftest import rows
    from text2spoken import normalize

    for row in rows(name):
        assert normalize(row["text"], row["tag"], tokenizer=lambda text, lang: ()) == row["expected"], row["id"]


def _spellers(spec: LanguageSpec) -> list:
    """Each speller that the file names, and each speller that one of them holds, alone or in a dict."""
    found = []
    for speller in spec.spellers.values():
        for candidate in (speller, *vars(speller).values()):
            found += candidate.values() if isinstance(candidate, dict) else (candidate,)
    return found


def _rbnf_spellers(spec: LanguageSpec) -> list[RbnfSpeller]:
    return [s for s in _spellers(spec) if isinstance(s, RbnfSpeller)]


def clause_11(name: str, spec: LanguageSpec) -> None:
    spellers = _rbnf_spellers(spec)
    for variety in spec.varieties:
        assert cldr_locale(variety.tag, plural_locales(), spec), f"{variety.tag}: no CLDR plural rules"
        for speller in spellers:
            locale = cldr_locale(variety.tag, rbnf_locales(), spec)
            assert locale, f"{variety.tag}: no RBNF locale"
            names = set(rbnf_engine(locale).rulesets)
            used = {*speller.cardinal_sets.values(), *speller.ordinal_sets.values(), speller.year_set}
            assert used <= names, f"{variety.tag}: {sorted(used - names)} are not rule sets of {locale}"


def _imports(source: str) -> tuple[set[str], set[str]]:
    tree = ast.parse(source)
    top, nested = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            target = top if node in tree.body else nested
            target.update(n.split(".")[0] for n in names)
    return top, nested


def check_imports(source: str) -> None:
    top, nested = _imports(source)
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    assert top <= stdlib | ALLOWED_IMPORTS | {"text2spoken"}, f"imports {sorted(top - stdlib - ALLOWED_IMPORTS)}"
    assert nested <= stdlib | ALLOWED_IMPORTS | LAZY_ONLY | {"text2spoken"}, f"imports {sorted(nested)}"


def declared(requirements: list[str], extra: str) -> set[str]:
    """The distributions that an install of the package with `extra` holds; "" is an install with no extra."""
    found = set()
    for line in requirements:
        requirement = Requirement(line)
        if requirement.marker is None or requirement.marker.evaluate({"extra": extra}):
            found.add(canonicalize_name(requirement.name))
    return found


def check_declared(source: str, code: str, requirements: list[str] | None = None) -> None:
    """A top-level import is a dependency of the package, and a lazy import is one too or one of the extra named
    after the language code. The `test` extra counts for neither."""
    requirements = requires("text2spoken") if requirements is None else requirements
    top, nested = _imports(source)
    for imports, extra in ((top, ""), (nested, code)):
        wanted = {canonicalize_name(DISTRIBUTIONS[m]) for m in imports if m in DISTRIBUTIONS}
        missing = wanted - declared(requirements, extra)
        install = f"text2spoken[{extra}]" if extra else "text2spoken"
        assert not missing, f"imports {sorted(missing)}, which an install of {install} does not hold"


def check_speller_dependencies(spec: LanguageSpec, requirements: list[str] | None = None) -> None:
    """Each core speller that the file names imports a distribution of the package or of the language extra."""
    requirements = requires("text2spoken") if requirements is None else requirements
    wanted = {canonicalize_name(SPELLER_DISTRIBUTIONS[type(s)]) for s in _spellers(spec)
              if type(s) in SPELLER_DISTRIBUTIONS}
    missing = wanted - declared(requirements, spec.code)
    assert not missing, f"its spellers import {sorted(missing)}, which text2spoken[{spec.code}] does not hold"


_SANDBOX = """
import socket, sys
import text2spoken.core.recognizers, text2spoken.core.spellers, text2spoken.core.color
before = set(sys.modules)
events = []
def hook(event, args):
    if event == "open" and not str(args[0]).startswith(sys.argv[2]):
        events.append(f"open {args[0]}")
    if event.startswith("socket."):
        events.append(event)
sys.addaudithook(hook)
__import__(sys.argv[1])
added = set(sys.modules) - before - {sys.argv[1]}
print(repr((events, sorted(added))))
"""


def sandbox_import(module: str, allowed_dir: str, path: str = "") -> tuple[list[str], list[str]]:
    """The files opened and sockets used outside `allowed_dir`, and the modules added, by importing `module`."""
    env = {**__import__("os").environ, "PYTHONPATH": path} if path else None
    out = subprocess.run([sys.executable, "-c", _SANDBOX, module, allowed_dir], capture_output=True, text=True,
                         check=True, env=env).stdout
    return ast.literal_eval(out.strip().splitlines()[-1])


def clause_12(name: str, spec: LanguageSpec, source: str | None = None, requirements: list[str] | None = None) -> None:
    path = Path(find_spec(f"text2spoken.lang.{name}").origin) if source is None else None
    text = source if path is None else path.read_text(encoding="utf-8")
    check_imports(text)
    check_declared(text, spec.code, requirements)
    check_speller_dependencies(spec, requirements)
    if path is not None:
        events, added = sandbox_import(f"text2spoken.lang.{name}", str(path.parent))
        foreign = [m for m in added if not m.startswith("text2spoken.lang")]
        assert not events and not foreign, f"importing {name}: {events} {foreign}"


CLAUSES = [clause_1, clause_2, clause_3, clause_4, clause_5, clause_6, clause_7, clause_8, clause_9, clause_10,
           clause_11, clause_12]
