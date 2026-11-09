"""Section 5.2: every language file passes each clause, and each clause check fails on a broken file."""
import ast
from dataclasses import replace
from importlib import import_module
from importlib.metadata import requires
from importlib.resources import files

import pytest

from tests import contract
from tests.conftest import rows
from tests.contract import CLAUSES, language_files
from tests.data_keys import OPTIONAL, READERS, SHAPES
from tests.fixtures import qac
from text2spoken.core import language as loader
from text2spoken.core.language import Request, Variety, select
from text2spoken.core.recognizers import SHARED
from text2spoken.core.spans import Features
from text2spoken.core.spellers import OvosNumberSpeller, RbnfSpeller
from text2spoken.core.tokens import default_tokenizer
from text2spoken.params import Form, FrozenMap, GrammaticalGender, NormalizationParams, freeze, thaw

FILES = language_files()
STUB = qac.LANGUAGE


def test_the_contract_has_twelve_clauses():
    assert [c.__name__ for c in CLAUSES] == [f"clause_{n}" for n in range(1, 13)]


@pytest.mark.parametrize("clause", CLAUSES, ids=[c.__name__ for c in CLAUSES])
@pytest.mark.parametrize("name", FILES)
def test_language_file_passes(name, clause):
    clause(name, import_module(f"text2spoken.lang.{name}").LANGUAGE)


@pytest.fixture
def en():
    return import_module("text2spoken.lang.en").LANGUAGE


def test_clause_1_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_1("en", replace(en, code="eng"))


def test_clause_2_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_2("en", replace(en, varieties=(Variety("en-gb"),)))


def test_clause_3_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_3("en", en, registry={"en": en, "sco": en})
    with pytest.raises(AssertionError):
        contract.clause_3("en", replace(en, serves=("en-US",)), registry={"en": en})


def test_clause_3_loader_refuses_two_files_for_one_code(monkeypatch, en):
    loader._registry.cache_clear()
    monkeypatch.setattr(loader, "import_module", lambda name: type("M", (), {"LANGUAGE": replace(en, serves=("en",))}))
    with pytest.raises(RuntimeError, match="two language files"):
        loader._registry()
    loader._registry.cache_clear()


def test_clause_4_bites(en):
    without = {f: v for f, v in en.verbalizers.items() if f is not Form.CARDINAL}
    with pytest.raises(AssertionError):
        contract.clause_4("en", replace(en, verbalizers=without))
    rbnf = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})
    with pytest.raises(AssertionError):
        contract.clause_4("en", replace(en, spellers={**en.spellers, Form.DECIMAL: rbnf}))


class _DropsScript:
    name, form = "cardinal", Form.CARDINAL

    def find(self, text, tokens, request):
        for span in import_module("text2spoken.core.recognizers").CARDINAL.find(text, tokens, request):
            yield replace(span, fields=FrozenMap({k: v for k, v in span.fields.items() if k != "script"}))


def test_clause_5_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_5("en", replace(en, recognizers=(_DropsScript(),)), texts=["I have 3 cats."])
    with pytest.raises(AssertionError, match="no sample sentence"):
        contract.clause_5("en", en, texts=["no number here"])


def test_clause_6_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_6("en", replace(en, data=FrozenMap({"x": frozenset({1})})))
    with pytest.raises(AssertionError):
        contract.clause_6("en", replace(en, data=FrozenMap({"x": GrammaticalGender.FEMININE})))


def test_the_stub_passes_the_data_and_import_clauses():
    contract.clause_6("qac", STUB)
    contract.clause_7("qac", STUB)
    contract.clause_12("qac", STUB, source=(files("tests.fixtures") / "qac.py").read_text(encoding="utf-8"))


BAD_KEYS = [
    ("digit_words", "0123456789"),
    ("digit_words", ["ze", "wa"]),
    ("digit_words", ["ze", "wa", "tu", "ri", "fo", "fa", "si", "se", "ei", 9]),
    ("number_marks", {"latn": [{"decimal": ".", "group": ","}]}),
    ("number_marks", {"Latn": []}),
    ("number_marks", {"Latn": [{"decimal": "."}]}),
    ("sign_words", {"–": "minu"}),
    ("leads", ["#"]),
    ("leads", {"#": 1}),
    ("symbols", {"$": "cash"}),
    ("percent", {"signs": ["%"]}),
    ("percent", {"signs": "%", "position": "after"}),
    ("operators", {"+-": "plus"}),
    ("short_codes", ["9 1 1"]),
    ("short_codes", [911]),
    ("currencies", {"USD": {"one": "dollar"}}),
    ("day_periods", {"pm": "pm"}),
    ("defaults", {"clocks": "12h"}),
    ("range_word", ["to"]),
    ("color_words", "colour"),
    ("phone_shapes", {"us": "[0-9]{3}"}),
    ("units", ["kg"]),
    ("clock_marks", [{"mark": "h", "seconds": False, "needs": "none", "closes_hour": "yes"}]),
]


@pytest.mark.parametrize(("key", "value"), BAD_KEYS, ids=[f"{k}-{i}" for i, (k, _) in enumerate(BAD_KEYS)])
def test_clause_6_checks_the_shape_of_each_key_the_core_reads(key, value):
    with pytest.raises(AssertionError, match=key):
        contract.clause_6("qac", replace(STUB, data=freeze({**thaw(STUB.data), key: value})))
    variety = Variety("qac", freeze({key: value}))
    with pytest.raises(AssertionError, match=key):
        contract.clause_6("qac", replace(STUB, varieties=(variety,)))


def test_clause_6_requires_the_keys_of_each_shared_recognizer():
    """The stub lists the shared percent and telephone recognizers, gives no `percent`, and writes `phone_word`."""
    data = freeze({**thaw(STUB.data), "phone_word": ["ligue"]})
    spec = replace(STUB, data=data, recognizers=(*STUB.recognizers, SHARED["percent"], SHARED["telephone"]))
    with pytest.raises(AssertionError, match="which its shared recognizers and verbalizers read") as error:
        contract.clause_6("qac", spec)
    assert "'percent'" in str(error.value) and "'phone_words'" in str(error.value)


def test_clause_6_requires_the_keys_of_a_subclass_of_a_shared_recognizer(en):
    telephone = next(r for r in en.recognizers if r.name == "telephone")
    assert type(telephone) is not type(SHARED["telephone"])
    with pytest.raises(AssertionError, match="'phone_words'"):
        contract.clause_6("qac", replace(STUB, recognizers=(*STUB.recognizers, telephone)))


def test_clause_6_requires_the_keys_in_each_variety():
    percent = freeze({"percent": {"signs": ["%"], "position": "after"}, "range_word": "al"})
    varieties = (Variety("qac", percent), Variety("qac-AA"))
    spec = replace(STUB, varieties=varieties, recognizers=(*STUB.recognizers, SHARED["percent"]))
    with pytest.raises(AssertionError, match="qac-AA: no"):
        contract.clause_6("qac", spec)


def test_clause_6_requires_the_keys_of_each_shared_verbalizer():
    """The stub reads cardinals with leads through `speak_cardinal`, which reads `digit_words` for a leading zero."""
    data = freeze({k: v for k, v in thaw(STUB.data).items() if k != "digit_words"})
    assert STUB.verbalizers[Form.CARDINAL] is contract.speak_cardinal and "leads" in data
    with pytest.raises(AssertionError, match="'digit_words'"):
        contract.clause_6("qac", replace(STUB, data=data))


def test_clause_6_requires_no_key_of_a_verbalizer_that_the_file_replaces():
    data = freeze({k: v for k, v in thaw(STUB.data).items() if k != "digit_words"})
    own = {**STUB.verbalizers, Form.CARDINAL: lambda span, context: span.fields["digits"]}
    contract.clause_6("qac", replace(STUB, data=data, verbalizers=own))


def test_clause_6_admits_a_file_with_none_of_the_optional_keys():
    data = freeze({**thaw(STUB.data), "range_word": "al", "time_words": ["je"], "day_periods": {"am": ["am"]},
                   "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"},
                                   {"mark": "h", "seconds": False, "needs": "none", "closes_hour": True}]})
    readers = (SHARED["decimal"], SHARED["date_numeric"], SHARED["time_clock"])
    spec = replace(STUB, data=data, recognizers=(*STUB.recognizers, *readers))
    assert OPTIONAL <= set().union(*(READERS[r.name] for r in readers)) and not OPTIONAL & set(spec.data)
    contract.clause_6("qac", spec)


def _data_reads(source: str) -> set[str]:
    """The string keys that a source reads from `data`, `request.data` or `merged_data(...)`."""
    def is_data(node) -> bool:
        return ((isinstance(node, ast.Name) and node.id == "data")
                or (isinstance(node, ast.Attribute) and node.attr == "data")
                or (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "merged_data"))

    keys = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Subscript) and is_data(node.value) and isinstance(node.slice, ast.Constant):
            keys.add(node.slice.value)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
              and is_data(node.func.value) and node.args and isinstance(node.args[0], ast.Constant)):
            keys.add(node.args[0].value)
    return keys


def test_the_declared_keys_are_the_keys_the_core_reads():
    core = files("text2spoken.core")
    read = set().union(*(_data_reads(e.read_text(encoding="utf-8")) for e in core.iterdir() if e.name.endswith(".py")))
    assert set(SHAPES) == read == set().union(*READERS.values())


def test_each_reader_is_a_shared_recognizer_or_a_named_core_reader():
    assert set(READERS) - {*contract.SHARED_VERBALIZERS, "render", "effective_params"} == set(SHARED)


class _Recorder(FrozenMap):
    __slots__ = ("keys",)

    def __getitem__(self, key):
        self.keys.add(key)
        return super().__getitem__(key)


def test_each_shared_recognizer_reads_only_its_declared_keys(monkeypatch):
    """A recording run over the rows of each language file, for the shared recognizers that the files use."""
    read: dict[str, set[str]] = {name: set() for name in SHARED}
    used = set()
    data = Request.data.fget

    def recording(request):
        recorder = _Recorder(data(request))
        recorder.keys = read[request.memo["recognizer"]]
        return recorder

    monkeypatch.setattr(Request, "data", property(recording))
    for code in FILES:
        for row in rows(code):
            tag, language, variety = select(row["tag"])
            tokens = default_tokenizer(row["text"], tag)
            for name, recognizer in SHARED.items():
                if recognizer in language.recognizers:
                    used.add(name)
                    request = Request(tag, variety, language, NormalizationParams(), memo={"recognizer": name})
                    list(recognizer.find(row["text"], tokens, request))
    for name, keys in read.items():
        assert keys <= READERS[name], f"{name} reads {sorted(keys - READERS[name])}, which it does not declare"
    assert set().union(*read.values()) == set().union(*(READERS[name] for name in used))


@pytest.mark.parametrize("pattern", [r"\d+", r"[0-9]\b", r"\w", r"\s", r"(a)\1", "(?i)ab", "(?=a)", "(?<=a)b",
                                     "(?P<n>a)", r"\D", r"\S", r"\W", r"\B"])
def test_clause_7_bites(en, pattern):
    with pytest.raises(AssertionError):
        contract.clause_7("en", replace(en, data=freeze({**en.data, "patterns": {"bad": pattern}})))


@pytest.mark.parametrize("pattern", [r"\d{3}-\d{4}", r"[0-9]{3}\b", "(?i)tel"])
def test_clause_7_checks_phone_shapes(pattern):
    with pytest.raises(AssertionError):
        contract.clause_7("qac", replace(STUB, data=freeze({**thaw(STUB.data), "phone_shapes": [pattern]})))
    with pytest.raises(AssertionError):
        contract.clause_7("qac", replace(STUB, varieties=(Variety("qac", freeze({"phone_shapes": [pattern]})),)))


@pytest.mark.parametrize("pattern", ["[0-9]+", "(?:ab)+", "(a|b)", "[0-9٠-٩]"])
def test_clause_7_admits_the_subset(pattern):
    contract.check_pattern(pattern)


def test_clause_8_bites(en):
    with pytest.raises(AssertionError):
        contract.clause_8("en", replace(en, not_applicable=en.not_applicable | {"clock"}))
    with pytest.raises(AssertionError):
        contract.clause_8("en", replace(en, not_applicable=en.not_applicable - {"register"}))
    with pytest.raises(AssertionError):
        contract.clause_8("en", replace(en, data=freeze({**en.data, "defaults": {}})))


class _SameWords:
    def cardinal(self, digits, features, request):
        return "un"


def test_clause_9_passes_on_a_gendered_file(gendered):
    contract.clause_9("qaa", gendered.LANGUAGE, expected_cells=["Tenho uma casa e um carro."])


def test_clause_9_bites(gendered):
    with pytest.raises(AssertionError):
        contract.clause_9("qaa", replace(gendered.LANGUAGE, spellers={Form.CARDINAL: _SameWords()}),
                          expected_cells=["un"])
    with pytest.raises(AssertionError, match="no row holds"):
        contract.clause_9("qaa", gendered.LANGUAGE, expected_cells=["Tenho um carro."])


def test_clause_10_bites(monkeypatch, en):
    broken = replace(en, context_words=False)
    monkeypatch.setattr(loader, "_registry", lambda: {"en": broken})
    with pytest.raises(AssertionError):
        contract.clause_10("en", broken)


def test_clause_11_bites(en):
    typo = RbnfSpeller(cardinal={Features(): "spellout-cardinal-typo"}, ordinal={Features(): "spellout-ordinal"})
    with pytest.raises(AssertionError):
        contract.clause_11("en", replace(en, spellers={Form.CARDINAL: typo}))
    with pytest.raises(AssertionError):
        contract.clause_11("en", replace(en, code="tlh", varieties=(Variety("tlh"),)))


@pytest.mark.parametrize("source", ["import requests\n", "import tugalex\n", "from orthography2ipa import x\n",
                                    "def f():\n    import scriptconv\n"])
def test_clause_12_bites(en, source):
    with pytest.raises(AssertionError):
        contract.clause_12("en", en, source=source)


@pytest.mark.parametrize("source", ["def f():\n    import ovos_number_parser\n", "def f():\n    import tugalex\n",
                                    "import ovos_color_parser\n", "def f():\n    from ovos_date_parser import x\n"])
def test_clause_12_bites_on_an_undeclared_dependency(source):
    with pytest.raises(AssertionError, match="does not hold"):
        contract.clause_12("qac", STUB, source=source)


def test_clause_12_admits_no_other_extra():
    source = "def f():\n    import tugalex\n"
    with pytest.raises(AssertionError, match="does not hold"):
        contract.clause_12("qac", STUB, source=source, requirements=['tugalex; extra == "pt"'])
    with pytest.raises(AssertionError, match="does not hold"):
        contract.clause_12("qac", STUB, source=source, requirements=['tugalex; extra == "test"'])
    with pytest.raises(AssertionError, match="does not hold"):
        contract.clause_12("qac", STUB, source="import linguatag\n", requirements=['linguatag; extra == "qac"'])


OVOS_SOURCE = "from text2spoken.core.spellers import OvosNumberSpeller\nSPELLER = OvosNumberSpeller({})\n"


def test_clause_12_checks_the_dependency_of_each_core_speller():
    """The stub names OvosNumberSpeller, so the import of ovos_number_parser lives in the core, not in the file."""
    spec = replace(STUB, spellers={Form.CARDINAL: OvosNumberSpeller({})})
    with pytest.raises(AssertionError, match="ovos-number-parser"):
        contract.clause_12("qac", spec, source=OVOS_SOURCE)
    with pytest.raises(AssertionError, match="ovos-number-parser"):
        contract.clause_12("qac", spec, source=OVOS_SOURCE, requirements=['ovos-number-parser; extra == "pt"'])
    contract.clause_12("qac", spec, source=OVOS_SOURCE, requirements=['ovos-number-parser; extra == "qac"'])


class _ByVariety:
    def __init__(self, speller):
        self.spellers = {"qac": speller}


RBNF = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})


@pytest.mark.parametrize(("speller", "distribution"), [(OvosNumberSpeller({}), "ovos-number-parser"),
                                                       (RBNF, "unicode-rbnf")])
def test_clause_12_finds_a_core_speller_inside_a_speller(speller, distribution):
    spec = replace(STUB, spellers={Form.CARDINAL: _ByVariety(speller)})
    with pytest.raises(AssertionError, match=distribution):
        contract.clause_12("qac", spec, source=OVOS_SOURCE, requirements=[])
    contract.clause_12("qac", spec, source=OVOS_SOURCE, requirements=[distribution])


def test_clause_12_admits_a_lazy_extra(en):
    extra = [*requires("text2spoken"), 'tugalex; extra == "en"']
    contract.clause_12("en", en, source="import re\nfrom text2spoken.core import spans\ndef f():\n    import tugalex\n",
                       requirements=extra)
    contract.clause_12("qac", STUB, source="import linguatag\ndef f():\n    import ovos_number_parser\n",
                       requirements=["linguatag", 'ovos-number-parser>=0.24; extra == "qac"'])


def test_clause_12_sandbox_sees_a_file_read_and_a_new_module(tmp_path):
    import os
    import sys

    (tmp_path / "reads_a_file.py").write_text("import csv\nopen(__file__.replace('.py', '.txt'), 'w').close()\n")
    events, added = contract.sandbox_import("reads_a_file", str(tmp_path / "__pycache__"),
                                            path=os.pathsep.join([str(tmp_path), *sys.path]))
    assert any(e.startswith("open ") and e.endswith("reads_a_file.txt") for e in events)
    assert "csv" in added
