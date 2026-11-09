"""Write the tables of a language file as JSON: `python -m text2spoken.export <code>`."""
from __future__ import annotations

import json
import sys

from text2spoken.core.language import language_file
from text2spoken.params import thaw


def export(code: str) -> dict:
    language = language_file(code)
    if language is None or language.code != code:
        raise LookupError(f"no language file with the code {code!r}")
    return {"code": language.code, "serves": list(language.serves), "data": thaw(language.data),
            "varieties": {variety.tag: thaw(variety.data) for variety in language.varieties}}


if __name__ == "__main__":
    json.dump(export(sys.argv[1]), sys.stdout, ensure_ascii=False, indent=2)
    print()
