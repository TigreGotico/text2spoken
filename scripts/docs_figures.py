"""Write the figures of docs/img/, or check that the committed files are current.

Usage:
    python scripts/docs_figures.py            run each docs/img/plot_*.py
    python scripts/docs_figures.py --check    exit 1 when a committed figure differs from a fresh one
    python scripts/docs_figures.py --measure  run the timing again, write docs/img/timing.json, then write each figure

Each docs/img/plot_<name>.py writes <name>.svg and <name>-dark.svg from the repository's own data. The SVG holds
no date and no random value, so a fresh run of the same inputs gives the same bytes.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "img"
TIMING = IMG / "timing.json"

TIMING_SENTENCE = "Dr Smith paid £3.50 for 2 tickets on 14 March 2024 at 7:30 pm. "
TIMING_REPEATS = (1, 2, 4, 8, 16, 32, 64, 128, 256)
TIMING_TAG = "en-GB"


def measure() -> dict:
    from text2spoken import normalize

    normalize(TIMING_SENTENCE, TIMING_TAG)
    points = []
    for repeats in TIMING_REPEATS:
        sample = TIMING_SENTENCE * repeats
        seconds = []
        for _ in range(5):
            start = time.perf_counter()
            normalize(sample, TIMING_TAG)
            seconds.append(time.perf_counter() - start)
        points.append({"characters": len(sample), "milliseconds": round(min(seconds) * 1000, 1)})
    return {"tag": TIMING_TAG, "sentence": TIMING_SENTENCE, "points": points}


def main(argv: list[str]) -> int:
    if "--measure" in argv:
        TIMING.write_text(json.dumps(measure(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in IMG.glob("*.svg")}
    for script in sorted(IMG.glob("plot_*.py")):
        if script.name != "plot_style.py":
            subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    if "--check" in argv:
        stale = [path.name for path in sorted(IMG.glob("*.svg")) if before.get(path) != path.read_bytes()]
        if stale:
            print(f"stale: {', '.join(stale)}; run python scripts/docs_figures.py", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
