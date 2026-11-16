# Development

This page is for maintainers: how to run the tests, write the row files, keep the docs true, refresh the CLDR data and release.

## Set up and run the tests

```bash
uv venv
uv pip install --prerelease=allow -e ".[test]"
pytest tests
```

The `test` extra installs the dependencies of every language extra, so the suite runs every language file.

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

`tests/data/electronic/pt.tsv` holds the Portuguese address rows. They run on the stub language `tests/fixtures/pt_electronic.py`, which has the address tables of `text2spoken/lang/_pt_electronic.py` and no other form. `tests/fixtures/qac.py` is a stub language whose rows, in `tests/fixtures/qac.tsv`, run beside the rows of each shipped file.

## Other tests

| Test | What it checks |
| --- | --- |
| `tests/test_contract.py` | Each clause of the [language file contract](adding-a-language.md#the-contract), on every file, and that each clause check fails on a broken file |
| `tests/test_table_mutation.py` | That dropping one entry of each table of a language file fails a row. A new language file adds its entries to `ENTRIES` |
| `tests/test_properties.py` | Determinism, inline blocks byte for byte, text outside the spans unchanged, params that do not affect each other, and an import that loads no language file |
| `tests/test_errors.py`, `tests/test_effective_params.py`, `tests/test_gender.py` | The errors and warnings of [Errors and warnings](errors.md): the failure policy and the lexicon, a param value that a language cannot produce, and the genders |
| `tests/test_round_trip.py` | That `ovos-number-parser` parses each English cardinal back to its number. This proves self-consistency only, and never replaces a cited row |
| `tests/test_docs_examples.py` | That each example in `README.md` and `docs/` is the output of a real run, and that each link resolves |

## Keep the docs true

`tests/test_docs_examples.py` runs every example of the docs, so CI fails when a change of the code changes an output that a page shows. It checks three kinds of example:

- A `python` code block with `>>>` lines runs as a doctest. The blocks of one page share one namespace.
- A table with a `Written` column holds examples. Each column whose header holds `Spoken` or `Second pass` must equal the output of `normalize`. The header, or a `Tag` column, gives the tag in backticks. A form name in backticks with `on` or `off` after it, such as `` `EMOJI` on ``, and a param in backticks, such as `` `clock="24h"` ``, give the params. A cell that says `stays as written` expects the text unchanged.
- A table whose first column is `Option` gives the values and the defaults of each option, as `supports` and `effective_params` give them.

The test also refuses an output claim in prose: a written form in backticks, the word `reads`, and then words in quotes. No test checks such a claim, so put the example in a table instead. When a change of the code changes an output on purpose, run the example, and paste its new output into the page.

`docs/adding-a-language.md` builds an example language file. A code block whose info string is `python text2spoken/lang/id.py` holds a part of that file, and each doctest after it runs with the file as it stands.

## The CLDR data

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/` from the pinned cldr-json release 49.0.0 and the Unicode 17.0.0 character and emoji files. It fetches the files from GitHub and unicode.org, or reads a local copy:

```bash
python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release
```

`scripts/seed_colors.py en` prints the English colour table, from an `ovos-color-parser` palette, as a Python dict for the `colors` key of the language data. A native speaker checks each table.

## The emoji data

The emoji sequences come from the Unicode 17.0 emoji files, the version whose emoji CLDR 49 names. Some names stay as written, because their reading holds a character that is no word. They hold `&` (en-GB 14, en-US 14), `!` (2 in each tag), `#` and `*` (the keycaps, 1 each in each tag), `/` (pt-PT 2), or a full stop that no abbreviation reads. The full stops are en-US 9, as in `flag: St. Lucia` and `flag: U.S. Virgin Islands`, and pt-PT 6, in `Sra. Natal`. `scripts/extract_cldr.py` prints each such name.

## CI

| Workflow | When | What |
| --- | --- | --- |
| Build Tests | A pull request to `dev` or `master`, and a push to `dev` | Runs `pytest tests` with the `test` extra on Python 3.11, 3.12 and 3.13 |
| License Check | A pull request to `dev` or `master` | Checks the licences of the dependencies |
| Release Alpha and Propose Stable | A merged pull request to `dev` | Publishes an alpha release to PyPI |
| Publish Stable Release | A push to `master` | Publishes a stable release |

The release workflows set the version from the conventional commit titles, so a pull request does not change `text2spoken/version.py`.

---
[← Adding a language](adding-a-language.md) · [Home](index.md)
