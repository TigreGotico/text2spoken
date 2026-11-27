"""Write the CLDR unit, currency and symbol data of each variety tag to `text2spoken/data/cldr/`.

    python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
    python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release

The script reads the `cldr-units-full`, `cldr-numbers-full`, `cldr-annotations-full`,
`cldr-annotations-derived-full` and `cldr-core` packages of cldr-json at the pinned tag and commit. It resolves
the CLDR parent chain of each tag (`pt-PT` to `pt` to `und`, `en-GB` to `en-001` to `en` to `und`), so the runtime
reads one file and does no inheritance. Each data file records the release, the commit, the locale chain and the
sha256 of each input file. It writes four files for each tag: `<tag>.json` with the units, `<tag>.currencies.json`,
`<tag>.symbols.json` and `<tag>.emoji.json`. It also reads
`cldr-dates-full` and writes `<locale>.dates.json` for each locale of `DATE_LOCALES`.

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
`Sm`, `Sc`, `Sk` or `So`, or that is one of `§ ¶ † ‡ •`, and that is no emoji with emoji presentation by
default (design section 4.7). The general category and the emoji property come from the Unicode Character Database
of the Unicode version of the release, `UnicodeData.txt` and `emoji/emoji-data.txt`, which the script fetches from
unicode.org or reads from `--ucd`.

An emoji file maps each sequence of the Unicode emoji files of the same Unicode version, `emoji-sequences.txt` and
`emoji-zwj-sequences.txt`, to its spoken name. The script fetches the files from unicode.org or reads them from
`--emoji`. A key has no U+FE0F, as CLDR keys it. The spoken name is the `tts` name in three steps. First, each quote
mark goes, and each `:`, `,`, `(` and `)` becomes a space. U+2019 between two letters is an apostrophe, so it stays.
Second, `normalize` reads the result with the default params, so pt-PT `polegar para cima: tipo de pele 4` gives
"polegar para cima tipo de pele quatro" and en `1st place medal` gives "first place medal". Third, a result that holds a
character other than a letter, a combining mark, a space, `-`, `'` or U+2019 is no spoken name, so the sequence maps to
null and stays as written, as en `flag: Antigua & Barbuda` and `keycap: #` do. The script prints each such name.

A dates file holds the wide month names of the Gregorian calendar in the format context, the one that a date
pattern uses, and the `long` date pattern. A date with no file reads through them (design section 17.5). The
`DATE_LOCALES` are the languages with no language file whose numbers read through ovos-number-parser or CLDR RBNF.
A locale that the release does not hold gets no file.

The data is under the Unicode License v3, which the script copies to `text2spoken/data/cldr/LICENSE`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
import urllib.request
from pathlib import Path

RELEASE = "49.0.0"
COMMIT = "a4b67247b446fd51b475991017a2481911210c60"
RAW = f"https://raw.githubusercontent.com/unicode-org/cldr-json/{COMMIT}/"
UNICODE = "17.0.0"
UCD = f"https://www.unicode.org/Public/{UNICODE}/ucd/"
EMOJI = f"https://www.unicode.org/Public/{UNICODE}/emoji/"
EMOJI_FILES = ("emoji-sequences.txt", "emoji-zwj-sequences.txt")
SELECTOR = "\ufe0f"
TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR", "ca-ES", "ca-AD", "ca-ES-valencia", "it-IT", "it-CH", "it-SM", "nl-NL", "nl-BE",
        "nl-SR", "zh-CN", "zh-TW")
LIKELY_SCRIPT = {"zh-TW": "zh-Hant-TW"}
"""The tags whose CLDR locale holds a script that the tag leaves out, by CLDR 49 likelySubtags.json: `"zh-TW":
"zh-Hant-TW"`. The parent chain of such a tag starts at the locale with the script, so zh-TW reads zh-Hant and not
zh."""
DATE_LOCALES = (
    "af", "ak", "am", "an", "ast", "az", "be", "bg", "bs", "ca", "ccp", "chr", "cs", "cy", "da", "ee", "eo", "et",
    "fa", "ff", "fi", "fil", "fo", "fy", "ga", "gl", "he", "hi", "hr", "hu", "hy", "id", "is", "ja", "ka", "kab",
    "kk", "kl", "km", "ko", "ky", "lb", "lo", "lrc", "lt", "lv", "mk", "ms", "mt", "mwl", "my", "nb", "ne", "nn",
    "no", "oc", "pl", "qu", "ro", "se", "sk", "sl", "sq", "sr", "su", "sv", "sw", "ta", "th", "tr", "uk", "vec",
    "vi", "yue", "zh", "zu")
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "cldr"
MICRO = ("µ", "μ")
COMPOUNDS = ("per", "power2", "power3")
SYMBOL_FIELDS = ("symbol", "symbol-alt-narrow", "symbol-alt-variant")
SYMBOL_CATEGORIES = ("Sm", "Sc", "Sk", "So")
SYMBOL_MARKS = "§¶†‡•"


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


def dates_path(locale: str) -> str:
    return f"cldr-json/cldr-dates-full/main/{locale}/ca-gregorian.json"


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


def _gregorian(source: Source, locale: str) -> dict | None:
    return _part(source, dates_path(locale), "main", locale, "dates", "calendars", "gregorian")


def chain(tag: str, parents: dict[str, str], source: Source, read=_units) -> list[tuple[str, dict]]:
    """The locales of the CLDR parent chain of the tag that the release holds, from the tag, or its locale in
    `LIKELY_SCRIPT`, to `und`, each with the data that `read` gives: by default its `units` data."""
    found, locale = [], LIKELY_SCRIPT.get(tag, tag)
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


def extract_dates(locale: str, parents: dict[str, str], source: Source, shared: dict[str, str]) -> dict | None:
    """The wide format month names and the long date pattern of the locale, each from the first locale of its
    parent chain that holds it; None when the release holds no file for the locale itself."""
    source.hashes = dict(shared)
    locales = chain(locale, parents, source, _gregorian)
    if not locales or locales[0][0] != locale:
        return None
    wide = next(data["months"]["format"]["wide"] for _, data in locales
                if "wide" in data.get("months", {}).get("format", {}))
    long = next(data["dateFormats"]["long"] for _, data in locales if "long" in data.get("dateFormats", {}))
    return {"source": {"release": RELEASE, "commit": COMMIT, "locales": [name for name, _ in locales],
                       "files": dict(sorted(source.hashes.items()))},
            "months": [wide[str(month)] for month in range(1, 13)], "long": long}


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


def _tts_names(tag: str, parents: dict[str, str], source: Source,
               shared: dict[str, str]) -> tuple[list[tuple[str, dict]], dict[str, str]]:
    """The annotation locales of a tag, and the first `tts` name of each key, the nearest locale winning."""
    source.hashes = dict(shared)
    locales = chain(tag, parents, source, _annotations)
    names: dict[str, str] = {}
    for _, entries in reversed(locales):
        for key, entry in entries.items():
            if "tts" in entry:
                names[key] = entry["tts"][0]
    return locales, names


def extract_symbols(tag: str, parents: dict[str, str], source: Source, shared: dict[str, str],
                    categories: dict[str, str], presentation: frozenset[str]) -> dict:
    locales, names = _tts_names(tag, parents, source, shared)
    symbols = {char: name for char, name in sorted(names.items())
               if len(char) == 1 and not char.isascii() and char not in presentation
               and (categories.get(char) in SYMBOL_CATEGORIES or char in SYMBOL_MARKS)}
    return {
        "source": {"release": RELEASE, "commit": COMMIT, "unicode": UNICODE,
                   "locales": [locale for locale, _ in locales], "files": dict(sorted(source.hashes.items()))},
        "symbols": symbols,
    }


def emoji_sequences(emoji: Source) -> list[str]:
    """Each emoji sequence of the Unicode emoji files, as Unicode writes it: a range of code points gives one
    sequence for each code point."""
    sequences = set()
    for name in EMOJI_FILES:
        blob = emoji.read(name)
        if blob is None:
            raise SystemExit(f"{emoji.root or emoji.base} holds no {name}")
        for line in blob.decode("utf-8").splitlines():
            points = line.split("#")[0].split(";")[0].strip()
            if not points:
                continue
            low, _, high = points.partition("..")
            if high:
                sequences.update(map(chr, range(int(low, 16), int(high, 16) + 1)))
            else:
                sequences.add("".join(chr(int(point, 16)) for point in points.split()))
    return sorted(sequences)


_QUOTES = frozenset("\"“”‘’")
_SPACES = frozenset(":,()")


def spoken_name(name: str, tag: str) -> str | None:
    """The spoken form of a CLDR `tts` name in the three steps, or None when it holds a character that is no word."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from text2spoken import NormalizationParams, normalize

    plain = "".join(" " if char in _SPACES else "" if char in _QUOTES and not (
        char == "’" and 0 < index < len(name) - 1 and name[index - 1].isalpha() and name[index + 1].isalpha())
        else char for index, char in enumerate(name))
    spoken = normalize(" ".join(plain.split()), tag, NormalizationParams(strict=False))
    if all(char.isalpha() or unicodedata.category(char).startswith("M") or char in " -'’" for char in spoken):
        return spoken
    return None


def extract_emoji(tag: str, parents: dict[str, str], source: Source, shared: dict[str, str],
                  sequences: list[str]) -> tuple[dict, list[str]]:
    """The emoji file of a tag, and the names that give no spoken name."""
    locales, names = _tts_names(tag, parents, source, shared)
    keys = {sequence.replace(SELECTOR, "") for sequence in sequences}
    spoken = {key: spoken_name(name, tag) for key, name in sorted(names.items()) if key in keys}
    data = {
        "source": {"release": RELEASE, "commit": COMMIT, "unicode": UNICODE,
                   "locales": [locale for locale, _ in locales], "files": dict(sorted(source.hashes.items()))},
        "names": spoken,
    }
    return data, sorted({names[key] for key, name in spoken.items() if name is None})


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, help="a checkout of cldr-json at the pinned commit")
    parser.add_argument("--ucd", type=Path, help=f"a copy of the Unicode {UNICODE} character database")
    parser.add_argument("--emoji", type=Path, help=f"a copy of the Unicode {UNICODE} emoji sequence files")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    source = Source(args.source)
    ucd = Source(args.ucd, UCD)
    categories, presentation = unicode_properties(ucd)
    ucd_hashes = {f"ucd/{path}": digest for path, digest in ucd.hashes.items()}
    emoji = Source(args.emoji, EMOJI)
    sequences = emoji_sequences(emoji)
    emoji_hashes = {f"emoji/{path}": digest for path, digest in emoji.hashes.items()}
    parents, licence = source.read("cldr-json/cldr-core/supplemental/parentLocales.json"), source.read("LICENSE")
    if parents is None or licence is None:
        parser.error(f"{args.source or RAW} holds no cldr-json release with parentLocales.json and LICENSE")
    parents = json.loads(parents)["supplemental"]["parentLocales"]["parentLocale"]
    shared = dict(source.hashes)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "LICENSE").write_bytes(licence)
    print(f"{len(sequences)} emoji sequences")
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
        data, names = extract_emoji(tag, parents, source, {**shared, **emoji_hashes}, sequences)
        write(args.out / f"{tag}.emoji.json", data)
        print(f"{tag}: {len(data['names'])} emoji sequences, {len(names)} names refused")
        for name in names:
            print(f"  refused {name!r}")
    written = 0
    for locale in DATE_LOCALES:
        data = extract_dates(locale, parents, source, shared)
        if data is None:
            print(f"{locale}: no dates file in the release")
            continue
        write(args.out / f"{locale}.dates.json", data)
        written += 1
        print(f"{locale}: long date {data['long']!r}")
    print(f"dates: {len(DATE_LOCALES)} locales in, {written} files out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
