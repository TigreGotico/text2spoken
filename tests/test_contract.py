"""Section 5.2: every language file passes each clause, and each clause check fails on a broken file."""
from dataclasses import replace
from importlib import import_module

import pytest

from tests import contract
from tests.contract import CLAUSES, language_files
from text2spoken.core import language as loader
from text2spoken.core.language import Variety
from text2spoken.core.spans import Features
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.params import Form, FrozenMap, GrammaticalGender, freeze

FILES = language_files()


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


@pytest.mark.parametrize("pattern", [r"\d+", r"[0-9]\b", r"\w", r"\s", r"(a)\1", "(?i)ab", "(?=a)", "(?<=a)b",
                                     "(?P<n>a)", r"\D", r"\S", r"\W", r"\B"])
def test_clause_7_bites(en, pattern):
    with pytest.raises(AssertionError):
        contract.clause_7("en", replace(en, data=freeze({**en.data, "patterns": {"bad": pattern}})))


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


def test_clause_12_admits_a_lazy_extra(en):
    contract.clause_12("en", en, source="import re\nfrom text2spoken.core import spans\ndef f():\n    import tugalex\n")


def test_clause_12_sandbox_sees_a_file_read_and_a_new_module(tmp_path):
    import os
    import sys

    (tmp_path / "reads_a_file.py").write_text("import csv\nopen(__file__.replace('.py', '.txt'), 'w').close()\n")
    events, added = contract.sandbox_import("reads_a_file", str(tmp_path / "__pycache__"),
                                            path=os.pathsep.join([str(tmp_path), *sys.path]))
    assert any(e.startswith("open ") and e.endswith("reads_a_file.txt") for e in events)
    assert "csv" in added
