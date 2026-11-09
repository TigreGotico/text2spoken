"""Write the colour table of a language file from one ovos-color-parser palette.

    python scripts/seed_colors.py en

The script prints a Python dict literal of six lowercase hex digits to one lowercase name, which goes into the
`colors` key of the language data. It records the palette it read. A native speaker checks each table.

For `en`, the palette is `en-US/dot-net-colors.json`, the CSS named colours. The palette writes each name as
one word (`Darkslategray`). The script takes the word breaks from `en-US/wikipedia_color_list.json` when that
palette holds a name with the same letters, and it drops a colour whose word breaks it cannot find.
"""
from __future__ import annotations

import json
import re
import sys
from importlib.resources import files

PALETTES = {"en": ("en-US", "dot-net-colors.json", "wikipedia_color_list.json")}


def _letters(name: str) -> str:
    return re.sub("[^a-z]", "", name.lower())


def seed(code: str) -> tuple[dict[str, str], list[str]]:
    locale, palette, spacing = PALETTES[code]
    res = files("ovos_color_parser") / "res" / locale
    colors = json.loads((res / palette).read_text(encoding="utf-8"))
    spaced = {}
    for name in json.loads((res / spacing).read_text(encoding="utf-8")).values():
        plain = re.sub(" [(].*", "", name).strip().lower()
        spaced.setdefault(_letters(plain), plain)
    table, dropped = {}, []
    for hex_code, name in colors.items():
        words = spaced.get(_letters(name))
        if words is None:
            dropped.append(name)
            continue
        table[hex_code[1:].lower()] = words
    return dict(sorted(table.items())), dropped


if __name__ == "__main__":
    table, dropped = seed(sys.argv[1])
    print(f"# {len(table)} colours seeded from {'/'.join(PALETTES[sys.argv[1]][:2])}; {len(dropped)} dropped: "
          + ", ".join(dropped), file=sys.stderr)
    print(json.dumps(table, ensure_ascii=False, indent=4))
