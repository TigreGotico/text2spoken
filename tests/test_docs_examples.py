"""Every example in README.md and docs/ is the output of a real run.

A `python` code block with `>>>` lines runs as a doctest, one namespace per page. A `text stderr` block after a
doctest holds the log lines that the doctest writes. A table with a `Written` column holds examples: each column
whose header holds `Spoken` or `Second pass` must equal `normalize` of the written text. The header of such a
column, or a `Tag` column, gives the tag in backticks. A form name in backticks with `on` or `off` after it, such
as `` `EMOJI` on ``, and a param in backticks, such as `` `clock="24h"` ``, give the params. A cell that says
`stays as written` expects the text unchanged. A table whose first column is `Option` gives the values and the
defaults of each option, and `supports` and `effective_params` must give the same.

docs/adding-a-language.md builds an example language file, `text2spoken/lang/id.py`. The info string of a code
block names the file that the block writes: `python text2spoken/lang/id.py` is the whole file, and
`python +text2spoken/lang/id.py` adds to it. The top-level statements of an added block replace the statements of
the same name, and new ones go before `LANGUAGE`. `text tests/data/id.tsv` and `text +tests/data/id.tsv` write and
add test rows, and `python +tests/test_table_mutation.py` adds a line to `ENTRIES`. Each doctest after a block runs
with the files as they stand, and each `pytest` command of a `bash` block runs on a copy of the checkout with those
files. The `text output` block after it holds lines of the output: each `E` line, the start of each `FAILED` line,
and the counts of the last line with no deselected tests, warnings or time.
"""
import ast
import doctest
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import types
from dataclasses import replace
from pathlib import Path

import pytest

from tests.contract import SHARED_VERBALIZERS
from tests.data_keys import OPTIONAL, READERS
from text2spoken import Form, FrozenMap, GrammaticalGender, NormalizationParams, effective_params, normalize, supports
from text2spoken.core import language, recognizers

ROOT = Path(__file__).parent.parent
PAGES = sorted([ROOT / "README.md", *(ROOT / "docs").glob("*.md"), *(ROOT / "docs" / "languages").glob("*.md")])
WALKTHROUGH = ROOT / "docs" / "adding-a-language.md"
EXAMPLE_FILE = "text2spoken/lang/id.py"
EXAMPLE_ROWS = "tests/data/id.tsv"
ENTRIES_FILE = "tests/test_table_mutation.py"
MINIMUM = {
    "README.md": 3, "index.md": 0, "quickstart.md": 8, "usage.md": 16, "how-it-reads.md": 3, "numbers.md": 26,
    "dates-and-times.md": 24, "money-units-and-symbols.md": 45, "addresses-letters-and-emoji.md": 92, "api.md": 20,
    "errors.md": 8, "adding-a-language.md": 7, "development.md": 0, "ar.md": 36, "de.md": 51, "en.md": 50,
    "es.md": 50, "eu.md": 28, "pt.md": 46, "ru.md": 49,
}
"""The fewest examples that each page holds, so that a page that loses its examples fails."""
FENCE = re.compile(r"^```(\S*)(?: (\S+))?\n(.*?)^```$", re.M | re.S)
NAMES = {"frozenset": frozenset, "FrozenMap": FrozenMap, "GrammaticalGender": GrammaticalGender}
"""The names that a param in a column header may use."""
CLAIM = re.compile(r"`[^`\n]+` reads [\"'“‘]")


def tables(text: str) -> list[list[list[str]]]:
    """Each table of a page as rows of cells, the header first, with no separator row."""
    found, current = [], []
    for line in [*text.splitlines(), ""]:
        if line.startswith("|"):
            current.append([cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line)[1:-1]])
        elif current:
            found.append([row for row in current if not re.fullmatch(r"[\s:|-]*", "|".join(row))])
            current = []
    return found


def unquote(cell: str) -> str:
    match = re.fullmatch(r"(`+) ?(.*?) ?\1", cell)
    return match.group(2) if match else cell


def is_example_column(title: str) -> bool:
    return "Spoken" in title or "Second pass" in title


def column_spec(header: str) -> tuple[str | None, NormalizationParams, int]:
    """The tag, the params and the number of passes that a column header gives."""
    tag, params = None, NormalizationParams()
    for token, after in re.findall(r"`([^`]+)`( on| off)?", header):
        if after:
            form = Form[token]
            params = params.plus(form) if after == " on" else params.without(form)
        elif "=" in token:
            name, value = token.split("=", 1)
            params = replace(params, **{name: eval(value, {"__builtins__": {}}, NAMES)})
        else:
            tag = token
    return tag, params, 2 if "Second pass" in header else 1


def table_examples(page: Path) -> list[tuple[str, str, str, NormalizationParams, int, str]]:
    """(where, written, tag, params, passes, expected) for each example cell of a page."""
    examples = []
    for table in tables(page.read_text(encoding="utf-8")):
        header, *body = table
        if "Written" not in header:
            continue
        written_column = header.index("Written")
        tag_column = header.index("Tag") if "Tag" in header else None
        for index, title in enumerate(header):
            if not is_example_column(title):
                continue
            tag, params, passes = column_spec(title)
            for row in body:
                written = unquote(row[written_column])
                row_tag = unquote(row[tag_column]) if tag_column is not None else tag
                assert row_tag, f"{page.name}: no tag for {written!r}"
                cell = row[index]
                expected = written if cell == "stays as written" else unquote(cell)
                examples.append((f"{page.name}: {written}", written, row_tag, params, passes, expected))
    return examples


TABLE_EXAMPLES = [example for page in PAGES for example in table_examples(page)]


@pytest.mark.parametrize(("where", "written", "tag", "params", "passes", "expected"), TABLE_EXAMPLES,
                         ids=[e[0] for e in TABLE_EXAMPLES])
def test_table_example(where, written, tag, params, passes, expected):
    spoken = written
    for _ in range(passes):
        spoken = normalize(spoken, tag, params)
    assert spoken == expected


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_example_tables_have_a_written_column(page):
    """A table with a spoken column and no `Written` column would hold examples that no test runs."""
    for header, *_ in tables(page.read_text(encoding="utf-8")):
        assert "Written" in header or not any(map(is_example_column, header)), f"{page.name}: {header}"


def option_cell(tag: str, name: str) -> str:
    """The values of an option in a tag, as an options table writes them."""
    if name in supports(tag).not_applicable:
        return "changes nothing"
    return ", ".join(f"`{value}`" for value in sorted(map(str, supports(tag).options[name])))


def default_cell(tag: str, name: str) -> str:
    """The default of an option in a tag, as an options table writes it."""
    if name == "default_gender":
        return f"`{language.select(tag)[1].default_gender}`"
    value = getattr(effective_params(tag), name)
    if isinstance(value, frozenset):
        return ", ".join(f"`{region}`" for region in sorted(value)) or "none"
    return f"`{value}`"


def option_rows(page: Path) -> list[tuple[str, str, str]]:
    """(where, expected, written) for each cell of a table whose first column is `Option`: the `Values` column holds
    the values that `supports` gives, and each `Default` column the value that `effective_params` gives."""
    cells = []
    for table in tables(page.read_text(encoding="utf-8")):
        header, *body = table
        if not header or header[0] != "Option":
            continue
        tags = [re.search(r"`([^`]+)`", title).group(1) for title in header if title.startswith("Default")]
        for row in body:
            name = unquote(row[0])
            for title, cell in zip(header[1:], row[1:]):
                if title == "Values":
                    cells.append((f"{page.name}: {name} values", option_cell(tags[0], name), cell))
                elif title.startswith("Default"):
                    tag = re.search(r"`([^`]+)`", title).group(1)
                    if cell != "-":
                        cells.append((f"{page.name}: {name} in {tag}", default_cell(tag, name), cell))
    return cells


OPTION_ROWS = [cell for page in PAGES for cell in option_rows(page)]


@pytest.mark.parametrize(("where", "expected", "written"), OPTION_ROWS, ids=[c[0] for c in OPTION_ROWS])
def test_option_table(where, expected, written):
    assert written == expected


def fences(page: Path) -> list[tuple[str, str, str]]:
    """(language, info, body) of each code block of a page, in order."""
    return FENCE.findall(page.read_text(encoding="utf-8"))


def test_every_page_holds_its_examples():
    """Each page holds at least its number of checked examples, so a lost page or a lost table fails."""
    counts = {}
    for page in PAGES:
        doctests = sum(len(re.findall(r"^>>> ", body, re.M)) for lang, _, body in fences(page) if lang == "python")
        counts[page.name] = (doctests + sum(e[0].startswith(f"{page.name}:") for e in TABLE_EXAMPLES)
                             + sum(c[0].startswith(f"{page.name}:") for c in OPTION_ROWS))
    assert set(counts) == set(MINIMUM)
    assert {name: n for name, n in counts.items() if n < MINIMUM[name]} == {}


def merge(source: str, part: str) -> str:
    """The module source with the top-level statements of `part` in place of those of the same name."""
    def name(node: ast.stmt) -> str:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            return node.name
        if isinstance(node, ast.Assign):
            return node.targets[0].id
        if isinstance(node, ast.ImportFrom):
            return f"from {node.module}"
        return "docstring" if isinstance(node, ast.Expr) else ast.dump(node)

    def pieces(text: str) -> dict[str, str]:
        return {name(node): ast.get_source_segment(text, node) for node in ast.parse(text).body}

    merged = pieces(source)
    for key, segment in pieces(part).items():
        if key in merged:
            merged[key] = segment
        else:
            merged = {**{k: v for k, v in merged.items() if k != "LANGUAGE"}, key: segment,
                      "LANGUAGE": merged["LANGUAGE"]}
    return "\n\n".join(merged.values()) + "\n"


def load(source: str) -> language.LanguageSpec:
    module = types.ModuleType("text2spoken.lang.id")
    exec(compile(source, EXAMPLE_FILE, "exec"), module.__dict__)
    return module.LANGUAGE


def shipped() -> dict[str, language.LanguageSpec]:
    """The registry of the shipped files. A reader who follows the walk-through has an `id` file, and the page
    starts from a checkout with none."""
    return {code: spec for code, spec in language._registry().items() if code != "id"}


class Records(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


@pytest.mark.parametrize("page", [p for p in PAGES if any(">>>" in body for _, _, body in fences(p))],
                         ids=lambda p: p.name)
def test_doctests(page, monkeypatch):
    registry = shipped()
    monkeypatch.setattr(language, "_registry", lambda: registry)
    source, namespace, logged = "", {}, []
    parser, runner = doctest.DocTestParser(), doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    logger = logging.getLogger("text2spoken")
    handlers = list(logger.handlers)
    try:
        for index, (lang, info, body) in enumerate(fences(page)):
            if info.lstrip("+") == EXAMPLE_FILE:
                source = merge(source, body) if info.startswith("+") else body
                example = {**registry, "id": load(source)}
                monkeypatch.setattr(language, "_registry", lambda example=example: example)
            elif lang == "text" and info == "stderr":
                assert body.splitlines() == logged, f"{page.name} block {index}"
            elif lang == "python" and ">>>" in body:
                records = Records()
                logger.addHandler(records)
                test = parser.get_doctest(body, namespace, f"{page.name} block {index}", str(page), 0)
                runner.run(test, clear_globs=False)
                logger.removeHandler(records)
                namespace, logged = test.globs, records.messages
    finally:
        logger.handlers[:] = handlers
    assert runner.failures == 0, f"{runner.failures} doctest failures in {page.name}"


def finished_file() -> str:
    """The last whole example file of the walk-through."""
    return [body for _, info, body in fences(WALKTHROUGH) if info == EXAMPLE_FILE][-1]


def test_the_example_language_ships_no_file():
    """The walk-through starts from a checkout with no `id` file. A reader's own copy of the finished file is
    allowed, so that `pytest tests` passes at the end of the page."""
    path = ROOT / EXAMPLE_FILE
    assert not path.exists() or ast.dump(ast.parse(path.read_text(encoding="utf-8"))) == \
        ast.dump(ast.parse(finished_file())), (
        f"{EXAMPLE_FILE} ships, so docs/adding-a-language.md no longer starts from a language with no file. "
        "Move the walk-through to a language that still has no file.")


def test_each_added_block_says_what_it_adds_to():
    """A block that adds to a file is not the whole file, and the paragraph before it says so."""
    text = WALKTHROUGH.read_text(encoding="utf-8")
    for match in FENCE.finditer(text):
        if match.group(2) and match.group(2).startswith("+"):
            before = text[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
            assert f"add to `{match.group(2)[1:]}`" in before.lower(), before


def test_the_finished_file_is_the_sum_of_the_steps():
    source, finished = "", finished_file()
    for _, info, body in fences(WALKTHROUGH):
        if info.lstrip("+") == EXAMPLE_FILE and body != finished:
            source = merge(source, body) if info.startswith("+") else body
    assert ast.dump(ast.parse(source)) == ast.dump(ast.parse(finished))


def summary(output: str) -> str:
    """The counts of the last line of a pytest run, with no deselected tests, warnings or time."""
    last = [line for line in output.splitlines() if line.startswith("=")][-1].strip("= ")
    counts = [part for part in re.sub(r" in [\d.]+s.*$", "", last).split(", ")
              if not re.search(r"deselected|warnings?$", part)]
    return ", ".join(counts)


def run_pytest(copy: Path, command: str) -> str:
    args = shlex.split(command)
    assert args[0] == "pytest", command
    env = {**os.environ, "PYTHONPATH": str(copy), "PYTHONDONTWRITEBYTECODE": "1", "COLUMNS": "80"}
    return subprocess.run([sys.executable, "-m", "pytest", *args[1:], "-p", "no:cacheprovider"], cwd=copy, env=env,
                          capture_output=True, text=True).stdout


def test_walkthrough(tmp_path):
    """Each file, test row and command of the walk-through, run on a copy of the checkout. Each test row reads as
    its expected value, and each output block holds lines of the real output."""
    copy = tmp_path / "checkout"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".venv*", "__pycache__", "*.egg-info", "build",
                                                               "dist", "docs"))
    for name in (EXAMPLE_FILE, EXAMPLE_ROWS):
        (copy / name).unlink(missing_ok=True)
    entries = copy / ENTRIES_FILE
    entries.write_text(re.sub(r'(?m)^    "id": \{.*\},\n', "", entries.read_text(encoding="utf-8")), encoding="utf-8")
    source, output, commands, outputs = "", "", 0, 0
    for lang, info, body in fences(WALKTHROUGH):
        target = info.lstrip("+")
        if target == EXAMPLE_FILE:
            source = merge(source, body) if info.startswith("+") else body
            (copy / target).write_text(source, encoding="utf-8")
        elif target == EXAMPLE_ROWS:
            rows = copy / target
            rows.write_text((rows.read_text(encoding="utf-8") if info.startswith("+") else "") + body,
                            encoding="utf-8")
            registry = {**shipped(), "id": load(source)}
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(language, "_registry", lambda: registry)
                for line in body.splitlines():
                    row_id, tag, _, text, expected, *_ = line.split("\t")
                    assert row_id == "id" or normalize(text, tag) == expected, row_id
        elif target == ENTRIES_FILE:
            entries.write_text(re.sub(r"(?m)^ENTRIES = \{\n", lambda m: m.group() + body,
                                      entries.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        elif lang == "bash" and body.startswith("pytest "):
            output = run_pytest(copy, body.strip())
            commands += 1
        elif lang == "text" and info == "output":
            real = [line.rstrip() for line in output.splitlines()]
            for line in body.splitlines():
                if line.startswith("E "):
                    assert line in real, line
                elif line.startswith("FAILED "):
                    assert any(r.startswith(line) for r in real), line
                else:
                    assert line == summary(output), output
            outputs += 1
    assert (commands, outputs) >= (5, 5)


def shared_table(first: str) -> list[list[str]]:
    [body] = [body for header, *body in tables(WALKTHROUGH.read_text(encoding="utf-8")) if header[0] == first]
    return body


def keys_cell(cell: str) -> set[str]:
    return set() if cell == "none" else set(re.findall(r"`([^`]+)`", cell))


def test_the_shared_recognizer_table():
    """The recognizers of `SHARED`, their forms, and the data keys that each reads, as `READERS` and `OPTIONAL`
    declare them."""
    body = shared_table("Recognizer")
    assert {unquote(row[0]) for row in body} == set(recognizers.SHARED)
    for name, form, needed, optional in body:
        recognizer = recognizers.SHARED[unquote(name)]
        keys = READERS[recognizer.name]
        assert (unquote(form), keys_cell(needed), keys_cell(optional)) == \
            (recognizer.form.name, keys - OPTIONAL, keys & OPTIONAL), name


def test_the_shared_verbalizer_table():
    body = shared_table("Verbalizer")
    assert {unquote(row[0]) for row in body} == {name for name in READERS if name.startswith("speak_")}
    for name, needed, optional in body:
        assert unquote(name) in SHARED_VERBALIZERS
        keys = READERS[unquote(name)]
        assert (keys_cell(needed), keys_cell(optional)) == (keys - OPTIONAL, keys & OPTIONAL), name


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_no_unchecked_output_in_prose(page):
    """An output in prose is not checked, so a page gives each output in a doctest or an example table."""
    text = FENCE.sub("", page.read_text(encoding="utf-8"))
    prose = [line for line in text.splitlines() if not line.startswith("|")]
    assert not [line for line in prose if CLAIM.search(line)]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_links_resolve(page):
    """Each relative link names a file that exists, and each anchor a heading of that file."""
    text = FENCE.sub("", page.read_text(encoding="utf-8"))
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http://", "https://")):
            continue
        path, _, anchor = target.partition("#")
        file = (page.parent / path).resolve() if path else page
        assert file.exists(), f"{page.name}: {target}"
        if anchor and file.suffix == ".md":
            headings = re.findall(r"^#+ (.+)$", FENCE.sub("", file.read_text(encoding="utf-8")), re.M)
            slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
            assert anchor in slugs, f"{page.name}: {target}"
