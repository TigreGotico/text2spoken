"""The checks of the language file contract (design section 5.2), one function per clause.

Each check takes the module name and the LanguageSpec, and raises AssertionError on a breach. test_contract.py
runs them over every file in `text2spoken/lang/`, and over broken specs to show that each check bites.
"""
import ast
import json
import re
import subprocess
import sys
from importlib.resources import files
from importlib.util import find_spec
from pathlib import Path

import linguatag

from text2spoken import Features, NormalizationParams
from text2spoken.core import language as loader
from text2spoken.core.language import LanguageSpec, Request, check_tag, cldr_locale, plural_locales, rbnf_locales
from text2spoken.core.spans import FIELDS, Span
from text2spoken.core.spellers import RbnfSpeller, rbnf_engine
from text2spoken.core.tokens import default_tokenizer
from text2spoken.params import OPTIONS, Form, FrozenMap

FORM_METHOD = {Form.CARDINAL: "cardinal", Form.ORDINAL: "ordinal", Form.YEAR: "year", Form.DECIMAL: "decimal",
               Form.FRACTION: "fraction"}
METHOD_ARGS = {"cardinal": ("2",), "ordinal": ("2",), "year": ("2024",), "decimal": ("2", "5"),
               "fraction": ("1", "2")}
ALLOWED_IMPORTS = {"linguatag", "ovos_number_parser", "ovos_date_parser", "ovos_color_parser", "unicode_rbnf",
                   "quebra_frases"}
LAZY_ONLY = {"tugalex"}
PATTERN_REFUSED = re.compile(r"\\[dDwWsSbB1-9]|\(\?(?!:)")


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


def clause_6(name: str, spec: LanguageSpec) -> None:
    from text2spoken.params import freeze, thaw

    for where, data in (("data", spec.data), *((v.tag, v.data) for v in spec.varieties)):
        _json_only(data, where)
        assert freeze(json.loads(json.dumps(thaw(data)))) == data, f"{where} does not round-trip through JSON"


def check_pattern(pattern: str) -> None:
    refused = PATTERN_REFUSED.search(pattern)
    assert refused is None, f"{pattern!r} uses {refused.group()!r}, outside the portable subset"
    re.compile(pattern)


def clause_7(name: str, spec: LanguageSpec) -> None:
    for where, data in (("data", spec.data), *((v.tag, v.data) for v in spec.varieties)):
        for pattern in data.get("patterns", FrozenMap()).values():
            check_pattern(pattern)


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
    for field, values in (("gender", spec.genders), ("animacy", spec.animacies), ("noun_class", spec.noun_classes),
                          ("numeral_system", spec.numeral_systems)):
        for value in values:
            words = {n: speller.cardinal(n, Features(**{field: value}), request) for n in ("1", "2")}
            for other in values - {value}:
                others = {n: speller.cardinal(n, Features(**{field: other}), request) for n in ("1", "2")}
                assert any(words[n] != others[n] for n in words), f"{value} and {other} give the same words"
            distinct = [w for n, w in words.items()
                        if all(w != speller.cardinal(n, Features(**{field: o}), request) for o in values - {value})]
            assert any(any(w in cell.split() for cell in cells) for w in distinct), f"no row holds a {value} word"


def clause_10(name: str, spec: LanguageSpec) -> None:
    if spec.context_words:
        return
    from tests.conftest import rows
    from text2spoken import normalize

    for row in rows(name):
        assert normalize(row["text"], row["tag"], tokenizer=lambda text, lang: ()) == row["expected"], row["id"]


def _rbnf_spellers(spec: LanguageSpec) -> list[RbnfSpeller]:
    found = []
    for speller in spec.spellers.values():
        candidates = [speller, *vars(speller).values()]
        for candidate in candidates:
            nested = candidate.values() if isinstance(candidate, dict) else (candidate,)
            found += [s for s in nested if isinstance(s, RbnfSpeller)]
    return found


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


def clause_12(name: str, spec: LanguageSpec, source: str | None = None) -> None:
    path = Path(find_spec(f"text2spoken.lang.{name}").origin)
    check_imports(path.read_text(encoding="utf-8") if source is None else source)
    if source is None:
        events, added = sandbox_import(f"text2spoken.lang.{name}", str(path.parent))
        foreign = [m for m in added if not m.startswith("text2spoken.lang")]
        assert not events and not foreign, f"importing {name}: {events} {foreign}"


CLAUSES = [clause_1, clause_2, clause_3, clause_4, clause_5, clause_6, clause_7, clause_8, clause_9, clause_10,
           clause_11, clause_12]
