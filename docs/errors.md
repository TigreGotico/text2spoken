# Errors and warnings

<!-- agent-hint
covers: each error and warning, in the default mode and in strict mode.
source: text2spoken/errors.py
generated: no
verify: `python scripts/check_doc_page.py docs/errors.md`
see: api.md, languages/ar.md
-->

text2spoken has two modes. The default mode keeps a form that it cannot read as written and logs a warning, so a voice still speaks the sentence. Strict mode, `NormalizationParams(strict=True)`, raises an error instead, so a training pipeline finds each gap.

## Each case

| Case | Default mode | `strict=True` |
| --- | --- | --- |
| An argument, a param field or a hint of the wrong type | `ArgumentTypeError` | `ArgumentTypeError` |
| A param value that no language takes, such as `date_order="mdy"` | `InvalidParameterError` | `InvalidParameterError` |
| A tag that is not a BCP 47 tag | `InvalidLanguageTagError` | `InvalidLanguageTagError` |
| A form that the library cannot read | Stays as written, WARNING logged | `UnreadFormError` |
| A param value that the language cannot produce | Language default, `ParameterNotHonouredWarning` | `UnsupportedParameterError` |
| A `say_as` value, format or detail that the language cannot read | The reading without it, `ParameterNotHonouredWarning` | `UnsupportedParameterError` |
| A `say_as` whose form is not in the text | The reading with no `say_as`, WARNING logged | `UnreadFormError` |
| A `say_as` span that the language cannot speak, such as a German ordinal of one million | The reading with no `say_as`, WARNING logged | `UnreadFormError` |
| A `say_as` `characters` in a language with no letter names | Each letter as written, alone, `ParameterNotHonouredWarning` | `UnsupportedParameterError` |
| A `say_as` `telephone` with a `+` that the language has no word for | The country code without the `+`, WARNING logged | `UnreadFormError` |
| A gender that a language with genders does not have | `UndefinedGrammaticalGender` | `UndefinedGrammaticalGender` |
| A hint at an offset where no span starts | `HintWarning` | `InvalidHintError` |
| A lexicon value that contains a readable form | `InvalidLexiconError` | `InvalidLexiconError` |
| A tokenizer result that is not a sequence of tokens that match the text | `TokenizerError` | `TokenizerError` |
| `revision` finds a module of the output path in a zip file or in another place that is not a directory or a file | `RevisionError` | `RevisionError` |
| The `revision` probe exits with an error, prints no readable result, or runs longer than `PROBE_TIMEOUT` | `RevisionError` | `RevisionError` |

## A form that the library cannot read

In the default mode the form stays as written. In strict mode, `UnreadFormError.unread` holds each run that stays as written:

```python
>>> from text2spoken import NormalizationParams, UnreadFormError, normalize
>>> normalize("The run took 1:23:45.", "en-GB")
'The run took 1:23:45.'
>>> try:
...     normalize("The run took 1:23:45.", "en-GB", NormalizationParams(strict=True))
... except UnreadFormError as error:
...     print(error.unread)
('1:23:45.',)
```

## A param value that the language cannot produce

A param value that the language cannot produce is a problem of the call, not of the text. So the library reports it with the Python `warnings` module, and a caller can turn it into an error with a warnings filter. `effective_params` shows the value that applies:

```python
>>> import warnings
>>> from text2spoken import ParameterNotHonouredWarning
>>> with warnings.catch_warnings():
...     warnings.simplefilter("error", ParameterNotHonouredWarning)
...     try:
...         normalize("Às 14:30.", "pt-PT", NormalizationParams(clock="12h"))
...     except ParameterNotHonouredWarning as warning:
...         print(warning)
'pt-PT' cannot produce clock='12h'; '24h' applies
```

An option that changes nothing in a language, which `supports(lang).not_applicable` lists, has no effect and gives no warning.

## Genders

A language with genders raises `UndefinedGrammaticalGender` for a gender that it does not have, in both modes, because a substitute gender would change the words of the sentence. The error names the language, the value and the genders that the language has:

```python
>>> from text2spoken import FrozenMap, GrammaticalGender, UndefinedGrammaticalGender
>>> try:
...     normalize("Comprei 1.", "pt-PT", NormalizationParams(default_gender=FrozenMap({"pt": GrammaticalGender.NEUTER})))
... except UndefinedGrammaticalGender as error:
...     print(error)
'pt-PT' does not define 'neuter'; it defines ['feminine', 'masculine']
```

A language with no genders ignores a gender in a hint or in `default_gender`. English, Basque and most languages with no file have no genders. A language with no file has the genders of its CLDR ordinal rule sets when CLDR has one for more than one gender, as Hindi and Danish do.

## When a reading stays as written

The library declines a reading that it cannot give for sure. A speller or a verbalizer that cannot read a span that the library found raises `DeclinedReading`. The span then stays as written, and the library logs one WARNING that names the form, the span and the reason. In strict mode, `UnreadFormError` replaces the warning, chained to the cause. A digit or a symbol of a form in `forms` that stays in the output gets the same treatment.

The logger is `logging.getLogger("text2spoken")`. A log warning names the form and the text, so a reader can find each span that the library declined, and each digit or symbol that it left unread. The Spanish file reads no number from 10^42 up, so this number stays as written:

```python
>>> import logging, sys
>>> logging.getLogger("text2spoken").addHandler(logging.StreamHandler(sys.stdout))
>>> normalize("Hay 1000000000000000000000000000000000000000001 granos.", "es-ES")
unread cardinal span '1000000000000000000000000000000000000000001' at 4: 43 digits reach 10**42, which this file leaves as written
'Hay 1000000000000000000000000000000000000000001 granos.'
```

## The error classes

Every error in this page is a subclass of `Text2SpokenError`, and so of `ValueError`. `ArgumentTypeError` is also a subclass of `TypeError`. `UndefinedGrammaticalGender` is a subclass of `UnsupportedParameterError`. Every warning is a subclass of `Text2SpokenWarning`, which is a `UserWarning`. A defect in a speller or a verbalizer raises its own error, with a note that names the language, the form and the text.

---
[← API](api.md) · [Home](index.md) · [Arabic →](languages/ar.md)
