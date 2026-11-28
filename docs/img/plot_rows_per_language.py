"""docs/img/rows-per-language.svg: the test rows of each language, cited and silver.

    python docs/img/plot_rows_per_language.py

The counts come from tests/data/<code>.tsv. A row is silver when its source column holds the word `silver`.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import save  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "tests" / "data"


def row_counts() -> dict[str, list[int]]:
    counts = {}
    for path in sorted(DATA.glob("*.tsv")):
        with open(path, encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE))
        silver = sum(bool(re.search(r"\bsilver\b", row["source"])) for row in rows)
        counts[path.stem] = [len(rows) - silver, silver]
    return counts


def draw(fig, theme, counts):
    order = sorted(counts, key=lambda code: (sum(counts[code]), code))
    cited = [counts[code][0] for code in order]
    silver = [counts[code][1] for code in order]
    ax = fig.subplots()
    ax.barh(order, cited, color=theme["series"][0], label="reading from a cited source", height=0.7)
    ax.barh(order, silver, left=cited, color=theme["series"][1], label="silver: no source holds the reading",
            height=0.7)
    for y, (c, s) in enumerate(zip(cited, silver)):
        ax.text(c + s + 8, y, f"{c + s}" + (f", {s} silver" if s else ""), va="center", color=theme["text"],
                fontsize=9)
    ax.set_xlabel("Test rows")
    ax.set_xlim(0, max(c + s for c, s in zip(cited, silver)) * 1.25)
    ax.grid(axis="y", visible=False)
    total = sum(cited) + sum(silver)
    ax.set_title(f"{total:,} test rows in {len(order)} languages")
    ax.legend(loc="lower right")


if __name__ == "__main__":
    save("docs/img/rows-per-language", draw, row_counts(), height=5.6)
