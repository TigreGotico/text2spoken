"""Write the data figures of docs/ as SVG files, or check that the committed files are current.

Usage:
    python scripts/docs_figures.py            write each figure
    python scripts/docs_figures.py --check    exit 1 when a committed figure differs from a fresh one
    python scripts/docs_figures.py --measure  run the timing again, write docs/figures/timing.json, then write each figure

Inputs:
    tests/data/<code>.tsv      rows per language, and the rows whose source holds the word `silver`
    supports(code).forms       the forms that each language file reads
    docs/figures/timing.json   the timing of `normalize` against the length of the text (`--measure` writes it)

Outputs, in docs/figures/: rows-per-language.svg, forms-per-language.svg, time-by-length.svg.
The SVG text holds no date and no random value, so a fresh run of the same inputs gives the same bytes.
"""
import csv
import json
import re
import sys
import time
from pathlib import Path

from text2spoken import Form, normalize, supports

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "data"
FIGURES = ROOT / "docs" / "figures"
TIMING = FIGURES / "timing.json"

INK = "#707880"
CITED = "#4a8fd9"
SILVER = "#e08e3c"
GRID = "#9aa0a6"
FONT = 'font-family="DejaVu Sans, Verdana, sans-serif" font-size="15"'

TIMING_SENTENCE = "Dr Smith paid £3.50 for 2 tickets on 14 March 2024 at 7:30 pm. "
TIMING_REPEATS = (1, 2, 4, 8, 16, 32, 64, 128, 256)
TIMING_TAG = "en-GB"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(width: int, height: int, title: str, description: str, body: list[str]) -> str:
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">\n'
            f'<title id="title">{esc(title)}</title>\n<desc id="description">{esc(description)}</desc>\n')
    return head + "\n".join(body) + "\n</svg>\n"


def text(x: float, y: float, content: str, anchor: str = "start", extra: str = "") -> str:
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" fill="{INK}" {FONT}{extra}>{esc(content)}</text>'


def language_codes() -> list[str]:
    return sorted(path.stem for path in DATA.glob("*.tsv"))


def row_counts() -> dict[str, tuple[int, int]]:
    """For each language code, the rows that cite a source and the rows marked `silver` in the source column."""
    counts = {}
    for code in language_codes():
        with open(DATA / f"{code}.tsv", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE))
        silver = sum(bool(re.search(r"\bsilver\b", row["source"])) for row in rows)
        counts[code] = (len(rows) - silver, silver)
    return counts


def rows_figure() -> str:
    counts = row_counts()
    order = sorted(counts, key=lambda code: (-sum(counts[code]), code))
    names = {code: code for code in order}
    total = sum(map(sum, counts.values()))
    silver = sum(silver for _, silver in counts.values())
    left, top, bar, gap, scale = 60, 20, 22, 8, 0.6
    width = left + int(max(sum(counts[code]) for code in order) * scale) + 150
    height = top + len(order) * (bar + gap) + 50
    body = []
    for index, code in enumerate(order):
        cited, silvered = counts[code]
        y = top + index * (bar + gap)
        body.append(text(left - 10, y + 17, names[code], "end"))
        body.append(f'<rect x="{left}" y="{y}" width="{cited * scale:g}" height="{bar}" fill="{CITED}"/>')
        if silvered:
            body.append(f'<rect x="{left + cited * scale:g}" y="{y}" width="{silvered * scale:g}" height="{bar}" '
                        f'fill="{SILVER}"/>')
        label = f"{cited + silvered}" + (f", {silvered} silver" if silvered else "")
        body.append(text(left + (cited + silvered) * scale + 8, y + 17, label))
    legend_y = height - 14
    body.append(f'<rect x="{left}" y="{legend_y - 12}" width="14" height="14" fill="{CITED}"/>')
    body.append(text(left + 20, legend_y, "reading from a cited source"))
    body.append(f'<rect x="{left + 250}" y="{legend_y - 12}" width="14" height="14" fill="{SILVER}"/>')
    body.append(text(left + 270, legend_y, "silver: no source holds the reading"))
    description = (f"Horizontal bars of test rows for {len(order)} languages, {total} rows in all, "
                   f"{total - silver} with a cited source and {silver} marked silver. "
                   + "; ".join(f"{names[code]} {sum(counts[code])}" for code in order) + ".")
    return svg(width, height, "Test rows per language", description, body)


def form_matrix() -> tuple[list[str], list[Form], dict[str, frozenset[Form]]]:
    codes = language_codes()
    read = {code: supports(code).forms for code in codes}
    forms = [form for form in Form if any(form in forms_of for forms_of in read.values())]
    order = sorted(codes, key=lambda code: (-len(read[code]), code))
    return order, forms, read


def forms_figure() -> str:
    order, forms, read = form_matrix()
    cell, left, top = 26, 60, 150
    width = left + len(forms) * cell + 60
    height = top + len(order) * cell + 20
    body = []
    for column, form in enumerate(forms):
        x = left + column * cell + cell // 2
        body.append(f'<text x="{x}" y="{top - 8}" text-anchor="start" fill="{INK}" {FONT} '
                    f'transform="rotate(-60 {x} {top - 8})">{form.value}</text>')
    for row, code in enumerate(order):
        y = top + row * cell + cell // 2
        body.append(text(left - 10, y + 5, code, "end"))
        for column, form in enumerate(forms):
            x = left + column * cell + cell // 2
            if form in read[code]:
                body.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{CITED}"/>')
            else:
                body.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{GRID}"/>')
        body.append(text(left + len(forms) * cell + 8, y + 5, str(len(read[code]))))
    description = (f"Matrix of {len(order)} language files by {len(forms)} forms. "
                   + "; ".join(f"{code} reads {len(read[code])}" for code in order) + ".")
    return svg(width, height, "Forms that each language file reads", description, body)


def measure() -> dict:
    normalize(TIMING_SENTENCE, TIMING_TAG)
    points = []
    for repeats in TIMING_REPEATS:
        sample = TIMING_SENTENCE * repeats
        best = min(_seconds(sample) for _ in range(5))
        points.append({"characters": len(sample), "milliseconds": round(best * 1000, 1)})
    return {"tag": TIMING_TAG, "sentence": TIMING_SENTENCE, "points": points}


def _seconds(sample: str) -> float:
    start = time.perf_counter()
    normalize(sample, TIMING_TAG)
    return time.perf_counter() - start


def timing_figure() -> str:
    data = json.loads(TIMING.read_text(encoding="utf-8"))
    points = data["points"]
    left, top, plot_w, plot_h = 70, 20, 560, 300
    width, height = left + plot_w + 30, top + plot_h + 70
    max_x = max(p["characters"] for p in points)
    max_y = max(p["milliseconds"] for p in points)
    x_top = -(-max_x // 4000) * 4000
    y_top = int(-(-max_y // 200) * 200)
    sx, sy = plot_w / x_top, plot_h / y_top
    body = []
    for step in range(0, y_top + 1, 200):
        y = top + plot_h - step * sy
        body.append(f'<line x1="{left}" y1="{y:g}" x2="{left + plot_w}" y2="{y:g}" stroke="{GRID}" stroke-opacity="0.4"/>')
        body.append(text(left - 8, y + 5, str(step), "end"))
    for step in range(0, x_top + 1, 4000):
        x = left + step * sx
        body.append(f'<line x1="{x:g}" y1="{top}" x2="{x:g}" y2="{top + plot_h}" stroke="{GRID}" stroke-opacity="0.4"/>')
        body.append(text(x, top + plot_h + 22, str(step), "middle"))
    slope = sum(p["characters"] * p["milliseconds"] for p in points) / sum(p["characters"] ** 2 for p in points)
    body.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + max_x * sx:g}" y2="{top + plot_h - slope * max_x * sy:g}" '
                f'stroke="{SILVER}" stroke-width="2" stroke-dasharray="6 5"/>')
    path = " ".join(f"{left + p['characters'] * sx:g},{top + plot_h - p['milliseconds'] * sy:g}" for p in points)
    body.append(f'<polyline points="{path}" fill="none" stroke="{CITED}" stroke-width="2.5"/>')
    for p in points:
        body.append(f'<circle cx="{left + p["characters"] * sx:g}" cy="{top + plot_h - p["milliseconds"] * sy:g}" r="4.5" '
                    f'fill="{CITED}"/>')
    body.append(text(left + plot_w / 2, top + plot_h + 50, "characters in the text", "middle"))
    body.append(text(18, top + plot_h / 2, "milliseconds", "middle", f' transform="rotate(-90 18 {top + plot_h / 2:g})"'))
    description = ("Line chart of the time of normalize against the length of the text: "
                   + "; ".join(f"{p['characters']} characters take {p['milliseconds']} ms" for p in points)
                   + ". A dashed straight line from the origin through the mean slope lies on the points.")
    return svg(width, height, "Time of normalize against the length of the text", description, body)


FIGURES_OF = {
    "rows-per-language.svg": rows_figure,
    "forms-per-language.svg": forms_figure,
    "time-by-length.svg": timing_figure,
}


def main(argv: list[str]) -> int:
    if "--measure" in argv:
        TIMING.write_text(json.dumps(measure(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    stale = []
    for name, build in FIGURES_OF.items():
        fresh = build()
        path = FIGURES / name
        if "--check" in argv:
            if not path.exists() or path.read_text(encoding="utf-8") != fresh:
                stale.append(name)
        else:
            FIGURES.mkdir(exist_ok=True)
            path.write_text(fresh, encoding="utf-8")
            print(f"wrote docs/figures/{name}")
    if stale:
        print(f"stale: {', '.join(stale)}; run python scripts/docs_figures.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
