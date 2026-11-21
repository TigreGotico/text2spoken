# Quickstart

<!-- agent-hint
covers: how to install text2spoken, make the first call and see what a tag reads.
source: pyproject.toml, text2spoken/core/language.py:supports
generated: no
verify: `pytest tests/test_docs_examples.py -k quickstart.md && python -c "import tomllib;p=tomllib.load(open('pyproject.toml','rb'))['project'];e=sorted(k for k,v in p['optional-dependencies'].items() if not v);q=chr(96);s=', '.join(q+k+q for k in e[:-1])+' and '+q+e[-1]+q;t=open('docs/quickstart.md').read();assert f'The extras {s} add nothing' in t,s;assert 'Python '+p['requires-python'][2:]+' or later' in t"`
see: usage.md, api.md
-->

This page installs text2spoken, makes the first call, and shows how to see what a language tag reads.

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

The library needs Python 3.11 or later. It uses no network and loads no model. Every language reads with the base install. Portuguese also reads the gender of nouns and given names from `tugalex`, which the `pt` extra adds:

```bash
uv pip install --prerelease=allow "text2spoken[pt]"
```

The extras `ar`, `ca`, `es`, `eu`, `fr`, `it`, `nl` and `ru` add nothing, and an install that names one still works.

## The first call

`normalize(text, lang)` returns the spoken text. `lang` is a BCP 47 tag, for example `en`, `en-GB` or `pt-PT`.

```python
>>> from text2spoken import normalize
>>> normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
>>> normalize("O Dr. Silva pagou 2,50 € às 14:30.", "pt-PT")
'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

The tag selects the language file and the variety. A tag with no region takes the default region of its language, so `en` reads as `en-GB` and `pt` reads as `pt-PT`.

## See what a tag reads

`supports(lang)` returns the forms, genders and option values of a tag:

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

From a shell:

```bash
python -c "from text2spoken import supports; print(supports('en-US'))"
```

## Change the reading

`NormalizationParams` sets the forms to read and the options of each reading. A field that is `None` takes the default of the language variety.

```python
>>> from text2spoken import NormalizationParams
>>> normalize("Meet at 14:30.", "en-GB")
'Meet at two thirty PM.'
>>> normalize("Meet at 14:30.", "en-GB", NormalizationParams(clock="24h"))
'Meet at fourteen thirty.'
```

A form that the library cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger. Set `strict=True` to raise an error instead. [Errors and warnings](errors.md) gives each case.

## Next steps

- [Usage](usage.md) shows how to turn forms off and on, pick a variety, and add your own words.
- [How it reads text](how-it-reads.md) lists each written form.
- [API](api.md) gives each function and each param.

---
[Home](index.md) · [Usage →](usage.md)
