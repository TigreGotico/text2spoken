"""Each page with an agent hint is true against the code.

The `verify` line of the hint of each page runs `scripts/check_doc_page.py` on that page. This test runs the
same command, so CI fails when a change of the code makes a value that a page states untrue.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = [path.relative_to(ROOT).as_posix()
         for path in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
         if "<!-- agent-hint\n" in path.read_text(encoding="utf-8")]


@pytest.mark.parametrize("page", PAGES)
def test_page_is_true(page):
    command = f"python scripts/check_doc_page.py {page}"
    assert f"verify: `{command}`" in (ROOT / page).read_text(encoding="utf-8")
    run = subprocess.run([sys.executable, "scripts/check_doc_page.py", page], cwd=ROOT, capture_output=True,
                         text=True)
    assert run.returncode == 0, run.stderr
