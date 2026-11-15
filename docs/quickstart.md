# Quickstart

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

The library needs Python 3.11 or later. It uses no network and loads no model. English and German need no extra. Install the extra of each other language that you read:

| Extra | Language | What it adds |
| --- | --- | --- |
| `ar` | Arabic | `ovos-number-parser` |
| `es` | Spanish | `ovos-number-parser` |
| `eu` | Basque | `ovos-number-parser` |
| `pt` | Portuguese | `ovos-number-parser`, `ovos-date-parser` and `tugalex` |
| `ru` | Russian | `ovos-number-parser` |

```bash
uv pip install --prerelease=allow "text2spoken[pt,es]"
```

## The first call

`normalize(text, lang)` returns the spoken text. `lang` is a BCP 47 tag, for example `en`, `en-GB` or `pt-PT`.

```python
from text2spoken import normalize

normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
# 'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
normalize("O Dr. Silva pagou 2,50 € às 14:30.", "pt-PT")
# 'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

The tag selects the language file and the variety. A tag with no region takes the default region of its language, so `en` reads as `en-GB` and `pt` reads as `pt-PT`.

## See what a tag reads

`supports(lang)` returns the forms, genders and option values of a tag:

```python
from text2spoken import Form, supports

support = supports("pt-PT")
support.tag, support.code
# ('pt-PT', 'pt')
Form.ROMAN in support.forms, Form.ELECTRONIC in support.forms
# (True, False)
supports("en").tag, supports("pt").tag
# ('en-GB', 'pt-PT')
```

From a shell:

```bash
python -c "from text2spoken import supports; print(supports('en-US'))"
```

## Change the reading

`NormalizationParams` sets the forms to read and the options of each reading. A field that is `None` takes the default of the language variety.

```python
from text2spoken import NormalizationParams

normalize("Meet at 14:30.", "en-GB")
# 'Meet at two thirty PM.'
normalize("Meet at 14:30.", "en-GB", NormalizationParams(clock="24h"))
# 'Meet at fourteen thirty.'
```

A form that the library cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger. Set `strict=True` to raise an error instead. [Errors and warnings](errors.md) gives each case.

## Next steps

- [Usage](usage.md) shows the reading for a voice, a phonemizer and a word error rate score.
- [How it reads text](how-it-reads.md) lists each written form.
- [API](api.md) gives each function and each param.

---
[Home](index.md) · [Usage →](usage.md)
