# Development

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
| `form` | The form that the row tests, or `none` for a row that must stay as written |
| `text` | The written sentence |
| `expected` | The spoken sentence |
| `source` | The source of the expected reading |
| `checked_by` | The native speaker who checked the row, or `unchecked` |

Each expected value comes from a cited rule, from arithmetic done by hand, or from a native speaker, never from a run of the code. A reading that no source holds is marked `silver` in the `source` column. A row of the `letters` or `emoji` form runs with its form on.

`tests/test_rows.py` runs each row, and checks that a second pass changes nothing. A row whose source holds the words `README limit` is a known exception to the second-pass rule, and `tests/known_limits.py` names each such case. The test also checks that the rows of a file cover each form and each variety that the file declares, and that each language file has a row file.

`tests/data/electronic/pt.tsv` holds the Portuguese address rows. They run on the stub language `tests/fixtures/pt_electronic.py`, which has the address tables of `text2spoken/lang/_pt_electronic.py` and no other form. `tests/fixtures/qac.py` is a stub language whose rows, in `tests/fixtures/qac.tsv`, run beside the rows of each shipped file.

## Other tests

| Test | What it checks |
| --- | --- |
| `tests/test_contract.py` | Each clause of the [language file contract](adding-a-language.md#the-contract), on every file, and that each clause check fails on a broken file |
| `tests/test_table_mutation.py` | That dropping one entry of each table of a language file fails a row. A new language file adds its entries to `ENTRIES` |
| `tests/test_properties.py` | Determinism, inline blocks byte for byte, text outside the spans unchanged, params that do not affect each other, and an import that loads no language file |
| `tests/test_errors.py` | Each error and warning of [Errors and warnings](errors.md) |
| `tests/test_round_trip.py` | That `ovos-number-parser` parses each English cardinal back to its number. This proves self-consistency only, and never replaces a cited row |

## The CLDR data

`scripts/extract_cldr.py` writes `text2spoken/data/cldr/` from the pinned cldr-json release 49.0.0 and the Unicode 17.0.0 character and emoji files. It fetches the files from GitHub and unicode.org, or reads a local copy:

```bash
python scripts/extract_cldr.py                       # fetch the pinned cldr-json release
python scripts/extract_cldr.py --source ~/cldr-json  # read a checkout of that release
```

`scripts/seed_colors.py` writes the colour tables of the language files from `ovos-color-parser`.

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
