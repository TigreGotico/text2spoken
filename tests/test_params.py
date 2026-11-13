"""NormalizationParams and FrozenMap (design section 2.2)."""
import os
import subprocess
import sys
from dataclasses import fields

import pytest

from text2spoken import Form, FrozenMap, GrammaticalGender, NormalizationParams
from text2spoken.params import DEFAULT_FORMS, OPTIONS, freeze, thaw


def test_frozen_map_is_sorted_hashable_and_a_mapping():
    a = FrozenMap({"b": 1, "a": 2})
    b = FrozenMap([("a", 2), ("b", 1)])
    assert list(a) == ["a", "b"] and a == b and hash(a) == hash(b) and a == {"a": 2, "b": 1}
    assert a["a"] == 2 and len(a) == 2 and "c" not in a
    assert FrozenMap({"a": 1}) != FrozenMap({"a": 2})


def test_frozen_map_keeps_one_value_per_key():
    assert dict(FrozenMap([("a", 1), ("a", 2)])) == {"a": 2}


def test_freeze_and_thaw_round_trip():
    value = {"b": [1, {"c": None}], "a": "x"}
    frozen = freeze(value)
    assert isinstance(frozen["b"], tuple) and isinstance(frozen["b"][1], FrozenMap)
    assert thaw(frozen) == value


def test_params_are_hashable_and_equal_by_value():
    a = NormalizationParams(clock="24h", lexicon=FrozenMap({"en": FrozenMap({"ACME": "acme"})}))
    b = NormalizationParams(clock="24h", lexicon=FrozenMap({"en": FrozenMap({"ACME": "acme"})}))
    assert a == b and hash(a) == hash(b) and {a: 1}[b] == 1


def test_default_reads_every_form_except_letters_and_emoji():
    assert NormalizationParams().forms == DEFAULT_FORMS == frozenset(Form) - {Form.LETTERS, Form.EMOJI}


def test_only_without_and_plus():
    params = NormalizationParams(clock="12h")
    assert params.only(Form.DATE, Form.TIME).forms == {Form.DATE, Form.TIME}
    assert params.without(Form.TELEPHONE).forms == frozenset(Form) - {Form.TELEPHONE, Form.LETTERS, Form.EMOJI}
    assert params.plus(Form.LETTERS, Form.EMOJI).forms == frozenset(Form)
    assert params.only(Form.DATE).plus(Form.LETTERS).forms == {Form.DATE, Form.LETTERS}
    assert params.only(Form.DATE).clock == "12h" and params.plus(Form.LETTERS).clock == "12h"


@pytest.mark.parametrize("kwargs", [{"clock": "13h"}, {"date_order": "DYM"}, {"minute_style": "words"},
                                    {"scale": "medium"}, {"register": "casual"}, {"decimal_mark": ",,"}])
def test_an_unknown_value_raises_value_error(kwargs):
    with pytest.raises(ValueError):
        NormalizationParams(**kwargs)


@pytest.mark.parametrize("kwargs", [{"forms": {Form.DATE}}, {"forms": frozenset({"date"})},
                                    {"default_gender": {"pt": GrammaticalGender.FEMININE}},
                                    {"default_gender": FrozenMap({"pt": "feminine"})},
                                    {"lexicon": FrozenMap({"en": {"A": "a"}})}, {"phone_regions": {"GB"}},
                                    {"strict": 1}])
def test_a_wrong_type_raises_type_error(kwargs):
    with pytest.raises(TypeError):
        NormalizationParams(**kwargs)


def test_options_name_every_field_but_forms_lexicon_and_strict():
    assert set(OPTIONS) == {f.name for f in fields(NormalizationParams)} - {"forms", "lexicon", "strict"}


def test_enum_values_follow_universal_dependencies_names():
    assert [g.value for g in GrammaticalGender] == ["masculine", "feminine", "neuter", "common"]


def test_a_frozen_map_hashes_its_items_once():
    """A FrozenMap keys the lexicon and data caches, so each lookup hashes it: the hash of its items is kept."""
    calls = []

    class Counted:
        def __hash__(self):
            calls.append(1)
            return 7

    table = FrozenMap({"a": Counted()})
    expected = hash((("a", Counted()),))
    calls.clear()
    assert [hash(table) for _ in range(3)] == [expected] * 3
    assert len(calls) == 1


PICKLE_DUMP = """
import pickle, sys
from text2spoken import FrozenMap, NormalizationParams
table = FrozenMap({"New York": "N Y", "acme": "Acme"})
params = NormalizationParams(lexicon=FrozenMap({"en": table}))
hash(table), hash(params)
sys.stdout.write(pickle.dumps((table, params)).hex())
"""

PICKLE_LOAD = """
import json, pickle, sys
from text2spoken import FrozenMap, NormalizationParams
fresh = FrozenMap({"New York": "N Y", "acme": "Acme"})
fresh_params = NormalizationParams(lexicon=FrozenMap({"en": fresh}))
for loaded, new in zip(pickle.loads(bytes.fromhex(sys.stdin.read())), (fresh, fresh_params)):
    print(json.dumps([loaded == new, hash(loaded) == hash(new), loaded in {new}]))
"""


def test_a_frozen_map_from_a_pickle_hashes_as_a_fresh_one_under_another_hash_seed():
    """The hash of a string changes with the hash seed of each process, such as a spawned worker, so a pickle does
    not carry the kept hash: the loaded map and the params that hold it hash as fresh ones."""
    dumped = subprocess.run([sys.executable, "-c", PICKLE_DUMP], capture_output=True, text=True, check=True,
                            env={**os.environ, "PYTHONHASHSEED": "1"}).stdout
    loaded = subprocess.run([sys.executable, "-c", PICKLE_LOAD], input=dumped, capture_output=True, text=True,
                            check=True, env={**os.environ, "PYTHONHASHSEED": "2"}).stdout
    assert loaded == "[true, true, true]\n" * 2
