"""`revision(lang)` changes when the output of a language can change, and stays equal across processes and across
edits that cannot change the output (design section 12.1).

A mutant never edits an installed file: each test copies the package that it edits, and a process with the copy
first on its import path computes the revision."""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from importlib.util import find_spec
from pathlib import Path

import pytest

import text2spoken
from text2spoken import ArgumentTypeError, InvalidLanguageTagError, RevisionError, revision
from text2spoken.core.language import select
import text2spoken.core.revision as revision_module
from text2spoken.core.revision import _revision, _top_level_digest, code_tokens, probe, tree_digest

PACKAGE = Path(text2spoken.__file__).parent


def installed(name: str) -> Path:
    return Path(find_spec(name).submodule_search_locations[0])


def copy_package(source: Path, into: Path) -> Path:
    target = into / source.name
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} is not in {path}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def run_revision(lang: str, path: Path | None = None, seed: str = "0") -> subprocess.CompletedProcess:
    paths = [str(path)] if path else []
    env = {**os.environ, "PYTHONHASHSEED": seed,
           "PYTHONPATH": os.pathsep.join([*paths, *(entry or os.getcwd() for entry in sys.path)])}
    script = "import sys, text2spoken; print(text2spoken.revision(sys.argv[1]))"
    return subprocess.run([sys.executable, "-P", "-c", script, lang], capture_output=True, text=True, env=env)


def revision_in_process(lang: str, path: Path | None = None, seed: str = "0") -> str:
    done = run_revision(lang, path, seed)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


@pytest.fixture
def text2spoken_copy(tmp_path):
    return copy_package(PACKAGE, tmp_path)


def test_a_revision_is_the_scheme_prefix_and_a_sha256():
    assert re.fullmatch(r"t2s1:[0-9a-f]{64}", revision("pt-PT"))


def test_a_revision_is_equal_for_two_calls():
    assert revision("pt-PT") == revision("pt-PT")


@pytest.mark.parametrize("seed", ["1", "4242"])
def test_a_revision_is_equal_across_processes_with_any_hash_seed(seed):
    assert revision_in_process("pt-PT", seed=seed) == revision("pt-PT")


def test_two_languages_and_two_varieties_have_different_revisions():
    assert len({revision("pt-PT"), revision("pt-BR"), revision("en-US")}) == 3


def test_a_tag_with_no_region_has_the_revision_of_its_default_variety():
    assert revision("pt") == revision("pt-PT")


def test_lang_must_be_a_tag():
    with pytest.raises(ArgumentTypeError):
        revision(5)
    with pytest.raises(InvalidLanguageTagError):
        revision("not a tag")


def test_the_probe_reads_the_writers_of_the_language_and_not_every_module():
    loaded = probe("pt-PT")
    assert {"ovos_number_parser.numbers_pt", "ovos_date_parser", "unicode_rbnf", "tugalex"} <= loaded
    assert "ovos_date_parser.roman" not in loaded


def first_function_docstring(path: Path) -> tuple[int, int]:
    """The line and the column of the first function docstring of a module."""
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
            return node.body[0].lineno, node.body[0].col_offset
    raise AssertionError(f"{path} has no function docstring")


def test_a_docstring_edit_of_a_language_file_keeps_the_revision(text2spoken_copy):
    before = tree_digest("text2spoken", text2spoken_copy)
    pt = text2spoken_copy / "lang" / "pt.py"
    edit(pt, '"""Portuguese: pt-PT', '"""Portuguese, the language of Portugal and Brazil: pt-PT')
    line, column = first_function_docstring(pt)
    lines = pt.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[line - 1][column:column + 3] == '"""'
    lines[line - 1] = lines[line - 1][:column + 3] + "An edited docstring. " + lines[line - 1][column + 3:]
    pt.write_text("".join(lines), encoding="utf-8")
    assert tree_digest("text2spoken", text2spoken_copy) == before


def test_a_comment_edit_of_a_language_file_keeps_the_revision(text2spoken_copy):
    before = tree_digest("text2spoken", text2spoken_copy)
    pt = text2spoken_copy / "lang" / "pt.py"
    edit(pt, "\nfrom ", "\n# A comment on its own line.\nfrom ")
    edit(pt, '"EUR": {"minor": {"one": "cêntimo", "other": "cêntimos"}},',
         '"EUR": {"minor": {"one": "cêntimo", "other": "cêntimos"}},  # A comment at the end of a line.')
    assert tree_digest("text2spoken", text2spoken_copy) == before


def test_a_version_edit_keeps_the_revision(text2spoken_copy):
    before = tree_digest("text2spoken", text2spoken_copy)
    version = text2spoken_copy / "version.py"
    version.write_text(re.sub(r"VERSION_ALPHA = \d+", "VERSION_ALPHA = 999", version.read_text(encoding="utf-8")),
                       encoding="utf-8")
    assert "VERSION_ALPHA = 999" in version.read_text(encoding="utf-8")
    assert tree_digest("text2spoken", text2spoken_copy) == before


def test_a_one_token_code_edit_of_a_language_file_changes_the_revision(text2spoken_copy):
    before = tree_digest("text2spoken", text2spoken_copy)
    edit(text2spoken_copy / "lang" / "pt.py", '"other": "cêntimos"', '"other": "centavos"')
    assert tree_digest("text2spoken", text2spoken_copy) != before


def test_a_data_file_edit_changes_the_revision(text2spoken_copy):
    before = tree_digest("text2spoken", text2spoken_copy)
    edit(text2spoken_copy / "data" / "cldr" / "pt-PT.json", '":"', '":"x')
    assert tree_digest("text2spoken", text2spoken_copy) != before


def test_a_copy_of_the_package_has_the_revision_of_the_package(text2spoken_copy):
    assert revision_in_process("pt-PT", text2spoken_copy.parent) == revision("pt-PT")


def test_a_code_edit_of_the_package_that_the_process_imports_changes_the_revision(text2spoken_copy):
    edit(text2spoken_copy / "lang" / "pt.py", '"other": "cêntimos"', '"other": "centavos"')
    assert revision_in_process("pt-PT", text2spoken_copy.parent) != revision("pt-PT")


def test_copies_of_the_dependencies_have_the_revision_of_the_dependencies(tmp_path):
    for name in ("ovos_number_parser", "ovos_date_parser", "unicode_rbnf"):
        copy_package(installed(name), tmp_path)
    assert revision_in_process("pt-PT", tmp_path) == revision("pt-PT")


def test_an_edit_of_the_number_writer_of_the_language_changes_the_revision(tmp_path):
    numbers = copy_package(installed("ovos_number_parser"), tmp_path)
    edit(numbers / "numbers_pt.py", "JOINER_ON_TWENTYS = True,", "JOINER_ON_TWENTYS = False,")
    assert revision_in_process("pt-PT", tmp_path) != revision("pt-PT")


def test_an_edit_of_a_module_that_the_probe_does_not_load_changes_the_revision(tmp_path):
    assert "chronologia.computus" not in probe("pt-PT")
    dates = copy_package(installed("chronologia"), tmp_path)
    edit(dates / "computus.py", "def _gregorian_easter(year: int)", "def _gregorian_easter(year)")
    assert revision_in_process("pt-PT", tmp_path) != revision("pt-PT")


def test_an_edit_of_a_data_file_of_a_loaded_distribution_changes_the_revision(tmp_path):
    assert "unicode_rbnf" in probe("pt-PT")
    rbnf = copy_package(installed("unicode_rbnf"), tmp_path)
    edit(rbnf / "rbnf" / "pt.xml", '<rbnfrule value="20">vinte[', '<rbnfrule value="20">vintx[')
    assert revision_in_process("pt-PT", tmp_path) != revision("pt-PT")


def test_a_different_unicode_version_changes_the_revision(monkeypatch):
    """The tokenizer reads digits through `unicodedata`: Nag Mundari digits read as a number with Unicode 15 and
    stay as written with Unicode 14."""
    tag, language, variety = select("pt-PT")
    before = _revision.__wrapped__(tag, language.code, variety.tag)
    assert before == revision("pt-PT")
    monkeypatch.setattr(unicodedata, "unidata_version", "99.0.0")
    assert _revision.__wrapped__(tag, language.code, variety.tag) != before


def test_a_package_imported_from_a_zip_file_raises(tmp_path):
    root = installed("ovos_number_parser")
    archive = tmp_path / "numbers.zip"
    with zipfile.ZipFile(archive, "w") as packed:
        for path in root.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                packed.write(path, path.relative_to(root.parent).as_posix())
    done = run_revision("pt-PT", archive)
    assert done.returncode != 0 and done.stdout == ""
    assert "RevisionError" in done.stderr and str(archive / "ovos_number_parser") in done.stderr


def test_a_name_that_the_import_system_does_not_find_raises():
    with pytest.raises(RevisionError, match="t2s_no_such_module"):
        _top_level_digest("t2s_no_such_module")


@pytest.fixture
def fresh_probe():
    probe.cache_clear()
    _revision.cache_clear()
    yield
    probe.cache_clear()
    _revision.cache_clear()


def test_a_probe_that_prints_nothing_raises(fresh_probe, monkeypatch):
    monkeypatch.setattr(revision_module, "_PROBE", "pass")
    with pytest.raises(RevisionError, match="printed 0 results"):
        revision("pt-PT")


def test_a_print_at_exit_after_the_result_keeps_the_revision(fresh_probe, monkeypatch, tmp_path):
    before = revision("pt-PT")
    (tmp_path / "sitecustomize.py").write_text('import atexit\natexit.register(print, "done")\n', encoding="utf-8")
    control = subprocess.run([sys.executable, "-c", "pass"], capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": str(tmp_path)})
    assert control.stdout == "done\n"
    monkeypatch.syspath_prepend(str(tmp_path))
    probe.cache_clear()
    _revision.cache_clear()
    assert revision("pt-PT") == before


def test_text_before_the_result_without_a_line_end_keeps_the_revision(fresh_probe, monkeypatch, tmp_path):
    before = probe("pt-PT")
    (tmp_path / "sitecustomize.py").write_text('import sys\nsys.stdout.write("loading...")\n', encoding="utf-8")
    control = subprocess.run([sys.executable, "-P", "-c", "pass"], capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": str(tmp_path)})
    assert control.stdout == "loading..."
    monkeypatch.syspath_prepend(str(tmp_path))
    probe.cache_clear()
    assert probe("pt-PT") == before


def test_a_probe_that_writes_bytes_the_caller_cannot_decode_keeps_the_revision(fresh_probe, monkeypatch, tmp_path):
    before = probe("pt-PT")
    (tmp_path / "sitecustomize.py").write_text('import sys\nsys.stdout.write("café")\n', encoding="utf-8")
    control = subprocess.run([sys.executable, "-P", "-c", "pass"], capture_output=True,
                             env={**os.environ, "PYTHONIOENCODING": "latin-1", "PYTHONPATH": str(tmp_path)})
    assert control.stdout == "café".encode("latin-1")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("PYTHONIOENCODING", "latin-1")
    probe.cache_clear()
    assert probe("pt-PT") == before


def test_a_probe_that_runs_too_long_raises(fresh_probe, monkeypatch):
    monkeypatch.setattr(revision_module, "_PROBE", "import time\ntime.sleep(10)")
    monkeypatch.setattr(revision_module, "PROBE_TIMEOUT", 0.5, raising=False)
    with pytest.raises(RevisionError, match="ran longer than 0.5 s") as raised:
        revision("pt-PT")
    assert isinstance(raised.value.__cause__, subprocess.TimeoutExpired)


def test_a_probe_that_exits_with_an_error_raises(fresh_probe, monkeypatch):
    monkeypatch.setattr(revision_module, "_PROBE", "import sys\nsys.stderr.write('the probe broke')\nsys.exit(3)")
    with pytest.raises(RevisionError, match="exited with 3:\nthe probe broke") as raised:
        revision("pt-PT")
    assert isinstance(raised.value.__cause__, subprocess.CalledProcessError)
    assert raised.value.__cause__.returncode == 3


def test_a_probe_that_prints_two_results_raises(fresh_probe, monkeypatch):
    monkeypatch.setattr(revision_module, "_PROBE", "import sys\nprint(sys.argv[1] + '[]')\nprint(sys.argv[1] + '[]')")
    with pytest.raises(RevisionError, match="printed 2 results"):
        revision("pt-PT")


def test_a_probe_result_that_is_not_json_raises(fresh_probe, monkeypatch):
    monkeypatch.setattr(revision_module, "_PROBE", "import sys\nprint(sys.argv[1] + '[not json')")
    with pytest.raises(RevisionError, match="not JSON") as raised:
        revision("pt-PT")
    assert isinstance(raised.value.__cause__, json.JSONDecodeError)


def test_the_text_of_a_string_at_the_end_of_a_statement_is_in_the_tokens():
    assert code_tokens(b'x = "a"\n') != code_tokens(b'x = "b"\n')


def test_the_text_of_an_f_string_is_in_the_tokens():
    assert code_tokens(b'y = 1\nz = f"a{y}"\n') != code_tokens(b'y = 1\nz = f"b{y}"\n')
