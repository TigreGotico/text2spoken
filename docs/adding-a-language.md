# Adding a language

A language is one file, `text2spoken/lang/<code>.py`, where `<code>` is a primary language subtag such as `fr`. The file holds all the logic and all the tables of the language and its varieties. A new language needs no change to the core: the loader finds each file in `text2spoken/lang/` whose name does not start with `_`.

## The file

The file exports one name, `LANGUAGE`, a `LanguageSpec` from `text2spoken.core.language`. Its fields:

| Field | Value |
| --- | --- |
| `code` | The primary language subtag, equal to the file name |
| `serves` | Other primary subtags that the file reads, such as the Arabic varieties of ISO 639-3 in `ar.py` |
| `cldr_aliases` | CLDR locale ids to try after the locale of the tag |
| `varieties` | The `Variety` values, each a tag and the data that differs from the language data. The first is the default |
| `data` | The tables and patterns of the language, as JSON values only |
| `recognizers` | The full claim order: the shared recognizers of the core, by name, and the recognizers of the file |
| `verbalizers` | One verbalizer for each form that a recognizer claims |
| `spellers` | One number speller for each form that speaks a number |
| `genders`, `default_gender` | The genders of the language, empty when it has none, and the gender that applies when nothing else decides |
| `animacies`, `noun_classes`, `numeral_systems` | The values of each dimension, empty when the language has no such distinction |
| `context_words` | `False` when no verbalizer reads the words around a span, as for a script with no word boundaries |
| `options` | The values that each option of `NormalizationParams` can take in the language |
| `not_applicable` | The options that change nothing in the language |
| `attach`, `join_range` | Optional. How a prefix and a suffix join the spoken words, and how two spans join into a range |

The stub language [`tests/fixtures/qac.py`](../tests/fixtures/qac.py) is a complete file of about 40 lines. It reads cardinals and lexicon entries, and shows each field.

## The contract

`tests/test_contract.py` checks each clause for every file in `text2spoken/lang/`:

1. The file defines `LANGUAGE`, and `LANGUAGE.code` equals the file name.
2. `code` and each variety tag are valid BCP 47 tags in their standard form.
3. The loader gives this file for `code` and for each code in `serves`, and for no other code. No code belongs to two files.
4. Each form that a recognizer claims has a verbalizer. Each verbalizer that speaks a number has a speller for its form.
5. Each recognizer emits exactly the fields of its form.
6. `data` and the data of each variety hold only JSON values: strings, numbers, booleans, lists and objects. Each key that the core reads has the shape that `tests/data_keys.py` declares.
7. Each regex in the data uses the portable subset of the regex syntax.
8. Each option is in `options` or in `not_applicable`, never in both and never in neither. A language with no genders lists `default_gender` in `not_applicable`.
9. For each declared gender, animacy, noun class and numeral system, the speller gives a word for 1 or 2 that differs from the word of each other value where the language has distinct forms, and a test row holds it.
10. With `context_words=False`, each test row gives the same output when the context words are empty.
11. For each variety, the core finds CLDR plural rules, and it finds an RBNF locale for each RBNF speller that the file names.
12. Importing the file reads no file, opens no network connection and changes no state outside the module. It imports only the core, its own private modules such as `_pt_electronic`, the standard library and the declared dependencies. It never imports another language file. An optional dependency is imported inside a function, behind the extra of the language.

## Rules and sources

Each rule cites its source where the rule lives, in the docstring of the language file: a reference grammar, an academy norm, a dictionary entry or CLDR. Another normaliser's output is not a source. A wrong reading is worse than none, so a form that the file cannot read for sure stays as written.

## Steps

1. Write `text2spoken/lang/<code>.py`.
2. Add the dependencies of the language to an extra of the same name in `pyproject.toml`, and to the `test` extra.
3. Write `tests/data/<code>.tsv`, with rows for each form and each variety that the file declares. [Development](development.md) gives the format.
4. Add the table entries of the file to `ENTRIES` in `tests/test_table_mutation.py`.
5. Run `pytest tests/test_contract.py tests/test_rows.py tests/test_table_mutation.py`.
6. Add a page for the language to `docs/languages/`, with its varieties, its sources and its limits, and add it to the tables of `README.md` and `docs/index.md`.

---
[← Russian](languages/ru.md) · [Home](index.md) · [Development →](development.md)
