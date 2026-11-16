"""Write the English person-name lists of `text2spoken/data/en/`: `given_names.json` and `surnames.json`.

    python scripts/extract_names.py SSA_CSV CENSUS_CSV

SSA_CSV is `names_ranks_counts.csv` of the Hugging Face dataset `nkrishnaswami/us-ssa-baby-names-national` at
revision b10af862de8b3bb8d315b2e11d1a334813b3ed8d, a CC0 copy of the national baby-name data of the US Social
Security Administration (`names.zip` of https://www.ssa.gov/oact/babynames/limits.html), with the columns `name`,
`sex`, `year` and `count`. `given_names.json` holds the union of the 1,000 names of each sex with the most births in
each year from 1900 to 2020. Within a year and a sex, the names are ranked by births, and a tie goes to the name
that comes first in alphabetical order, as the SSA files order them.

CENSUS_CSV is `Names_2010Census.csv` of `names.zip` at
https://www2.census.gov/topics/genealogy/2010surnames/names.zip, the frequently occurring surnames of the 2010 US
census, with the columns `name` and `rank`, and a last row `ALL OTHER NAMES` of rank 0. `surnames.json` holds the
1,000 surnames of highest rank, in capitals as the file writes them.

Each file holds a `source` field and a `names` field with the names in alphabetical order.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

FIRST_YEAR, LAST_YEAR, TOP = 1900, 2020, 1000
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "en"
GIVEN_SOURCE = (
    "US Social Security Administration, baby names from Social Security card applications, national data "
    "(names.zip, https://www.ssa.gov/oact/babynames/limits.html), public domain, read from the CC0 copy "
    "nkrishnaswami/us-ssa-baby-names-national on Hugging Face at revision b10af862de8b3bb8d315b2e11d1a334813b3ed8d: "
    "the union of the 1,000 names of each sex with the most births in each year from 1900 to 2020, with a tie "
    "ranked in alphabetical order. Written by scripts/extract_names.py.")
SURNAME_SOURCE = (
    "US Census Bureau, Frequently Occurring Surnames from the 2010 Census "
    "(https://www2.census.gov/topics/genealogy/2010surnames/names.zip, Names_2010Census.csv), public domain: the "
    "1,000 surnames of highest rank, in capitals as the file writes them. Written by scripts/extract_names.py.")


def given_names(path: Path) -> list[str]:
    births: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as rows:
        for row in csv.DictReader(rows):
            if FIRST_YEAR <= int(row["year"]) <= LAST_YEAR:
                births[row["year"], row["sex"]].append((-int(row["count"]), row["name"]))
    assert len(births) == 2 * (LAST_YEAR - FIRST_YEAR + 1), f"{len(births)} year and sex groups"
    return sorted({name for group in births.values() for _, name in sorted(group)[:TOP]})


def surnames(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as rows:
        names = sorted(row["name"] for row in csv.DictReader(rows) if 1 <= int(row["rank"]) <= TOP)
    assert len(names) == TOP, f"{len(names)} surnames"
    return names


def write(name: str, source: str, names: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8") as out:
        json.dump({"source": source, "names": names}, out, ensure_ascii=False, indent=0)
        out.write("\n")
    print(f"{name}: {len(names)} names")


if __name__ == "__main__":
    write("given_names.json", GIVEN_SOURCE, given_names(Path(sys.argv[1])))
    write("surnames.json", SURNAME_SOURCE, surnames(Path(sys.argv[2])))
