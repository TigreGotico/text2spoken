"""Write the figures of docs/img/, or check that the committed files are current.

Usage:
    python scripts/docs_figures.py            run each docs/img/plot_*.py
    python scripts/docs_figures.py --check    exit 1 when the data of a committed figure differs from a fresh read
    python scripts/docs_figures.py --measure  run the timing again, write docs/img/timing.json, then write each figure

Each docs/img/plot_<name>.py writes <name>.json, the values it draws, then <name>.svg and <name>-dark.svg. The check
compares the JSON only and needs no matplotlib, because the SVG bytes move between matplotlib versions.
"""
import json
import os
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
    return {"tag": TIMING_TAG, "sentence": TIMING_SENTENCE, "cpu": cpu(), "points": points}


def cpu() -> str:
    """The CPU model name from /proc/cpuinfo, or the platform processor string."""
    import platform
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as info:
            return next(line.split(":", 1)[1].strip() for line in info if line.startswith("model name"))
    except (OSError, StopIteration):
        return platform.processor() or platform.machine()


def main(argv: list[str]) -> int:
    if "--measure" in argv:
        TIMING.write_text(json.dumps(measure(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    check = "--check" in argv
    before = {path: path.read_bytes() for path in IMG.glob("*.json") if path != TIMING}
    env = {**os.environ, "DOCS_FIGURES_DATA_ONLY": "1"} if check else None
    for script in sorted(IMG.glob("plot_*.py")):
        if script.name != "plot_style.py":
            subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, env=env)
    if check:
        stale = [path.name for path in sorted(IMG.glob("*.json"))
                 if path != TIMING and before.get(path) != path.read_bytes()]
        if stale:
            print(f"stale: {', '.join(stale)}; run python scripts/docs_figures.py", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
