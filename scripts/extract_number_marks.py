"""Write the CLDR decimal and group marks of each locale to `text2spoken/data/cldr/number-marks.json`.

    python scripts/extract_number_marks.py                       # fetch the pinned cldr-json release
    python scripts/extract_number_marks.py --source ~/cldr-json  # read a checkout of that release

A language with no file reads its decimal and group marks from this file (design section 6.1). The script reads
`numbers.json` of `cldr-numbers-full` for every locale of `availableLocales.json`, at the release and commit that
`extract_cldr.py` pins, and resolves the CLDR parent chain of each locale. For each locale it keeps the `decimal`
and `group` symbols of three numbering systems: `latn`, the default system and the native system. It keys them by
the ISO 15924 script of the digits, as `text2spoken.core.tokens.digit_script` names them, so the core reads `3.5`
and `३.५` with the marks of their own digits.

The file holds each language under its language subtag, and each other locale, under its CLDR id with `_`, only
when its marks differ from the marks of its language. The runtime reads one file and does no inheritance.
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import cache
from pathlib import Path

from extract_cldr import COMMIT, OUT, RAW, RELEASE, Source, chain, write

SCRIPTS = {
    "latn": "Latn", "arab": "Arab", "arabext": "Arab", "deva": "Deva", "beng": "Beng", "guru": "Guru",
    "gujr": "Gujr", "orya": "Orya", "tamldec": "Taml", "telu": "Telu", "knda": "Knda", "mlym": "Mlym",
    "thai": "Thai", "laoo": "Laoo", "tibt": "Tibt", "mymr": "Mymr", "khmr": "Khmr", "mong": "Mong", "nkoo": "Nkoo",
}
"""The ISO 15924 script of the digits of each CLDR numbering system that `digit_script` tells apart."""


def numbers_path(locale: str) -> str:
    return f"cldr-json/cldr-numbers-full/main/{locale}/numbers.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, help="a checkout of cldr-json at the pinned commit")
    parser.add_argument("--out", type=Path, default=OUT / "number-marks.json")
    args = parser.parse_args(argv)
    source = Source(args.source)

    @cache
    def numbers(_, locale: str) -> dict | None:
        blob = source.read(numbers_path(locale))
        return None if blob is None else json.loads(blob)["main"][locale]["numbers"]

    available = source.read("cldr-json/cldr-core/availableLocales.json")
    parents = source.read("cldr-json/cldr-core/supplemental/parentLocales.json")
    if available is None or parents is None:
        parser.error(f"{args.source or RAW} holds no cldr-json release with availableLocales.json")
    locales = json.loads(available)["availableLocales"]["full"]
    parents = json.loads(parents)["supplemental"]["parentLocales"]["parentLocale"]
    resolved = {}
    for locale in locales:
        fields: dict = {}
        for _, data in reversed(chain(locale, parents, source, numbers)):
            for key, value in data.items():
                fields[key] = {**fields.get(key, {}), **value} if isinstance(value, dict) else value
        systems = ["latn", fields["defaultNumberingSystem"], fields.get("otherNumberingSystems", {}).get("native")]
        marks: dict[str, dict[str, str]] = {}
        for system in dict.fromkeys(s for s in systems if s):
            if system not in SCRIPTS:
                print(f"{locale}: no digit script for the numbering system {system}")
                continue
            symbols = fields[f"symbols-numberSystem-{system}"]
            entry = {"decimal": symbols["decimal"], "group": symbols["group"]}
            script = SCRIPTS[system]
            if script in marks and marks[script] != entry:
                print(f"{locale}: {system} gives {script} other marks, {entry} after {marks[script]}; kept the first")
                continue
            marks[script] = entry
        resolved[locale] = marks
    table = {}
    for locale, marks in sorted(resolved.items()):
        language = locale.split("-")[0]
        if locale == language or marks != resolved.get(language):
            table[locale.replace("-", "_")] = marks
    write(args.out, {"source": {"release": RELEASE, "commit": COMMIT, "files": dict(sorted(source.hashes.items()))},
                     "marks": table})
    print(f"{len(locales)} locales in, {len(resolved)} resolved, {len(table)} written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
