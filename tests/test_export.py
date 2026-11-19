"""`python -m text2spoken.export`, run as a user runs it."""
import json
import subprocess
import sys

import pytest

from text2spoken import InvalidLanguageTagError, normalize, supports
from text2spoken.core.language import language_file


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "text2spoken.export", *args], capture_output=True, text=True)


# README: "The command prints the language file that `normalize` selects for that tag." and "If the tag is not valid,
# or if no language file reads the tag, the command writes one error line and exits with code 1."
@pytest.mark.parametrize("tag", ["en-GB", "en-US", "EN", "en_us", "en-Latn-US", "en-x-scouse"])
def test_a_tag_exports_the_file_that_normalize_selects(tag):
    result = run(tag)
    assert (result.returncode, result.stderr) == (0, "")
    tables = json.loads(result.stdout)
    spec = language_file(supports(tag).code)
    assert tables["code"] == spec.code == "en"
    assert set(tables["data"]) == set(spec.data)
    assert set(tables["varieties"]) == {variety.tag for variety in spec.varieties}
    assert result.stdout == run("en").stdout


@pytest.mark.parametrize("tag", ["lb", "lb-LU", "xx"])
def test_a_valid_tag_with_no_language_file_is_one_error_line(tag):
    assert language_file(tag.split("-")[0]) is None
    result = run(tag)
    assert (result.returncode, result.stdout) == (1, "")
    assert "Traceback" not in result.stderr
    assert result.stderr.count("\n") == 1 and repr(tag) in result.stderr


@pytest.mark.parametrize("tag", ["not a tag!", "en--GB", ""])
def test_an_invalid_tag_is_one_error_line(tag):
    with pytest.raises(InvalidLanguageTagError):
        normalize("1", tag)
    result = run(tag)
    assert (result.returncode, result.stdout) == (1, "")
    assert "Traceback" not in result.stderr
    assert result.stderr.count("\n") == 1 and "not a BCP 47 language tag" in result.stderr


def test_no_argument_prints_the_usage():
    result = run()
    assert result.returncode == 2 and result.stdout == ""
    assert result.stderr.startswith("usage: python -m text2spoken.export") and "Traceback" not in result.stderr


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_prints_the_usage(flag):
    result = run(flag)
    assert (result.returncode, result.stderr) == (0, "")
    assert result.stdout.startswith("usage: python -m text2spoken.export")
