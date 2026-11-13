"""Write the CLDR unit data of each variety tag to `text2spoken/data/cldr/<tag>.json`.

    python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
    python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release

The script reads the `cldr-units-full` and `cldr-core` packages of cldr-json at the pinned tag and commit. It
resolves the CLDR parent chain of each tag (`pt-PT` to `pt` to `und`, `en-GB` to `en-001` to `en` to `und`), so
the runtime reads one file and does no inheritance. Each data file records the release, the commit, the locale
chain and the sha256 of each input file.

A unit holds its `long` patterns by plural category, its grammatical gender when CLDR gives one, its per-unit
pattern, and its written symbols: the `short` patterns of the locale with `{0}` removed. A symbol that two units
share in one locale is left out, and the script prints each such symbol. A micro sign, `U+00B5` or `U+03BC`, is
written both ways. The `compound` key holds the `per`, `power2` and `power3` patterns.

The data is under the Unicode License v3, which the script copies to `text2spoken/data/cldr/LICENSE`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

RELEASE = "49.0.0"
COMMIT = "a4b67247b446fd51b475991017a2481911210c60"
RAW = f"https://raw.githubusercontent.com/unicode-org/cldr-json/{COMMIT}/"
TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR")
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "cldr"
MICRO = ("µ", "μ")
COMPOUNDS = ("per", "power2", "power3")


class Source:
    """The files of the pinned cldr-json release, from a local checkout or from GitHub, with their sha256."""

    def __init__(self, root: Path | None):
        self.root = root
        self.hashes: dict[str, str] = {}

    def read(self, path: str) -> bytes | None:
        if self.root is not None:
            file = self.root / path
            blob = file.read_bytes() if file.is_file() else None
        else:
            try:
                with urllib.request.urlopen(RAW + path, timeout=60) as response:
                    blob = response.read()
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                blob = None
        if blob is not None:
            self.hashes[path] = hashlib.sha256(blob).hexdigest()
        return blob


def units_path(locale: str) -> str:
    return f"cldr-json/cldr-units-full/main/{locale}/units.json"


def chain(tag: str, parents: dict[str, str], source: Source) -> list[tuple[str, dict]]:
    """The locales of the CLDR parent chain of the tag that the release holds, from the tag to `und`, each with
    its `units` data."""
    found, locale = [], tag
    while True:
        blob = source.read(units_path(locale))
        if blob is not None:
            found.append((locale, json.loads(blob)["main"][locale]["units"]))
        if locale == "und":
            return found
        locale = parents.get(locale) or (locale.rsplit("-", 1)[0] if "-" in locale else "und")


def resolve(locales: list[tuple[str, dict]], length: str) -> dict[str, dict]:
    """The entries of one length, with each child field over the field of its parent."""
    resolved: dict[str, dict] = {}
    for _, units in reversed(locales):
        for key, entry in units[length].items():
            resolved[key] = {**resolved.get(key, {}), **entry}
    return resolved


def counted(entry: dict, prefix: str) -> dict[str, str]:
    """The fields `<prefix>-count-<category>` of an entry, by category."""
    return {name.removeprefix(prefix + "-count-"): value for name, value in entry.items()
            if name.startswith(prefix + "-count-") and "-" not in name.removeprefix(prefix + "-count-")}


def written(symbol: str) -> list[str]:
    """The symbol, and the symbol with the other micro sign when it holds one."""
    forms = [symbol]
    for one, other in (MICRO, MICRO[::-1]):
        if one in symbol:
            forms.append(symbol.replace(one, other))
    return forms


def extract(tag: str, parents: dict[str, str], source: Source, shared: dict[str, str]) -> tuple[dict, dict]:
    source.hashes = dict(shared)
    locales = chain(tag, parents, source)
    long, short = resolve(locales, "long"), resolve(locales, "short")
    owners: dict[str, set[str]] = {}
    for key, entry in short.items():
        for pattern in counted(entry, "unitPattern").values():
            for symbol in written(pattern.replace("{0}", "").strip()):
                owners.setdefault(symbol, set()).add(key)
    collisions = {symbol: sorted(keys) for symbol, keys in sorted(owners.items()) if len(keys) > 1}
    units = {}
    for key, entry in sorted(long.items()):
        patterns = counted(entry, "unitPattern")
        if not patterns:
            continue
        unit = {"names": patterns,
                "symbols": sorted(s for s, keys in owners.items() if keys == {key})}
        if "gender" in entry:
            unit["gender"] = entry["gender"]
        if "perUnitPattern" in entry:
            unit["per"] = entry["perUnitPattern"]
        units[key] = unit
    compound = {"per": long["per"]["compoundUnitPattern"],
                "power2": counted(long["power2"], "compoundUnitPattern1"),
                "power3": counted(long["power3"], "compoundUnitPattern1")}
    for power in ("power2", "power3"):
        feminine = {name.removeprefix("compoundUnitPattern1-gender-feminine-count-"): value
                    for name, value in long[power].items()
                    if name.startswith("compoundUnitPattern1-gender-feminine-count-")}
        if feminine:
            compound[power + "_feminine"] = feminine
    data = {
        "source": {"release": RELEASE, "commit": COMMIT, "locales": [locale for locale, _ in locales],
                   "files": dict(sorted(source.hashes.items()))},
        "units": units,
        "compound": compound,
        "collisions": collisions,
    }
    return data, collisions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, help="a checkout of cldr-json at the pinned commit")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    source = Source(args.source)
    parents, licence = source.read("cldr-json/cldr-core/supplemental/parentLocales.json"), source.read("LICENSE")
    if parents is None or licence is None:
        parser.error(f"{args.source or RAW} holds no cldr-json release with parentLocales.json and LICENSE")
    parents = json.loads(parents)["supplemental"]["parentLocales"]["parentLocale"]
    shared = dict(source.hashes)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "LICENSE").write_bytes(licence)
    for tag in TAGS:
        data, collisions = extract(tag, parents, source, shared)
        text = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        (args.out / f"{tag}.json").write_text(text, encoding="utf-8")
        print(f"{tag}: {len(data['units'])} units, chain {' > '.join(data['source']['locales'])}")
        for symbol, keys in collisions.items():
            print(f"  left out {symbol!r}: {', '.join(keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
