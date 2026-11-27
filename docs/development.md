# Development

<!-- agent-hint
covers: how to run the tests, write the row files, keep the docs true, refresh the CLDR data and release.
source: .github/workflows/, tests/test_rows.py, tests/test_docs_examples.py, scripts/extract_cldr.py
generated: no
verify: `python scripts/check_doc_page.py docs/development.md`
see: ../AGENTS.md, adding-a-language.md
-->

This page is for maintainers: how to run the tests, write the row files, keep the docs true, refresh the CLDR data and release. [AGENTS.md](../AGENTS.md) gives the short list of rules that a pull request must meet.

## Set up and run the tests

```bash
git clone https://github.com/TigreGotico/text2spoken
cd text2spoken
uv venv
source .venv/bin/activate
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

The `test` extra installs `tugalex` and the test tools, so the suite runs every language file. `source .venv/bin/activate` puts `pytest` on your path. In a new shell, run it again before you run the tests.

## The row files

Real sentences are the tests. Each language file has one TSV file, `tests/data/<code>.tsv`, with these columns:

| Column | Value |
| --- | --- |
| `id` | A unique id, such as `pt-012` |
| `tag` | The language tag of the call |
| `form` | The form that the row tests. A row that must stay as written gives the form that it guards against, or `none` |
| `text` | The written sentence |
| `expected` | The spoken sentence |
| `source` | The source of the expected reading |
| `checked_by` | The native speaker who checked the row, or `unchecked` |

Each expected value comes from a cited rule, from arithmetic done by hand, or from a native speaker, never from a run of the code. A reading that no source holds is marked `silver` in the `source` column. A row of the `letters` or `emoji` form runs with its form on.

`tests/test_rows.py` runs each row, and checks that a second pass changes nothing. A row whose source holds the words `README limit` is a known exception to the second-pass rule, and `tests/known_limits.py` names each such case. The test also checks that each language file has a row file, and that the rows of a file cover each form that the file declares, except `LEXICON`, and each variety. The rows of each file must also hold four texts that stay as written, in rows whose expected value equals the text: `16:9`, `3:16`, `#decade` and `13/13/2024`.

`tests/fixtures/qac.py` is a stub language whose rows, in `tests/fixtures/qac.tsv`, run beside the rows of each shipped file.

## Other tests

| Test | What it checks |
| --- | --- |
| `tests/test_contract.py` | Each clause of the [language file contract](adding-a-language.md#the-contract), on every file, and that each clause check fails on a broken file |
| `tests/test_table_mutation.py` | That dropping one entry of each table of a language file fails a row. A new language file adds its entries to `ENTRIES` |
| `tests/test_properties.py` | Determinism, inline blocks byte for byte, text outside the spans unchanged, params that do not affect each other, and an import that loads no language file |
| `tests/test_errors.py`, `tests/test_effective_params.py`, `tests/test_gender.py` | The errors and warnings of [Errors and warnings](errors.md): the failure policy and the lexicon, a param value that a language cannot produce, and the genders |
| `tests/test_round_trip.py` | That `ovos-number-parser` parses each English cardinal back to its number. This proves self-consistency only, and never replaces a cited row |
| `tests/test_docs_examples.py` | That each example in `README.md` and `docs/` is the output of a real run, and that each link resolves |
| `tests/test_doc_pages.py` | That each page with an agent hint calls `scripts/check_doc_page.py` from its `verify` line, and that the script passes on the page |

## Keep the docs true

`tests/test_docs_examples.py` runs every example of the docs, so CI fails when a change of the code changes an output that a page shows. When the change is on purpose, run the example and paste its new output into the page.

These are the examples that the test runs:

- A `python` code block with `>>>` lines runs as a doctest. The blocks of one page share one namespace. A `text stderr` block after a doctest holds the log lines that the doctest writes, and the test compares them.
- A table with a `Written` column holds examples. Each column whose header holds `Spoken` or `Second pass` must equal the output of `normalize`. The header, or a `Tag` column, gives the tag in backticks. A form name in backticks with `on` or `off` after it, such as `` `EMOJI` on ``, and a param in backticks, such as `` `clock="24h"` ``, give the params. A cell that says `stays as written` expects the text unchanged.
- A table whose first column is `Option` gives the values and the defaults of each option, as `supports` and `effective_params` give them.

The test also holds the docs to these rules:

- A table with a `Spoken` or `Second pass` column must have a `Written` column, because the test runs only the rows of such a table.
- An output claim in prose fails: a written form in backticks, the word `reads`, and then words in quotes or guillemets. Put the example in a table instead.
- Each page holds at least the number of examples that `MINIMUM` gives for it, so a page that loses its examples fails. A new page in `docs/` needs an entry in `MINIMUM`. A language page that `MINIMUM` does not list needs at least `LANGUAGE_MINIMUM` examples: one row of what the file reads, the values of the eight options and one limit.
- A language page gives no number of rows of its file in `tests/data`, so a pull request that adds rows does not change the page.
- Each relative link names a file that exists, and each anchor a heading of that file.

`scripts/check_doc_page.py` checks named prose values of a page against the code, such as the languages that offer a form, the empty extras or the CLDR release. Its docstring lists the sentences and tables that it reads for each page. It reads no other prose, so the docs test is the only check of the rest, and some prose has no check: the signature table of `docs/api.md` and the case table of `docs/errors.md`. The script runs the docs test of the page first, and it exits 1 with the first value that is not true. The `verify` line of the agent hint of each page calls it, and `tests/test_doc_pages.py` runs it on each such page:

```bash
python scripts/check_doc_page.py docs/numbers.md
```

`docs/adding-a-language.md` builds the example language `id`. The test follows the page on a copy of the checkout:

- A code block whose info string is `python text2spoken/lang/id.py` holds the whole file. An info string with a `+` before the path, such as `python +text2spoken/lang/id.py`, holds a part of the file, and the paragraph before the block says "Add to" and the path in backticks. The test puts each statement of the part in place of the statement of the same name, and a statement with a new name before `LANGUAGE`. A `text tests/data/id.tsv` block writes the test rows, and a `text +tests/data/id.tsv` block adds rows. A `python +tests/test_table_mutation.py` block adds a line to `ENTRIES`.
- Each doctest runs with the file as it stands at that step, and each test row must read as its expected value.
- A `bash` block that starts with `pytest` runs in the copy. The `text output` block after it holds lines of the real output: the `E` lines, the start of the `FAILED` lines and the counts of the last line. Each command has one output block.
- The last whole file must equal the sum of the steps.
- The tables of the shared recognizers and verbalizers must give the data keys that `READERS` and `OPTIONAL` in `tests/data_keys.py` give.
- The checkout must not ship `text2spoken/lang/id.py`, so that a reader starts from a language with no file. A reader's copy of the finished file passes. If a file for `id` ships, move the walk-through to a language that still has no file.

## The CLDR data

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/` from the pinned cldr-json release 49.0.0 and the Unicode 17.0.0 character and emoji files. It fetches the files from GitHub and unicode.org, or reads a local copy:

```bash
python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release
```

`scripts/seed_colors.py en` prints the English colour table, from an `ovos-color-parser` palette, as a Python dict for the `colors` key of the language data. A native speaker checks each table.

## The emoji data

The emoji sequences come from the Unicode 17.0 emoji files, the version whose emoji CLDR 49 names. Some names stay as written, because their reading holds a character that is no word. Such a name holds `&`, `!`, `/`, the `#` or the `*` of a keycap, or a full stop that no abbreviation reads, as in `flag: St. Lucia`. `scripts/extract_cldr.py` prints each such name.

## CI

| Workflow | When | What |
| --- | --- | --- |
| Build Tests | A pull request to `dev` or `master`, and a push to `dev` | Runs `pytest tests` with the `test` extra on Python 3.11, 3.12 and 3.13 |
| License Check | A pull request to `dev` or `master` | Checks the licences of the dependencies |
| Release Alpha and Propose Stable | A merged pull request to `dev` | Publishes an alpha release to PyPI |
| Publish Stable Release | A push to `master` | Publishes a stable release |

The release workflows set the version from the conventional commit titles, so a pull request does not change `text2spoken/version.py`. [CHANGELOG.md](../CHANGELOG.md) lists the changes of each release.

---
[← Adding a language](adding-a-language.md) · [Home](index.md)
