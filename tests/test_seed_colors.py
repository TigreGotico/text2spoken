"""The colour table of en.py is the output of scripts/seed_colors.py (design section 12)."""
import runpy
from pathlib import Path

from text2spoken.lang.en import COLORS, DATA, VARIETIES


def test_the_english_table_is_the_seed_output():
    seed = runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "seed_colors.py"))["seed"]
    table, _ = seed("en")
    assert COLORS == table and DATA["colors"] == table


def test_the_british_variety_writes_grey():
    gb = dict(VARIETIES[0].data["colors"])
    assert VARIETIES[0].tag == "en-GB" and gb["808080"] == "grey" and all("gray" not in name for name in gb.values())
