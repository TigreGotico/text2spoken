"""The CLDR unit data and the symbol rule of design section 4.7, with values read off the rule and the data files."""
import json
import re
import subprocess
import sys
from importlib.resources import files

import pytest

from text2spoken.core.units import no_word
from text2spoken.lang import en, pt

TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR")


def data(tag: str) -> dict:
    return json.loads((files("text2spoken") / "data" / "cldr" / f"{tag}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("symbol", ["km/h", "kWh", "°C", "µm", "μm", "m²", "cm³", "‰", "L/100 km", "mL", "inHg"])
def test_a_symbol_that_cannot_be_a_word_reads_with_no_list(symbol):
    assert no_word(symbol)


@pytest.mark.parametrize("symbol", ["in", "A", "GB", "ms", "ha", "st", "rd", "cup", "l", "MHz", "MB", "°", "%"])
def test_a_symbol_of_letters_or_a_bare_degree_needs_the_list(symbol):
    assert not no_word(symbol)


@pytest.mark.parametrize("tag", TAGS)
def test_each_data_file_records_the_pinned_release_and_its_inputs(tag):
    source = data(tag)["source"]
    assert source["release"] == "49.0.0"
    assert source["commit"] == "a4b67247b446fd51b475991017a2481911210c60"
    assert source["locales"][-1] == "und"
    expected = {"LICENSE", "cldr-json/cldr-core/supplemental/parentLocales.json",
                *(f"cldr-json/cldr-units-full/main/{locale}/units.json" for locale in source["locales"])}
    assert set(source["files"]) == expected
    assert all(re.fullmatch("[0-9a-f]{64}", digest) for digest in source["files"].values())


def test_the_parent_chain_resolves_at_extraction():
    assert data("en-GB")["source"]["locales"] == ["en-GB", "en-001", "en", "und"]
    assert data("pt-PT")["source"]["locales"] == ["pt-PT", "pt", "und"]
    assert data("pt-BR")["source"]["locales"] == ["pt", "und"]


def test_the_licence_ships_with_the_data():
    licence = (files("text2spoken") / "data" / "cldr" / "LICENSE").read_text(encoding="utf-8")
    assert licence.startswith("UNICODE LICENSE V3")


@pytest.mark.parametrize("tag", TAGS)
def test_a_symbol_that_two_units_share_reads_as_neither(tag):
    tables = data(tag)
    owned = {symbol for unit in tables["units"].values() for symbol in unit["symbols"]}
    assert tables["collisions"] and not owned & set(tables["collisions"])
    assert all(len(keys) >= 2 for keys in tables["collisions"].values())


@pytest.mark.parametrize("tag", TAGS)
def test_both_micro_signs_name_the_micrometre(tag):
    assert {"µm", "μm"} <= set(data(tag)["units"]["length-micrometer"]["symbols"])


@pytest.mark.parametrize("module", [en, pt])
def test_each_listed_symbol_is_made_of_letters_and_is_a_cldr_symbol(module):
    listed = module.DATA["unit_symbols"]
    symbols = {s for v in module.VARIETIES for u in data(v.tag)["units"].values() for s in u["symbols"]}
    assert all(not no_word(symbol) for symbol in listed)
    assert set(listed) <= symbols
    assert not {"in", "A", "GB", "ms", "ha", "st", "rd", "cup", "l"} & set(en.DATA["unit_symbols"])


def test_the_data_loads_on_first_use_of_each_variety():
    script = ("import text2spoken.lang.en\n"
              "from text2spoken import normalize\n"
              "from text2spoken.core.units import cldr_data\n"
              "before = cldr_data.cache_info().currsize\n"
              "normalize('It weighs 10 kg.', 'en-GB')\n"
              "print(before, cldr_data.cache_info().currsize)\n")
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
    assert result.stdout.split() == ["0", "1"]


@pytest.mark.parametrize("module", [en, pt])
def test_only_a_listed_symbol_reads_through_a_case_match(module):
    from text2spoken.core.language import Request, select
    from text2spoken.core.units import unit_table
    from text2spoken.params import NormalizationParams

    for variety in module.VARIETIES:
        tag, language, chosen = select(variety.tag)
        table = unit_table(Request(tag, chosen, language, NormalizationParams()))
        written = {s for u in data(variety.tag)["units"].values() for s in u["symbols"]}
        assert set(table) - written <= set(module.DATA["unit_symbols"])


def test_a_case_match_takes_the_symbol_with_the_fewest_case_changes():
    """en-US writes `mL` for the millilitre and `ML` for the megalitre, so the listed `ml` reads as `mL`."""
    symbols = {s: key for key, u in data("en-US")["units"].items() for s in u["symbols"]}
    assert symbols["mL"] == "volume-milliliter" and symbols["ML"] == "volume-megaliter" and "ml" not in symbols


def test_a_unit_whose_name_holds_a_digit_reads_no_symbol():
    """CLDR en names `L/100 km` "{0} liters per 100 kilometers". Read, a second pass would read the 100 again."""
    from text2spoken import normalize

    once = normalize("It uses 5 L/100 km.", "en-US")
    assert once == "It uses five L/one hundred kilometers."
    assert normalize(once, "en-US") == once


def test_a_feminine_unit_takes_the_feminine_power_pattern():
    """CLDR pt-PT: duration-hour `{0} horas`, gender feminine; power2 feminine `{0} quadradas`."""
    from text2spoken import normalize

    assert normalize("A área é 2 h².", "pt-PT") == "A área é duas horas quadradas."


def test_a_power_after_a_slash_squares_the_denominator():
    """`km/h²` is kilometres per square hour: CLDR pt-PT `{0} quilómetros`, per `{0} por {1}`, duration-hour one
    `{0} hora`, power2 feminine one `{0} quadrada`. A square of the whole `km/h` would read "por hora quadrados"."""
    from text2spoken import normalize

    assert normalize("Acelera 5 km/h².", "pt-PT") == "Acelera cinco quilómetros por hora quadrada."


def test_a_case_match_with_two_equal_candidates_reads_no_unit():
    """en-US writes `cd` for the candela and `CD` for the carat. A listed `Cd` differs from each in one letter, so
    it reads neither, while a listed `ml` differs from `mL` in one letter and from `ML` in two, so it reads `mL`."""
    from text2spoken.core.units import _cldr_table

    symbols = {s for u in data("en-US")["units"].values() for s in u["symbols"]}
    assert {"cd", "CD"} <= symbols and "Cd" not in symbols
    assert "Cd" not in _cldr_table("en-US", ("Cd",))
    assert _cldr_table("en-US", ("ml",))["ml"]["names"]["other"] == "{0} milliliters"
