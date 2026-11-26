"""docs/img/time-by-length.svg: the time of `normalize` against the length of the text.

    python docs/img/plot_time_by_length.py

The points come from docs/img/timing.json, which `python scripts/docs_figures.py --measure` writes.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import save  # noqa: E402

TIMING = Path(__file__).with_name("timing.json")


def draw(fig, theme, data):
    xs = [p["characters"] for p in data["points"]]
    ys = [p["milliseconds"] for p in data["points"]]
    slope = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
    ax = fig.subplots()
    ax.plot([0, max(xs)], [0, slope * max(xs)], color=theme["series"][1], linestyle="--", linewidth=1.5,
            label=f"straight line from 0, {slope * 1000:.1f} ms per 1,000 characters")
    ax.plot(xs, ys, color=theme["series"][0], marker="o", label=f"measured, {data['tag']}")
    ax.set_xlabel("Characters in the text")
    ax.set_ylabel("Milliseconds")
    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.set_title("Time of normalize against the length of the text")
    ax.legend(loc="upper left")


if __name__ == "__main__":
    save("docs/img/time-by-length", draw, json.loads(TIMING.read_text(encoding="utf-8")))
