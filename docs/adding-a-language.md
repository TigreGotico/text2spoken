# Adding a language

This page shows how to make text2spoken read numbers and dates in your language. It builds a small file for Indonesian, step by step, and ends when every test passes. text2spoken ships no Indonesian file, and the example is not a complete or reviewed reading of Indonesian. Each output on this page comes from a real run of the example.

## Before you start

A language is one file, `text2spoken/lang/<code>.py`, where `<code>` is a primary language subtag such as `id`. The file holds all the logic and all the tables of the language and its varieties. The loader finds each file in `text2spoken/lang/` whose name does not start with `_`, so a new language needs no change to the core.

Every rule cites its source where the rule lives, in the docstring of the language file. A source is a reference grammar, an academy norm, a dictionary entry or CLDR. Another normaliser's output is not a source. This is how the Spanish file cites the rule that reads a date:

```python
def speak_date(span: Span, context: SpanContext) -> str:
    """Day, `de`, the month name, `de`, the year (DPD «fecha», 1.a and 3.c). The first day is `uno` in Spain and
    `primero` in America (DPD «primero», 3)."""
```

A wrong reading is worse than none. If the file cannot read a form for sure, the form stays as written. A form is unsure when it has two readings that the context does not choose between. A form with one reading that a speaker reads with ease must read, and the file quotes a source for that reading. To leave such a form as written is a bug, and it gets an issue.

Set up a checkout with the test extra, as [Development](development.md#set-up-and-run-the-tests) shows. The commands on this page run from the root of the checkout.

## Step 1: see what your language reads now

A language with no file reads cardinal numbers and decimals, from `ovos-number-parser` where it has a module for the language and from the CLDR spell-out rules elsewhere, and nothing else. It reads the decimal mark `,` and the group mark `.` that CLDR gives `id`, so `1.250` reads. The date stays as written:

```python
>>> from text2spoken import normalize, supports
>>> normalize("Saya punya 3 kucing dan 1.250 buku pada 12/03/2024.", "id")
'Saya punya tiga kucing dan seribu dua ratus lima puluh buku pada 12/03/2024.'
>>> sorted(form.name for form in supports("id").forms)
['CARDINAL', 'DECIMAL', 'LEXICON']
```

The library also logs a WARNING for each written form that stays as written. In a Python session, this line appears on stderr:

```text stderr
unread written form '12/03/2024.' for id-ID
```

Each such line names a form that a file for the language could read. [Errors and warnings](errors.md#when-a-reading-stays-as-written) explains the log.

## Step 2: write the smallest file

Create the file `text2spoken/lang/id.py` with this text. The file exports one name, `LANGUAGE`, a `LanguageSpec`:

```python text2spoken/lang/id.py
"""Indonesian: id-ID.

Number words come from CLDR RBNF, the `spellout-cardinal` rule set of `id`. The decimal mark `,` and the group mark
`.` come from the CLDR 49 number symbols of `id`.
"""
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import SHARED, speak_cardinal, speak_lexicon
from text2spoken.core.spans import Features
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.params import OPTIONS, Form, freeze

SPELLER = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
})

LANGUAGE = LanguageSpec(
    code="id", serves=(), cldr_aliases=(), varieties=(Variety("id-ID"),), data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER},
    genders=frozenset(), default_gender=None, animacies=frozenset(), noun_classes=frozenset(),
    numeral_systems=frozenset(), context_words=True, options={}, not_applicable=frozenset(OPTIONS),
)
```

Each part has one job:

- The docstring names the source of each rule.
- `SPELLER` turns digits into words. `RbnfSpeller` reads the CLDR spell-out rules, and its arguments name the rule sets.
- `DATA` holds the tables of the language, as JSON values only. `number_marks` gives the decimal mark and the group mark of the Latin digits.
- `recognizers` finds the written forms, in order. `SHARED` holds the recognizers of the core, by name.
- `verbalizers` gives one verbalizer for each form that a recognizer claims, and `spellers` one speller for each form that speaks a number.
- Indonesian has no grammatical gender, so `genders` is empty and `default_gender` is `None`. The file offers no option yet, so every option is in `not_applicable`.

Run it. The file reads the same numbers, with the group mark of its own table:

```python
>>> normalize("Saya punya 3 kucing dan 1.250 buku pada 12/03/2024.", "id")
'Saya punya tiga kucing dan seribu dua ratus lima puluh buku pada 12/03/2024.'
```

## Step 3: add a date form

A date needs the month names and a verbalizer that puts the words in order. The shared recognizer `date_numeric` finds `12/03/2024` and `2024-03-12`, and gives the day, the month and the year as fields. The [shared recognizers](#the-shared-recognizers-and-verbalizers) table lists the other forms that the core can find for you.

This block holds only the parts of the file that change. Each part replaces the part of the same name in your file: the docstring, the import from `text2spoken.core.spans`, `DATA` and `LANGUAGE`. `speak_date` is new, so put it above `LANGUAGE`. Add to `text2spoken/lang/id.py`:

```python +text2spoken/lang/id.py
"""Indonesian: id-ID.

Number words come from CLDR RBNF, the `spellout-cardinal` rule set of `id`. The decimal mark `,` and the group mark
`.` come from the CLDR 49 number symbols of `id`.

A date reads in the order of the CLDR 49 long date pattern of `id`, `d MMMM y`, with the wide month names of the
CLDR 49 `id` Gregorian calendar. The day and the year read as cardinal numbers.
"""
from text2spoken.core.spans import Features, Span, SpanContext

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "months": ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
               "November", "Desember"],
})


def speak_date(span: Span, context: SpanContext) -> str:
    request = context.request
    day = SPELLER.cardinal(str(span.fields["day"]), Features(), request)
    month = request.data["months"][span.fields["month"] - 1]
    year = SPELLER.cardinal(str(span.fields["year"]), Features(), request)
    return f"{day} {month} {year}"


LANGUAGE = LanguageSpec(
    code="id", serves=(), cldr_aliases=(), varieties=(Variety("id-ID"),), data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["date_numeric"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER},
    genders=frozenset(), default_gender=None, animacies=frozenset(), noun_classes=frozenset(),
    numeral_systems=frozenset(), context_words=True, options={}, not_applicable=frozenset(OPTIONS),
)
```

The order of `recognizers` is the claim order: when two recognizers find the same characters, the earlier one takes them. Run it:

```python
>>> normalize("Rapat pada 12/03/2024.", "id")
'Rapat pada dua belas Maret dua ribu dua puluh empat.'
>>> normalize("Rapat pada 2024-03-12.", "id")
'Rapat pada dua belas Maret dua ribu dua puluh empat.'
```

## Step 4: add test rows

Real sentences are the tests. Create the file `tests/data/id.tsv`, with one row for each form. A tab separates the columns:

```text tests/data/id.tsv
id	tag	form	text	expected	source	checked_by
id-001	id-ID	cardinal	Saya punya 3 kucing.	Saya punya tiga kucing.	CLDR 49 RBNF id: spellout-cardinal	unchecked
id-002	id-ID	date	Rapat pada 12/03/2024.	Rapat pada dua belas Maret dua ribu dua puluh empat.	CLDR 49 id: the long date pattern d MMMM y and the wide month names; silver: no source gives the cardinal day	unchecked
```

Write the `expected` value from your source, never from a run of the code. The `source` column names the source. A reading that no source holds is marked `silver`, as the day of `id-002` is: the example cites CLDR for the order and the month names, and no grammar for the cardinal day. Before a real file reads dates, it cites a grammar for this rule. `checked_by` names the native speaker who checked the row, or says `unchecked`. [Development](development.md#the-row-files) gives every column.

## Step 5: run the contract test

`tests/test_contract.py` checks each of the 12 clauses of the contract on every language file. The selector `-k "id-clause"` runs the 12 checks of your file only:

```bash
pytest tests/test_contract.py -k "id-clause"
```

One clause fails. The output holds these lines:

```text output
E           AssertionError: id-ID: no ['digit_words', 'leads', 'sign_words', 'symbols'], which its shared recognizers and verbalizers read
FAILED tests/test_contract.py::test_language_file_passes[id-clause_6]
1 failed, 11 passed
```

The last line also counts the deselected tests and gives the time. Those numbers change with each language file, so this page leaves them out.

Clause 6 failed. The shared `cardinal` recognizer and `speak_cardinal` read four tables that `DATA` does not have. The core reads each table with `data.get`, so a missing table turns a rule off with no error. The calls of steps 2 and 3 worked, but a negative number such as `-5` stays as written, and so does a number with a leading zero after a lead word, such as `No. 007`.

## Step 6: fix it

`sign_words` gives the word of the minus sign, and `leads` gives the words that a number can follow, such as `No. `. `digit_words` reads a number with a leading zero after a lead, digit by digit. `symbols` gives the characters that belong to other forms, and it stays empty here.

This block holds the docstring, with the sources of the new tables, and `DATA`, with the four tables. Each replaces the part of the same name in your file. Add to `text2spoken/lang/id.py`:

```python +text2spoken/lang/id.py
"""Indonesian: id-ID.

Number words come from CLDR RBNF, the `spellout-cardinal` rule set of `id`. The decimal mark `,` and the group mark
`.` come from the CLDR 49 number symbols of `id`. The digit words of `digit_words` are the words of 0 to 9 in that
rule set, and the minus sign reads "negatif", as its negative rule writes.

A date reads in the order of the CLDR 49 long date pattern of `id`, `d MMMM y`, with the wide month names of the
CLDR 49 `id` Gregorian calendar. The day and the year read as cardinal numbers.
"""

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "digit_words": ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"],
    "sign_words": {"-": "negatif"},
    "leads": {"No. ": "nomor"},
    "symbols": {},
    "months": ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
               "November", "Desember"],
})
```

```python
>>> normalize("Suhu -5 derajat.", "id")
'Suhu negatif lima derajat.'
>>> normalize("Kamar No. 007.", "id")
'Kamar nomor nol nol tujuh.'
```

Each new table needs a row that reads it. Add to `tests/data/id.tsv`:

```text +tests/data/id.tsv
id-003	id-ID	cardinal	Ada 1.250 buku.	Ada seribu dua ratus lima puluh buku.	CLDR 49 id: the group mark .; CLDR 49 RBNF id: spellout-cardinal	unchecked
id-004	id-ID	cardinal	Suhu -5 derajat.	Suhu negatif lima derajat.	CLDR 49 RBNF id: the negative rule of spellout-cardinal	unchecked
id-005	id-ID	cardinal	Kamar No. 007.	Kamar nomor nol nol tujuh.	CLDR 49 RBNF id: the words of 0 to 9; silver: no source read for No. as nomor	unchecked
```

Run the contract test again:

```bash
pytest tests/test_contract.py -k "id-clause"
```

```text output
12 passed
```

## Step 7: pass the other checks

Two more test files check every language file. The row test runs each row, and checks that the rows cover the file. The selector `-k "[id] or id-0"` runs the tests of your file and of your rows only:

```bash
pytest tests/test_rows.py -k "[id] or id-0"
```

```text output
E           AssertionError: 16:9
FAILED tests/test_rows.py::test_rows_cover_every_form_and_variety[id]
1 failed, 15 passed
```

The rows of each file must cover each form that the file declares, except `LEXICON`, and each variety. They must also hold four texts that stay as written: `16:9`, `3:16`, `#decade` and `13/13/2024`. These guard rows prove that the file does not read a ratio, a verse, a hashtag or a date that does not exist. Add to `tests/data/id.tsv`, with the form `none`:

```text +tests/data/id.tsv
id-006	id-ID	none	Rasio 16:9 dan ayat 3:16.	Rasio 16:9 dan ayat 3:16.	text2spoken-design section 4.2: the file reads no time	unchecked
id-007	id-ID	none	Tagar #decade.	Tagar #decade.	text2spoken-design section 4.2: # is no lead in id	unchecked
id-008	id-ID	none	Tanggal 13/13/2024.	Tanggal 13/13/2024.	text2spoken-design section 4.2: no month 13	unchecked
```

```bash
pytest tests/test_rows.py -k "[id] or id-0"
```

```text output
25 passed
```

Then run the mutation test. It drops one entry of each table and checks that a row fails, which proves that each table reaches a row:

```bash
pytest tests/test_table_mutation.py -k "[id] or id-"
```

```text output
E       AssertionError: assert {'symbols'} == {'digit_words...s', 'symbols'}
FAILED tests/test_table_mutation.py::test_every_table_has_an_entry_to_drop[id]
1 failed
```

The test needs one entry of each table to drop. `symbols` needs no entry, because only strict mode reads it. Add to `tests/test_table_mutation.py` this line, inside the `ENTRIES` dict:

```python +tests/test_table_mutation.py
    "id": {"number_marks": "Latn", "digit_words": "nol", "sign_words": "-", "leads": "No. ", "months": "Maret"},
```

```bash
pytest tests/test_table_mutation.py -k "[id] or id-"
```

```text output
6 passed
```

## Step 8: finish

1. A file that reads with `RbnfSpeller` or `OvosNumberSpeller` needs no extra, because the base install holds `unicode-rbnf`, `ovos-number-parser` and `ovos-date-parser`. If the file imports another package, add it to an extra with the name of the language code in `pyproject.toml`, and to the `test` extra. Import it inside a function. Clause 12 accepts only the modules that `tests/contract.py` names, so add the module to `LAZY_ONLY` and to `DISTRIBUTIONS` in that file.
2. Run the whole suite with `pytest tests`. Every test passes.
3. Add a page for the language to `docs/languages/`, in the template of the other language pages: what it reads, its varieties, its options, its sources and its limits. Give what it reads and its limits in tables with a `Written` column, and give all eight options in the options table. The docs check runs these examples, and a new language page needs at least 10 of them. Then run `pytest tests` again.
4. Add the language to the tables of `README.md` and `docs/index.md`.

## The finished file

After the steps above, `text2spoken/lang/id.py` holds this text:

```python text2spoken/lang/id.py
"""Indonesian: id-ID.

Number words come from CLDR RBNF, the `spellout-cardinal` rule set of `id`. The decimal mark `,` and the group mark
`.` come from the CLDR 49 number symbols of `id`. The digit words of `digit_words` are the words of 0 to 9 in that
rule set, and the minus sign reads "negatif", as its negative rule writes.

A date reads in the order of the CLDR 49 long date pattern of `id`, `d MMMM y`, with the wide month names of the
CLDR 49 `id` Gregorian calendar. The day and the year read as cardinal numbers.
"""
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import SHARED, speak_cardinal, speak_lexicon
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.params import OPTIONS, Form, freeze

SPELLER = RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"})

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "digit_words": ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"],
    "sign_words": {"-": "negatif"},
    "leads": {"No. ": "nomor"},
    "symbols": {},
    "months": ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
               "November", "Desember"],
})


def speak_date(span: Span, context: SpanContext) -> str:
    request = context.request
    day = SPELLER.cardinal(str(span.fields["day"]), Features(), request)
    month = request.data["months"][span.fields["month"] - 1]
    year = SPELLER.cardinal(str(span.fields["year"]), Features(), request)
    return f"{day} {month} {year}"


LANGUAGE = LanguageSpec(
    code="id", serves=(), cldr_aliases=(), varieties=(Variety("id-ID"),), data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["date_numeric"], SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.CARDINAL: speak_cardinal},
    spellers={Form.CARDINAL: SPELLER},
    genders=frozenset(), default_gender=None, animacies=frozenset(), noun_classes=frozenset(),
    numeral_systems=frozenset(), context_words=True, options={}, not_applicable=frozenset(OPTIONS),
)
```

```python
>>> normalize("Pada 17/08/1945, 3 orang datang ke kamar No. 007.", "id")
'Pada tujuh belas Agustus seribu sembilan ratus empat puluh lima, tiga orang datang ke kamar nomor nol nol tujuh.'
```

The stub language [`tests/fixtures/qac.py`](../tests/fixtures/qac.py) is another complete file of about 40 lines, which the tests run beside every shipped file. It reads cardinals and lexicon entries with invented words.

## Reference

### The fields of `LanguageSpec`

`LanguageSpec` comes from `text2spoken.core.language`.

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

### The shared recognizers and verbalizers

`SHARED` in `text2spoken.core.recognizers` holds the recognizers of the core, by name. To add a form, put its recognizer in `recognizers`, and give `DATA` each key that the recognizer needs. Clause 6 fails when a needed key is missing, as Step 5 shows. An optional key that the file leaves out means that the language has no such words. A form with no shared verbalizer, such as `DATE`, needs a verbalizer in the file, as `speak_date` is in Step 3.

| Recognizer | Form | Needed data keys | Optional data keys |
| --- | --- | --- | --- |
| `lexicon` | `LEXICON` | none | none |
| `cardinal` | `CARDINAL` | `leads`, `number_marks`, `sign_words`, `symbols` | `case_suffixes`, `proclitics` |
| `decimal` | `DECIMAL` | `number_marks`, `symbols` | `case_suffixes`, `proclitics` |
| `fraction` | `FRACTION` | `number_marks`, `symbols`, `unit_symbols`, `units` | `case_suffixes`, `number_gaps`, `proclitics` |
| `idiom` | `IDIOM` | `idioms` | `case_suffixes`, `proclitics` |
| `range` | `RANGE` | `number_marks`, `symbols` | `case_suffixes`, `proclitics`, `range_marks` |
| `date_numeric` | `DATE` | `symbols` | `case_suffixes`, `proclitics` |
| `time_clock` | `TIME` | `clock_marks`, `time_words` | `day_periods`, `range_marks`, `range_word`, `time_suffixes` |
| `percent` | `PERCENT` | `number_marks`, `percent` | `case_suffixes`, `number_gaps`, `proclitics`, `range_marks`, `range_word` |
| `money` | `MONEY` | `currencies`, `currency_symbols`, `number_marks`, `scales` | `case_suffixes`, `number_gaps`, `proclitics`, `range_marks`, `range_word` |
| `kept_money` | `MONEY` | `currencies`, `currency_symbols`, `number_marks`, `symbols` | `case_suffixes`, `number_gaps`, `proclitics`, `symbol_names` |
| `measure` | `MEASURE` | `dimension_marks`, `number_marks`, `symbols`, `unit_symbols`, `units` | `case_suffixes`, `elision_marks`, `number_gaps`, `proclitics`, `range_marks`, `unjoined_symbols` |
| `telephone` | `TELEPHONE` | `currencies`, `currency_symbols`, `leads`, `list_links`, `no_phone_shapes`, `operators`, `phone_kept_shapes`, `phone_shapes`, `phone_unit_shapes`, `phone_words`, `short_codes`, `symbols`, `unit_symbols`, `units` | `case_suffixes`, `day_periods`, `function_words`, `proclitics`, `symbol_names` |
| `expression` | `EXPRESSION` | `number_marks`, `operators`, `patterns`, `symbols` | none |
| `abbreviation` | `ABBREVIATION` | `abbreviations`, `number_abbreviations`, `sentence_final`, `titles` | none |
| `space_groups` | `CARDINAL` | none | none |
| `color` | `COLOR` | `color_words` | none |
| `electronic` | `ELECTRONIC` | `electronic_schemes`, `electronic_tlds` | none |
| `letters` | `LETTERS` | `letter_codas`, `letter_names`, `letter_onsets`, `letter_vowels` | `letter_free_consonants`, `letter_label_nouns`, `letter_runs`, `letter_words` |
| `symbol` | `SYMBOL` | `currencies`, `currency_symbols`, `leads`, `operators`, `symbols`, `unit_symbols`, `units` | `symbol_names` |
| `emoji` | `EMOJI` | `currencies`, `currency_symbols`, `leads`, `operators`, `symbols`, `unit_symbols`, `units` | `symbol_names` |

Of `units` and `unit_symbols`, and of `currencies` and `currency_symbols`, a file gives at least one. `proclitics` and `case_suffixes` give the words that a language joins to a number, such as an article or a case ending.

The shared verbalizers read these keys:

| Verbalizer | Needed data keys | Optional data keys |
| --- | --- | --- |
| `speak_cardinal` | `digit_words`, `leads`, `sign_words` | none |
| `speak_lexicon` | none | none |
| `speak_electronic` | `digit_words`, `electronic_schemes`, `electronic_symbols`, `electronic_vowels`, `letter_names` | `electronic_labels`, `symbol_names` |
| `speak_letters` | `digit_words`, `letter_codas`, `letter_names`, `letter_onsets`, `letter_vowels` | `letter_free_consonants`, `letter_runs` |
| `speak_decimal` | `sign_words` | none |
| `speak_fraction` | `sign_words` | `mixed_half`, `mixed_word` |
| `speak_ordinal` | none | none |
| `speak_range` | none | `range_word` |
| `speak_percent` | `percent`, `sign_words` | none |
| `speak_expression` | `operators`, `sign_words` | none |
| `speak_telephone` | `digit_words`, `sign_words` | none |
| `speak_abbreviation` | `abbreviations`, `number_abbreviations`, `titles` | none |
| `speak_idiom` | `idioms` | none |
| `speak_color` | `digit_words` | `colors` |

`speak_fraction` reads a mixed number of a half, such as `2 1/2`, when the file gives `mixed_word` and `mixed_half`. `mixed_word` is the word between the two parts. `mixed_half` gives the half by gender, with the key `other` for any other gender or none. Portuguese gives `"mixed_word": "e"` and `"mixed_half": {"feminine": "meia", "other": "meio"}`. A file without these keys keeps every mixed number as written.

`READERS` and `OPTIONAL` in `tests/data_keys.py` list the same keys, and `SHAPES` gives the shape of each key.

### The contract

`tests/test_contract.py` checks each clause for every file in `text2spoken/lang/`, and checks that each clause check fails on a broken file.

| Clause | Rule | Why |
| --- | --- | --- |
| 1 | The file defines `LANGUAGE`, and `LANGUAGE.code` equals the file name. | The name of the file and the code that the loader registers are then the same. |
| 2 | `code` and each variety tag are valid BCP 47 tags in their standard form. | A tag in another form never matches the standard tag that a caller's tag becomes. |
| 3 | The loader gives this file for `code` and for each code in `serves`, and for no other code. No code belongs to two files. | One tag then always selects one file. |
| 4 | Each form that a recognizer claims has a verbalizer. Each verbalizer that speaks a number has a speller for its form. | A span that a recognizer finds can then always be read. |
| 5 | Each recognizer emits exactly the fields of its form. A sentence of the test rows reaches each recognizer. | The verbalizers and the callers of `analyze` read the fields by name. |
| 6 | `data` and the data of each variety hold only JSON values: strings, numbers, booleans, lists and objects. Each key that the core reads has the shape that `tests/data_keys.py` declares. The data holds each key that the shared recognizers and verbalizers of the file read, as `READERS` in that file names them. | The core reads each key with `data.get`, so a key with a wrong name or shape turns a rule off with no error. |
| 7 | Each regex in the data uses the portable subset of the regex syntax. | A pattern then means the same in every regex engine. In Python, `\d` matches every Unicode digit, and in other engines it matches only `0` to `9`. |
| 8 | Each option is in `options` or in `not_applicable`, never in both and never in neither. A language with no genders lists `default_gender` in `not_applicable`. A language with genders has its `default_gender` in `genders`. The `defaults` of each variety give a valid value for each option in `options`, except `default_gender` and `phone_regions`. | `supports` and `effective_params` can then tell a caller what each option does in the language. |
| 9 | For each two values of a declared gender, animacy, noun class or numeral system, the cardinal speller gives a different word for 1 or 2, in at least one case. A test row holds a word that only that value gives. | A declared distinction is then real, and a row shows each value. |
| 10 | With `context_words=False`, each test row gives the same output when the context words are empty. | The file then reads no context words, as it declares. |
| 11 | For each variety, the core finds CLDR plural rules, and it finds an RBNF locale for each RBNF speller that the file names. | The data that the file needs then exists for each variety, and a call does not fail on a missing locale. |
| 12 | Importing the file reads no file, opens no network connection and changes no state outside the module. It imports only the core, its own private modules such as `_pt_electronic`, the standard library and the declared dependencies. It never imports another language file. An optional dependency is imported inside a function, behind the extra of the language. | The loader imports every language file, so one file that needs a missing package or the network would break every language. |

---
[← Chinese](languages/zh.md) · [Home](index.md) · [Development →](development.md)
