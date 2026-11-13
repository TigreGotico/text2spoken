"""Write the tables of a language file as JSON: `python -m text2spoken.export <lang>`."""
from __future__ import annotations

import argparse
import json
import sys

from text2spoken.core.language import language_file, select
from text2spoken.errors import InvalidLanguageTagError
from text2spoken.params import thaw


def export(lang: str) -> dict:
    """The tables of the language file that reads the BCP 47 tag `lang`, selected as `normalize` selects it."""
    _, language, _ = select(lang)
    if language_file(language.code) is not language:
        raise LookupError(f"no language file reads {lang!r}")
    return {"code": language.code, "serves": list(language.serves), "data": thaw(language.data),
            "varieties": {variety.tag: thaw(variety.data) for variety in language.varieties}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m text2spoken.export",
                                     description="Write the tables of a language file as JSON.")
    parser.add_argument("lang", help="a BCP 47 tag, for example en or en-GB")
    args = parser.parse_args(argv)
    try:
        tables = export(args.lang)
    except (InvalidLanguageTagError, LookupError) as error:
        print(f"{parser.prog}: error: {error}", file=sys.stderr)
        return 1
    json.dump(tables, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
