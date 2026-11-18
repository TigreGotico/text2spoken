# API

This page gives each function, param and record of text2spoken. Every name on this page imports from `text2spoken`.

| Function | Returns |
| --- | --- |
| `normalize(text, lang, params=None, tokenizer=None, *, say_as=None)` | The spoken text |
| `analyze(text, lang, params=None, tokenizer=None, *, say_as=None)` | An `Analysis` with the tokens and the spans that the library found |
| `render(analysis, hints=None)` | The spoken text of an `Analysis` |
| `supports(lang)` | A `Support` record: the forms, genders and option values of a tag |
| `effective_params(lang, params=None)` | The params of a call, with the language defaults filled in |
| `revision(lang)` | A string that changes when the output of `normalize` for the language can change |

`lang` is a BCP 47 tag, for example `en`, `en-GB` or `pt-PT`. A tag that is not valid raises `InvalidLanguageTagError`. `normalize(text, lang, params)` gives the same text as `render(analyze(text, lang, params))`.

## normalize

```python
>>> from text2spoken import normalize
>>> normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
```

`params=None` gives `NormalizationParams()`, the defaults of the language variety. `tokenizer=None` gives the default tokenizer.

## say_as

SSML markup can name the form of a run of text, as in `<say-as interpret-as="ordinal">3</say-as>`. Give the attributes of the element as a `SayAs`. The markup is the evidence for the form, so the run reads in that form with no other evidence:

```python
>>> from text2spoken import SayAs
>>> normalize("123", "en-US")
'one hundred twenty-three'
>>> normalize("123", "en-US", say_as=SayAs(interpret_as="ordinal"))
'one hundred twenty-third'
>>> normalize("01/02/1960", "en-US", say_as=SayAs(interpret_as="date", format="dmy"))
'February first nineteen sixty'
>>> normalize("3981900", "en-US", say_as=SayAs(interpret_as="telephone"))
'three nine eight one nine zero zero'
>>> normalize("W3C", "en-US", say_as=SayAs(interpret_as="characters"))
'double-u three see'
>>> normalize("21 people", "en-US", say_as=SayAs(interpret_as="cardinal"))
'twenty-one people'
```

`SayAs` takes `interpret_as`, `format` and `detail`, as the markup writes them. The library strips the white space at their edges and ignores their case.

| `interpret_as` | `format` | `detail` | The run reads |
| --- | --- | --- | --- |
| `cardinal`, `number` | The decimal mark | The group mark | As a number |
| `ordinal` | | | As an ordinal. A run with no ordinal mark takes the `default_gender` |
| `date` | `dmy`, `mdy` or `ymd`: the order of three fields. `y`: a year of four digits | | As a date or a year |
| `time` | `hms24` or `hms12` | | As a clock time, with the `clock` option of the params |
| `telephone` | A country code | | Digit by digit |
| `digits` | | | Digit by digit |
| `characters`, `spell-out`, `letters`, `verbatim` | `characters` | | Letter by letter, and digit by digit |
| `fraction`, `unit`, `currency` | | | As a fraction, a measure or an amount of money |

The rest of the text reads as plain text, as `people` does in the last example. Any other value, such as `address`, gives the plain reading and a `ParameterNotHonouredWarning`. A format or a detail that the language cannot use is dropped with the same warning. When the text holds nothing of the form, as `abc` with `cardinal`, the call gives the plain reading and logs one `WARNING`. With `strict=True`, these cases raise `UnsupportedParameterError` and `UnreadFormError` (see [Errors and warnings](errors.md)). `analysis.request.say_as` shows the say-as that the call read, or `None`.

## analyze and render

`analyze` finds the spans and reads nothing. `render` reads the spans of an `Analysis`. A frontend that knows more about a sentence than the library, such as the gender of a noun, calls the two steps and gives `render` a hint:

```python
>>> from text2spoken import analyze, render
>>> analysis = analyze("Gate 7 opens at 9:15.", "en-US")
>>> [(span.start, span.end, span.form) for span in analysis.spans]
[(5, 6, <Form.CARDINAL: 'cardinal'>), (16, 20, <Form.TIME: 'time'>)]
>>> render(analysis)
'Gate seven opens at nine fifteen.'
```

An `Analysis` has these fields:

| Field | Value |
| --- | --- |
| `text` | The input text |
| `blocks` | The `[[...]]` blocks as `(start, end)` offsets. No span enters a block |
| `tokens` | The tokens, as `Token` values |
| `spans` | The spans in text order, with no overlap, as `Span` values |
| `request` | The tag, the variety, the language file and the effective params of the call. `analysis.request.params` equals `effective_params(lang, params)` |

A `Span` has `start` and `end`, the code point offsets of the span in the text, its `form`, and the `fields` that the form reads. `lead` and `trail` hold punctuation at the edges that stays as written, and `recognizer` names the recognizer that found the span. A span with `keep=True` claims its characters and keeps them as written.

### Grammatical agreement

In many languages a number agrees with its noun. `hints` maps the start offset of a span to `Features`, for example a grammatical gender:

```python
>>> from text2spoken import Features, GrammaticalGender
>>> analysis = analyze("Comprei 2 e paguei 3 €.", "pt-PT")
>>> render(analysis)
'Comprei dois e paguei três euros.'
>>> render(analysis, {8: Features(gender=GrammaticalGender.FEMININE)})
'Comprei duas e paguei três euros.'
```

`Features` has the fields `gender` (a `GrammaticalGender`), `animacy` (an `Animacy`), `noun_class`, `number` (`"singular"`, `"plural"` or `"dual"`), `case`, `numeral_system` and `definite`. Each field is `None` by default. A language names its own cases, noun classes and numeral systems, such as `"genitive"`.

For a German number and a Russian cardinal, a hint replaces all the features that the context of the span gives, so the hint gives each feature that the reading needs. Other readings, such as an Arabic number or a Russian decimal, keep each context feature that the hint does not set. In Russian, the hint below needs the case as well as the gender:

```python
>>> analysis = analyze("в 1 квартире", "ru-RU")
>>> render(analysis, {2: Features(gender=GrammaticalGender.FEMININE, case="prepositional")})
'в одной квартире'
>>> render(analysis, {2: Features(gender=GrammaticalGender.FEMININE)})
'в одна квартире'
```

A hint is data. It does not change which forms the library finds. A hint for a span whose reading takes no features has no effect. A hint at an offset where no span starts gives a `HintWarning`, or `InvalidHintError` in strict mode. A language with no genders ignores a gender in a hint. [Errors and warnings](errors.md#genders) gives the case of a gender that a language does not have.

`GrammaticalGender` has the values `MASCULINE`, `FEMININE`, `NEUTER` and `COMMON`. `Animacy` has the values `ANIMATE`, `INANIMATE` and `PERSONAL`. `supports(lang).genders` and `supports(lang).animacies` give the values that a language reads.

## supports

`supports(lang)` returns a `Support` record:

| Field | Value |
| --- | --- |
| `tag` | The tag with its region, such as `en-GB` for `en` |
| `code` | The code of the language file, such as `en` |
| `forms` | The `Form` values that the language reads |
| `genders`, `animacies`, `noun_classes`, `numeral_systems` | The values of each dimension that the language reads. Each is empty when the language has no such distinction |
| `options` | The values that each option can take in the language |
| `not_applicable` | The options that change nothing in the language |
| `context_words` | `False` when no reading of the language looks at the words around a span |

## effective_params

`effective_params(lang, params)` gives the params that apply to a call. Each `None` becomes the default of the language variety. A value that the language cannot produce becomes the value that applies instead, with a `ParameterNotHonouredWarning`:

```python
>>> from text2spoken import NormalizationParams, effective_params
>>> effective_params("en-US").date_order
'MDY'
>>> effective_params("pt-BR").scale
'short'
```

A test can assert the effective params of a call, with no log to read.

## revision

`revision(lang)` gives a string that changes when the output of `normalize` for the language can change. A caller that keeps spoken text, such as a voice dataset or a phonemizer cache, keeps the revision with it. When the revision of the installed library is different, `normalize` can give a different text:

```python
>>> from text2spoken import revision
>>> revision("pt-PT")[:5]
't2s1:'
>>> revision("pt") == revision("pt-PT")
True
>>> revision("pt-PT") == revision("pt-BR")
False
```

The value is `t2s1:` and a SHA-256 in hex. The hash holds the tag, the language file and the variety. It also holds each distribution that has a module that `normalize` or a number or date writer imports for the language. For each of these distributions, it holds the code tokens of each Python module and the bytes of each data file.

The hash also holds the Unicode version of the interpreter, `unicodedata.unidata_version`, because the library finds digits through `unicodedata`. Each Python minor version has a different Unicode version, so each has a different revision.

A docstring, a comment, a blank line and a `version.py` are not in the hash. A release that changes only these keeps the revision. A refactor that keeps the output can change the revision. A compiled module, such as the C part of `regex`, goes into the hash by its name and the version of its distribution, because its bytes are different on each platform.

The first call for a language takes some seconds. It runs a probe in a new Python process and reads the files of each distribution. Later calls give the stored value. `import text2spoken` computes no revision.

When a module of the output path loads from a zip file, or from another place that is not a directory or a file, `revision` raises `RevisionError`. It names the module and the place. It gives no revision over less than the code.

The probe raises `RevisionError` too when it exits with an error, prints no readable result, or runs longer than 60 seconds, the value of `text2spoken.core.revision.PROBE_TIMEOUT`. The probe prints its result after a marker that is new for each call, so a line that a `sitecustomize` module or an exit handler prints does not change the result.

## Params

`NormalizationParams` is a frozen dataclass. A field that is `None` takes the default of the language variety. The dataclass is hashable, so a caller can cache on it, and one value serves every language.

| Field | Values |
| --- | --- |
| `forms` | The `Form` values to read. The default holds every form except `LETTERS` and `EMOJI`. `params.only(Form.CARDINAL)`, `params.without(Form.TIME)` and `params.plus(Form.LETTERS)` give a changed copy |
| `date_order` | `DMY`, `MDY`, `YMD`: the order of an ambiguous date such as `12/03/2024` |
| `clock` | `12h`, `24h` |
| `minute_style` | `number`, `phrase`: `2:30` as "two thirty" or "half past two" |
| `decimal_mark` | One character, the decimal mark of the written numbers |
| `scale` | `short`, `long`: `10^9` as a billion or a thousand million |
| `default_gender` | A `FrozenMap` of language code to `GrammaticalGender` |
| `register` | `formal`, `colloquial` |
| `phone_regions` | ISO 3166 region codes for telephone number plans. [Numbers](numbers.md#telephone-numbers) shows the evidence that reads a phone number |
| `lexicon` | A `FrozenMap` of language tag to a `FrozenMap` of written form to spoken words. [Usage](usage.md#add-your-own-words) gives the matching rules |
| `strict` | `True` raises an error where the default mode logs a warning |

```python
>>> from text2spoken import Form
>>> normalize("Due 12/03/2024.", "en-GB", NormalizationParams(date_order="MDY"))
'Due the third of December twenty twenty-four.'
>>> normalize("Pagou 1000000000 €.", "pt-PT", NormalizationParams(scale="short"))
'Pagou um bilião de euros.'
>>> normalize("Meet at 2:30.", "en-GB", NormalizationParams(minute_style="phrase"))
'Meet at half past two.'
```

`default_gender` holds one gender for each language, keyed by the code of the language file. It gives the gender of a number when the context gives none:

```python
>>> from text2spoken import FrozenMap
>>> normalize("Comprei 2.", "pt-PT", NormalizationParams(default_gender=FrozenMap({"pt": GrammaticalGender.FEMININE})))
'Comprei duas.'
```

`FrozenMap` is an immutable, hashable mapping, sorted by key. `FrozenMap({"pt": FrozenMap({"ACME": "ácmi"})})` builds a lexicon.

## Your own tokenizer

The `tokenizer` argument takes a callable `(text, lang)` that returns a sequence of `Token(start, end, text)`. Give it when your pipeline already splits text into tokens, so that the spans and the context words follow your tokens. With no tokenizer, the library uses its default, `default_tokenizer`.

```python
>>> import re
>>> from text2spoken import Token
>>> def by_space(text, lang):
...     return [Token(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", text)]
>>> normalize("Pay $5 now.", "en-US", tokenizer=by_space)
'Pay five dollars now.'
```

Each offset counts Unicode code points of the text as the caller gives it. A token must match the text at its offsets, and the tokens must be in order with no overlap. A tokenizer that breaks one of these rules raises `TokenizerError`. A token can set `clause_end=True` to mark the end of a clause, so that no reading looks at the words after it. `Tokenizer` is the protocol of such a callable.

## The tables of a language file

To print the data of a language file as JSON, give a BCP 47 tag. The command prints the language file that `normalize` selects for that tag:

```bash
python -m text2spoken.export en
```

If the tag is not valid, or if no language file reads the tag, the command writes one error line and exits with code 1.

---
[← Addresses, letters and emoji](addresses-letters-and-emoji.md) · [Home](index.md) · [Errors and warnings →](errors.md)
