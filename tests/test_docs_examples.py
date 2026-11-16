"""Every example in README.md and docs/ is the output of a real run.

Two kinds of example are checked. A `python` code block with `>>>` lines runs as a doctest, one namespace per page.
A table with a `Written` column holds examples: each column whose header holds `Spoken` or `Second pass`
must equal `normalize` of the written text. The header of such a column, or a `Tag` column, gives the tag in
backticks. A form name in backticks with `on` or `off` after it, such as `` `EMOJI` on ``, and a param in
backticks, such as `` `clock="24h"` ``, give the params. A cell that says `stays as written` expects the text
unchanged. A table whose first column is `Option` gives the values and the defaults of each option, and
`supports` and `effective_params` must give the same.

docs/adding-a-language.md builds an example language file. A code block whose info string is
`python text2spoken/lang/id.py` holds a part of that file: its top-level statements replace the statements of the
same name, and new ones go before `LANGUAGE`. Each doctest after such a block runs with the file as it stands.
"""
import ast
import doctest
import logging
import re
import types
from dataclasses import replace
from pathlib import Path

import pytest

from text2spoken import Form, FrozenMap, GrammaticalGender, NormalizationParams, effective_params, normalize, supports
from text2spoken.core import language

ROOT = Path(__file__).parent.parent
PAGES = sorted([ROOT / "README.md", *(ROOT / "docs").glob("*.md"), *(ROOT / "docs" / "languages").glob("*.md")])
EXAMPLE_FILE = "text2spoken/lang/id.py"
FENCE = re.compile(r"^```(\S*)(?: (\S+))?\n(.*?)^```$", re.M | re.S)
NAMES = {"frozenset": frozenset, "FrozenMap": FrozenMap, "GrammaticalGender": GrammaticalGender}
"""The names that a param in a column header may use."""
CLAIM = re.compile(r'`[^`\n]+` reads "')


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
            if "Spoken" not in title and "Second pass" not in title:
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


def option_rows(page: Path) -> list[tuple[str, str, str, str]]:
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


def blocks(page: Path) -> list[tuple[str, str]]:
    """(info, code) of each `python` block of a page, in order."""
    return [(target, code) for lang, target, code in FENCE.findall(page.read_text(encoding="utf-8"))
            if lang == "python"]


def load(source: str) -> language.LanguageSpec:
    module = types.ModuleType("text2spoken.lang.id")
    exec(compile(source, EXAMPLE_FILE, "exec"), module.__dict__)
    return module.LANGUAGE


@pytest.mark.parametrize("page", [p for p in PAGES if any(">>>" in code for _, code in blocks(p))],
                         ids=lambda p: p.name)
def test_doctests(page, monkeypatch):
    shipped = language._registry()
    source, namespace = "", {}
    parser, runner = doctest.DocTestParser(), doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    logger = logging.getLogger("text2spoken")
    handlers = list(logger.handlers)
    try:
        for index, (target, code) in enumerate(blocks(page)):
            if target == EXAMPLE_FILE:
                source = merge(source, code) if source else code
                registry = {**shipped, "id": load(source)}
                monkeypatch.setattr(language, "_registry", lambda registry=registry: registry)
            elif ">>>" in code:
                test = parser.get_doctest(code, namespace, f"{page.name} block {index}", str(page), 0)
                runner.run(test, clear_globs=False)
                namespace = test.globs
    finally:
        logger.handlers[:] = handlers
    assert runner.failures == 0, f"{runner.failures} doctest failures in {page.name}"


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
