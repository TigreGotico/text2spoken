# Quickstart

<!-- agent-hint
covers: how to install text2spoken, make the first call and see what a tag reads.
source: pyproject.toml, text2spoken/core/language.py:supports
generated: no
verify: `python scripts/check_doc_page.py docs/quickstart.md`
see: usage.md, api.md
-->

This page installs text2spoken and makes a first call in four steps. Each step shows the real output.

```python
>>> from text2spoken import normalize
>>> normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
```

## Step 1: install the library

1. Use Python 3.11 or later.
2. Install the package:

   ```bash
   uv pip install --prerelease=allow text2spoken
   ```

3. For Portuguese, install the `pt` extra. It adds `tugalex`, which gives the gender of nouns and given names:

   ```bash
   uv pip install --prerelease=allow "text2spoken[pt]"
   ```

Every language reads with the base install. The library uses no network and loads no model. The extras `ar`, `ca`, `es`, `eu`, `fr`, `it`, `nl` and `ru` add nothing, and an install that names one still works.

## Step 2: make the first call

1. Import `normalize`.
2. Give it the text and a BCP 47 language tag, for example `en`, `en-GB` or `pt-PT`.
3. Read the spoken text that it returns:

```python
>>> normalize("O Dr. Silva pagou 2,50 € às 14:30.", "pt-PT")
'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

The tag selects the language file and the variety. A tag with no region takes the default region of its language, so `en` reads as `en-GB` and `pt` reads as `pt-PT`.

## Step 3: see what a tag reads

1. Import `supports` and `Form`.
2. Call `supports(lang)`. It returns the tag, the language code, and the forms, genders and option values of the tag:

```python
>>> from text2spoken import Form, supports
>>> support = supports("pt-PT")
>>> support.tag, support.code
('pt-PT', 'pt')
>>> Form.ROMAN in support.forms, Form.IDIOM in support.forms
(True, False)
>>> supports("en").tag, supports("pt").tag
('en-GB', 'pt-PT')
```

To see all the facts of a tag from a shell, print the result:

```bash
python -c "from text2spoken import supports; print(supports('en-US'))"
```

## Step 4: change the reading

1. Make a `NormalizationParams` value with the options that you want.
2. Give it to `normalize` as the third argument:

```python
>>> from text2spoken import NormalizationParams
>>> normalize("Meet at 14:30.", "en-GB")
'Meet at two thirty PM.'
>>> normalize("Meet at 14:30.", "en-GB", NormalizationParams(clock="24h"))
'Meet at fourteen thirty.'
```

A field that is `None` takes the default of the language variety. A form that the library cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger. Set `strict=True` to raise an error instead. [Errors and warnings](errors.md) gives each case.

## Next steps

- [Usage](usage.md) shows how to turn forms off and on, pick a variety, and add your own words.
- [How it reads text](how-it-reads.md) lists each written form.
- [API](api.md) gives each function and each param.

---
[Home](index.md) · [Usage →](usage.md)
