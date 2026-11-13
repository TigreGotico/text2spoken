"""Write the CLDR unit, currency and symbol data of each variety tag to `text2spoken/data/cldr/`.

    python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
    python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release

The script reads the `cldr-units-full`, `cldr-numbers-full`, `cldr-annotations-full`,
`cldr-annotations-derived-full` and `cldr-core` packages of cldr-json at the pinned tag and commit. It resolves
the CLDR parent chain of each tag (`pt-PT` to `pt` to `und`, `en-GB` to `en-001` to `en` to `und`), so the runtime
reads one file and does no inheritance. Each data file records the release, the commit, the locale chain and the
sha256 of each input file. It writes three files for each tag: `<tag>.json` with the units, `<tag>.currencies.json`
and `<tag>.symbols.json`.

A unit holds its `long` patterns by plural category, its grammatical gender when CLDR gives one, its per-unit
pattern, and its written symbols: the `short` patterns of the locale with `{0}` removed. A symbol that two units
share in one locale is left out, and the script prints each such symbol. A micro sign, `U+00B5` or `U+03BC`, is
written both ways. The `compound` key holds the `per`, `power2` and `power3` patterns.

A currency holds its display names by plural category and the symbols that read as it: its `symbol`, its
narrow symbol and its variant symbol. A symbol that two currencies share in one locale, such as the narrow `$`,
reads as the currency whose `symbol` it is. When no currency or two currencies hold it as their `symbol`, it is
left out, and the script prints it.

A symbol holds the `tts` name of the annotations of the locale, from `cldr-annotations-full` and
`cldr-annotations-derived-full`. The file holds each single character outside ASCII whose general category is
`Sm`, `Sc`, `Sk` or `So`, or that is one of `§ ¶ † ‡ • ‰ ‱`, and that is no emoji with emoji presentation by
default (design section 4.7). The general category and the emoji property come from the Unicode Character Database
of the Unicode version of the release, `UnicodeData.txt` and `emoji/emoji-data.txt`, which the script fetches from
unicode.org or reads from `--ucd`.

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
UNICODE = "16.0.0"
UCD = f"https://www.unicode.org/Public/{UNICODE}/ucd/"
TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR")
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "cldr"
MICRO = ("µ", "μ")
COMPOUNDS = ("per", "power2", "power3")
SYMBOL_FIELDS = ("symbol", "symbol-alt-narrow", "symbol-alt-variant")
SYMBOL_CATEGORIES = ("Sm", "Sc", "Sk", "So")
SYMBOL_MARKS = "§¶†‡•‰‱"


class Source:
    """The files of the pinned cldr-json release, from a local checkout or from GitHub, with their sha256."""

    def __init__(self, root: Path | None, base: str = RAW):
        self.root = root
        self.base = base
        self.hashes: dict[str, str] = {}

    def read(self, path: str) -> bytes | None:
        if self.root is not None:
            file = self.root / path
            blob = file.read_bytes() if file.is_file() else None
        else:
            try:
                with urllib.request.urlopen(self.base + path, timeout=60) as response:
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


def currencies_path(locale: str) -> str:
    return f"cldr-json/cldr-numbers-full/main/{locale}/currencies.json"


def annotations_paths(locale: str) -> tuple[str, str]:
    return (f"cldr-json/cldr-annotations-full/annotations/{locale}/annotations.json",
            f"cldr-json/cldr-annotations-derived-full/annotationsDerived/{locale}/annotations.json")


def _part(source: Source, path: str, *keys: str) -> dict | None:
    """The part of a JSON file of the release under the keys, or None when the release does not hold the file."""
    blob = source.read(path)
    if blob is None:
        return None
    data = json.loads(blob)
    for key in keys:
        data = data[key]
    return data


def _units(source: Source, locale: str) -> dict | None:
    return _part(source, units_path(locale), "main", locale, "units")


def _currencies(source: Source, locale: str) -> dict | None:
    return _part(source, currencies_path(locale), "main", locale, "numbers", "currencies")


def _annotations(source: Source, locale: str) -> dict | None:
    """The annotations of the locale, from the plain and the derived file. The derived file adds sequences, such
    as an emoji with a skin tone, and the names of some currency signs."""
    plain_path, derived_path = annotations_paths(locale)
    plain = _part(source, plain_path, "annotations")
    derived = _part(source, derived_path, "annotationsDerived")
    if plain is None and derived is None:
        return None
    return {**(derived or {}).get("annotations", {}), **(plain or {}).get("annotations", {})}


def chain(tag: str, parents: dict[str, str], source: Source, read=_units) -> list[tuple[str, dict]]:
    """The locales of the CLDR parent chain of the tag that the release holds, from the tag to `und`, each with
    the data that `read` gives: by default its `units` data."""
    found, locale = [], tag
    while True:
        data = read(source, locale)
        if data is not None:
            found.append((locale, data))
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


def extract_currencies(tag: str, parents: dict[str, str], source: Source, shared: dict[str, str]) -> tuple[dict, dict]:
    source.hashes = dict(shared)
    locales = chain(tag, parents, source, _currencies)
    resolved: dict[str, dict] = {}
    for _, currencies in reversed(locales):
        for code, entry in currencies.items():
            resolved[code] = {**resolved.get(code, {}), **entry}
    owners: dict[str, dict[str, bool]] = {}
    for code, entry in resolved.items():
        for field in SYMBOL_FIELDS:
            if field in entry:
                main = owners.setdefault(entry[field], {}).get(code, False)
                owners[entry[field]][code] = main or field == "symbol"
    assigned, collisions = {}, {}
    for symbol, codes in sorted(owners.items()):
        main = [code for code, is_main in codes.items() if is_main]
        if len(codes) == 1 or len(main) == 1:
            assigned[symbol] = main[0] if len(main) == 1 else next(iter(codes))
        else:
            collisions[symbol] = sorted(codes)
    currencies = {}
    for code, entry in sorted(resolved.items()):
        names = counted(entry, "displayName") or ({"other": entry["displayName"]} if "displayName" in entry else {})
        if names:
            currencies[code] = {"names": names,
                                "symbols": sorted(symbol for symbol, owner in assigned.items() if owner == code)}
    data = {
        "source": {"release": RELEASE, "commit": COMMIT, "locales": [locale for locale, _ in locales],
                   "files": dict(sorted(source.hashes.items()))},
        "currencies": currencies,
        "collisions": collisions,
    }
    return data, collisions


def unicode_properties(ucd: Source) -> tuple[dict[str, str], frozenset[str]]:
    """The general category of each character, and the characters with emoji presentation by default."""
    data, emoji = ucd.read("UnicodeData.txt"), ucd.read("emoji/emoji-data.txt")
    if data is None or emoji is None:
        raise SystemExit(f"{ucd.root or ucd.base} holds no UnicodeData.txt and emoji/emoji-data.txt")
    categories, first = {}, None
    for line in data.decode("utf-8").splitlines():
        point, name, category = line.split(";")[:3]
        if name.endswith(", First>"):
            first = int(point, 16)
            continue
        for value in range(first if name.endswith(", Last>") else int(point, 16), int(point, 16) + 1):
            categories[chr(value)] = category
    presentation = set()
    for line in emoji.decode("utf-8").splitlines():
        fields = [part.strip() for part in line.split("#")[0].split(";")]
        if len(fields) == 2 and fields[1] == "Emoji_Presentation":
            low, _, high = fields[0].partition("..")
            presentation.update(map(chr, range(int(low, 16), int(high or low, 16) + 1)))
    return categories, frozenset(presentation)


def extract_symbols(tag: str, parents: dict[str, str], source: Source, shared: dict[str, str],
                    categories: dict[str, str], presentation: frozenset[str]) -> dict:
    source.hashes = dict(shared)
    locales = chain(tag, parents, source, _annotations)
    names: dict[str, str] = {}
    for _, annotations in reversed(locales):
        for key, entry in annotations.items():
            if "tts" in entry:
                names[key] = entry["tts"][0]
    symbols = {char: name for char, name in sorted(names.items())
               if len(char) == 1 and not char.isascii() and char not in presentation
               and (categories.get(char) in SYMBOL_CATEGORIES or char in SYMBOL_MARKS)}
    return {
        "source": {"release": RELEASE, "commit": COMMIT, "unicode": UNICODE,
                   "locales": [locale for locale, _ in locales], "files": dict(sorted(source.hashes.items()))},
        "symbols": symbols,
    }


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, help="a checkout of cldr-json at the pinned commit")
    parser.add_argument("--ucd", type=Path, help=f"a copy of the Unicode {UNICODE} character database")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    source = Source(args.source)
    ucd = Source(args.ucd, UCD)
    categories, presentation = unicode_properties(ucd)
    ucd_hashes = {f"ucd/{path}": digest for path, digest in ucd.hashes.items()}
    parents, licence = source.read("cldr-json/cldr-core/supplemental/parentLocales.json"), source.read("LICENSE")
    if parents is None or licence is None:
        parser.error(f"{args.source or RAW} holds no cldr-json release with parentLocales.json and LICENSE")
    parents = json.loads(parents)["supplemental"]["parentLocales"]["parentLocale"]
    shared = dict(source.hashes)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "LICENSE").write_bytes(licence)
    for tag in TAGS:
        data, collisions = extract(tag, parents, source, shared)
        write(args.out / f"{tag}.json", data)
        print(f"{tag}: {len(data['units'])} units, chain {' > '.join(data['source']['locales'])}")
        for symbol, keys in collisions.items():
            print(f"  left out {symbol!r}: {', '.join(keys)}")
        data, collisions = extract_currencies(tag, parents, source, shared)
        write(args.out / f"{tag}.currencies.json", data)
        print(f"{tag}: {len(data['currencies'])} currencies")
        for symbol, codes in collisions.items():
            print(f"  left out {symbol!r}: {', '.join(codes)}")
        data = extract_symbols(tag, parents, source, {**shared, **ucd_hashes}, categories, presentation)
        write(args.out / f"{tag}.symbols.json", data)
        print(f"{tag}: {len(data['symbols'])} symbols")
    return 0


if __name__ == "__main__":
    sys.exit(main())
