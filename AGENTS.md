# AGENTS.md

text2spoken rewrites written forms, such as numbers, dates and sums of money, into the words that a speaker says. Each language has one file of rules and one file of test rows, and the docs examples are real runs that the suite checks.

## Map

| Path | What it holds |
| --- | --- |
| `text2spoken/__init__.py` | The public names. The main calls: `normalize`, `analyze`, `render`, `supports`, `effective_params`, `revision` |
| `text2spoken/params.py`, `text2spoken/errors.py` | `NormalizationParams`, and the errors and warnings |
| `text2spoken/core/` | The shared steps: tokens, recognizers, spellers, dates, times, units, currencies, revision |
| `text2spoken/lang/<code>.py` | One language file. Its module docstring cites the source of each rule |
| `text2spoken/data/` | JSON data. The CLDR files in `data/cldr/` come from `scripts/extract_cldr.py` |
| `tests/data/<code>.tsv` | The test rows of each language file |
| `tests/contract.py` | The checks of the language file contract |
| `scripts/` | The scripts that write the data files, and `check_doc_page.py`, which checks a docs page against the code |
| `docs/` | The user docs. `docs/index.md` lists every page in reading order |

## Set up and test

```bash
uv venv
source .venv/bin/activate
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

The `test` extra installs `tugalex`, so the suite runs every language file. CI runs the same `pytest tests` on Python 3.11, 3.12 and 3.13.

## Hard rules

1. An expected value of a row comes from a cited rule, from arithmetic done by hand, or from a native speaker. It never comes from a run of the code. See [the row files](docs/development.md#the-row-files).
2. The rows of a language file cover each form that the file declares, except `LEXICON`, and each variety. They also hold the four guard texts `16:9`, `3:16`, `#decade` and `13/13/2024`. `tests/test_rows.py` checks this.
3. A language file meets each clause of [the contract](docs/adding-a-language.md#the-contract), which `tests/test_contract.py` checks.
4. A language file adds the entries of its tables to `ENTRIES` in `tests/test_table_mutation.py`. See [other tests](docs/development.md#other-tests).
5. Every docs example is the output of a real run. A new page in `docs/` needs an entry in `MINIMUM` in `tests/test_docs_examples.py`, and a language page needs at least `LANGUAGE_MINIMUM` examples. See [keep the docs true](docs/development.md#keep-the-docs-true).
6. A language page gives no number of rows of its file, so a pull request that adds rows does not change the page. `tests/test_docs_examples.py` checks this.
7. `scripts/extract_cldr.py` writes `text2spoken/data/cldr/`. Change the script and run it again. See [the CLDR data](docs/development.md#the-cldr-data).
8. A pull request does not change `text2spoken/version.py`, because the release workflows set the version from the conventional commit titles. See [CI](docs/development.md#ci).

## Before a push

1. Run `pytest tests`.
2. If you changed an output that a docs page shows, run the example again and paste the new output into the page.
3. For each page that you changed, or whose code you changed, run `python scripts/check_doc_page.py <page>`.
4. Give the commit a conventional title, because the release workflows read it.
