"""`revision(lang)`: a string that changes when the output of `normalize` for a language can change (design
section 12.1).

The revision is a hash over the code and the data on the output path of the language. A probe in a fresh process
calls `normalize` and each parser writer for the language, and records the modules that the calls import. Each
distribution that holds one of those modules goes into the hash whole: the code tokens of each of its Python
modules and the bytes of each of its data files. The Unicode version of the interpreter is in the hash too, since
the tokenizer reads digits through `unicodedata`. A docstring, a comment and a `version.py` are not in the hash,
so a release that changes only those keeps the revision.

A probe that exits with an error, runs longer than `PROBE_TIMEOUT`, or prints no readable result raises
`RevisionError`.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import sysconfig
import tokenize
import unicodedata
import uuid
from collections.abc import Iterator
from functools import cache
from pathlib import Path

from text2spoken.core.language import select
from text2spoken.errors import RevisionError, require_type

FORMAT = "t2s1"
"""The prefix of a revision. It changes when the inputs or the encoding of the hash change."""

PROBE_TIMEOUT = 60
"""The seconds a probe may run before it counts as failed. A `pt-PT` probe takes up to 7 s on a loaded machine."""

_PROBE = """
import sys
before = set(sys.modules)
import json, sysconfig, warnings
marker, tag = sys.argv[1:3]
import text2spoken
from text2spoken.core import parsers
calls = (
    lambda: parsers.pronounce_number(42, tag), lambda: parsers.pronounce_ordinal(3, tag),
    lambda: parsers.pronounce_fraction("1/2", tag), lambda: parsers.spoken_date(tag, day=17, month=5, year=2024),
    lambda: parsers.spoken_time(tag, 14, 30), lambda: text2spoken.normalize("42 17/05/2024 14:30", tag),
)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for call in calls:
        try:
            call()
        except Exception:
            pass
paths = sysconfig.get_paths()
stdlib = tuple(paths[key] for key in ("stdlib", "platstdlib"))
installed = tuple(paths[key] for key in ("purelib", "platlib"))
def outside_stdlib(module):
    where = getattr(module, "__file__", None)
    return where is None or not where.startswith(stdlib) or where.startswith(installed)
print(marker + json.dumps(sorted(name for name, module in list(sys.modules.items())
                                 if name not in before and name.split(".")[0] not in sys.stdlib_module_names
                                 and outside_stdlib(module))), flush=True)
"""
"""Prints, after a marker, the modules outside the standard library that a `normalize` and each parser writer import
for a tag."""

_NATIVE = frozenset({".so", ".pyd", ".dll", ".dylib"})
_VERSION_FILES = frozenset({"version.py", "_version.py"})
_DROPPED = frozenset({tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER})
_LINE = frozenset({"NEWLINE", "INDENT", "DEDENT"})


def revision(lang: str) -> str:
    """A string that changes when the output of `normalize(text, lang)` can change, for some text.

    It must change when output can change: every input that can change the output for some text is in the hash. It
    may stay put when output cannot change: a docstring, a comment, `version.py`, the changelog or the tests leave it
    equal. It may also change on a refactor that keeps the output.

    The value is `"t2s1:"` and a SHA-256 in hex. The first call for a language runs a probe in a fresh process and
    reads the files of each distribution on the output path; later calls return the cached value."""
    require_type(lang, "lang", str)
    tag, language, variety = select(lang)
    return _revision(tag, language.code, variety.tag)


@cache
def _revision(tag: str, code: str, variety: str) -> str:
    digest = hashlib.sha256(json.dumps([FORMAT, unicodedata.unidata_version, tag, code, variety]).encode())
    for name in sorted(_top_levels(tag)):
        digest.update(f"\0{name}\0{_top_level_digest(name)}".encode())
    return f"{FORMAT}:{digest.hexdigest()}"


@cache
def probe(tag: str) -> frozenset[str]:
    """The modules outside the standard library that `normalize` and each parser writer import for a tag, in a
    fresh process with the import path of this one.

    The result is the one line that starts with a marker unique to the call, so output that a `sitecustomize` or an
    exit handler prints does not replace it. A probe that exits with an error, runs longer than `PROBE_TIMEOUT`, or
    prints no readable result raises `RevisionError`."""
    path = os.pathsep.join(entry or os.getcwd() for entry in sys.path)
    marker = f"text2spoken-revision-probe-{uuid.uuid4().hex}:"
    what = f"the revision probe for {tag!r}"
    try:
        done = subprocess.run([sys.executable, "-P", "-c", _PROBE, marker, tag], capture_output=True, text=True,
                              timeout=PROBE_TIMEOUT, check=True, env={**os.environ, "PYTHONPATH": path})
    except subprocess.TimeoutExpired as exc:
        raise RevisionError(f"{what} ran longer than {PROBE_TIMEOUT} s") from exc
    except subprocess.CalledProcessError as exc:
        raise RevisionError(f"{what} exited with {exc.returncode}:\n{exc.stderr}") from exc
    results = [line.removeprefix(marker) for line in done.stdout.splitlines() if line.startswith(marker)]
    if len(results) != 1:
        raise RevisionError(f"{what} printed {len(results)} results, not 1")
    try:
        return frozenset(json.loads(results[0]))
    except json.JSONDecodeError as exc:
        raise RevisionError(f"{what} printed a result that is not JSON: {results[0]!r}") from exc


def _top_levels(tag: str) -> set[str]:
    """Each top-level module of each distribution that holds a module of the probe, and `text2spoken`."""
    from importlib.metadata import packages_distributions

    owners = packages_distributions()
    loaded = {module.split(".")[0] for module in probe(tag)} | {"text2spoken"}
    distributions = {owner for name in loaded for owner in owners.get(name, ())}
    return loaded | {name for name, held in owners.items() if distributions & set(held)}


@cache
def _top_level_digest(name: str) -> str:
    """The hash of the files of one top-level module, where the import system finds it. A module that loads from
    anything but a directory or a file, such as a zip file, raises `RevisionError`."""
    from importlib.util import find_spec

    spec = find_spec(name)
    if spec is None:
        raise RevisionError(f"{name!r} is on the output path, but the import system does not find it")
    if spec.submodule_search_locations:
        roots = [Path(location) for location in spec.submodule_search_locations]
        for root in roots:
            if not root.is_dir():
                raise RevisionError(f"{name!r} loads from {str(root)!r}, which is not a directory")
        return tree_digest(name, *roots)
    if spec.origin is None or not Path(spec.origin).is_file():
        raise RevisionError(f"{name!r} loads from {spec.origin!r}, which is not a file")
    return hashlib.sha256(_entry(name, Path(spec.origin).name, Path(spec.origin)).encode()).hexdigest()


def tree_digest(name: str, *roots: Path) -> str:
    """The hash of the files of a package: the code tokens of each Python module and the bytes of each data file. A
    `version.py` or `_version.py` at the top of the package is not in it. A compiled module enters by its name and
    the version of its distribution, since its bytes differ by platform and by Python build."""
    digest = hashlib.sha256()
    for relative, path in sorted(_package_files(roots)):
        digest.update(_entry(name, relative, path).encode())
    return digest.hexdigest()


def _entry(name: str, relative: str, path: Path) -> str:
    if path.suffix in _NATIVE:
        module = Path(relative).with_name(path.name.split(".")[0]).as_posix()
        return f"\0{name}/{module}\0native\0{_native_version(name)}"
    return f"\0{name}/{relative}\0{file_digest(path)}"


def _package_files(roots: tuple[Path, ...]) -> Iterator[tuple[str, Path]]:
    for root in roots:
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if (path.is_file() and "__pycache__" not in relative.parts and path.suffix != ".pyc"
                    and not (len(relative.parts) == 1 and relative.name in _VERSION_FILES)):
                yield relative.as_posix(), path


@cache
def _native_version(name: str) -> str:
    from importlib.metadata import packages_distributions, version

    return " ".join(f"{owner}=={version(owner)}" for owner in sorted(set(packages_distributions().get(name, ()))))


def file_digest(path: Path) -> str:
    """The hash of the code tokens of a Python module, or of the bytes of any other file."""
    data = path.read_bytes()
    if path.suffix == ".py":
        try:
            data = json.dumps(code_tokens(data), ensure_ascii=False).encode()
        except (SyntaxError, tokenize.TokenError, UnicodeDecodeError):
            pass
    return hashlib.sha256(data).hexdigest()


def code_tokens(source: bytes) -> list[tuple[str, str]]:
    """The tokens of a module that can change what it does: no comment, no blank line and no string that stands
    as a statement of its own, as a docstring does. An f-string is one token with its source text, so that the
    tokens are the same on each Python version."""
    encoding, _ = tokenize.detect_encoding(io.BytesIO(source).readline)
    lines = io.StringIO(source.decode(encoding), newline="\n").readlines()
    tokens: list[tuple[str, str]] = []
    depth, start = 0, (0, 0)
    for token in tokenize.tokenize(io.BytesIO(source).readline):
        kind = tokenize.tok_name[token.type]
        if kind in ("FSTRING_START", "TSTRING_START"):
            depth, start = depth + 1, start if depth else token.start
        elif kind in ("FSTRING_END", "TSTRING_END"):
            depth -= 1
            if not depth:
                tokens.append(("STRING", _source_text(lines, start, token.end)))
        elif not depth and token.type not in _DROPPED:
            tokens.append((kind, "" if kind in _LINE else token.string))
    return _without_string_statements(tokens)


def _source_text(lines: list[str], start: tuple[int, int], end: tuple[int, int]) -> str:
    (first, first_column), (last, last_column) = start, end
    if first == last:
        return lines[first - 1][first_column:last_column]
    return lines[first - 1][first_column:] + "".join(lines[first:last - 1]) + lines[last - 1][:last_column]


def _without_string_statements(tokens: list[tuple[str, str]]) -> list[tuple[str, str]]:
    kept: list[tuple[str, str]] = []
    at = 0
    while at < len(tokens):
        end = at
        while end < len(tokens) and tokens[end][0] == "STRING":
            end += 1
        starts_line = not kept or kept[-1][0] in _LINE
        if end > at and starts_line and (end == len(tokens) or tokens[end][0] == "NEWLINE"):
            at = end + 1
            continue
        kept.extend(tokens[at:max(end, at + 1)])
        at = max(end, at + 1)
    return kept
