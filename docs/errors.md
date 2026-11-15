# Errors and warnings

The library has two modes. The default mode keeps a form that it cannot read as written and logs a warning, so a voice still speaks the sentence. Strict mode, `NormalizationParams(strict=True)`, raises an error instead, so a training pipeline finds each gap.

## Each case

| Case | Default mode | `strict=True` |
| --- | --- | --- |
| An argument, a param field or a hint of the wrong type | `ArgumentTypeError` | `ArgumentTypeError` |
| A param value that no language takes, such as `date_order="mdy"` | `InvalidParameterError` | `InvalidParameterError` |
| A tag that is not a BCP 47 tag | `InvalidLanguageTagError` | `InvalidLanguageTagError` |
| A form that the library cannot read | Stays as written, WARNING logged | `UnreadFormError` |
| A param value that the language cannot produce | Language default, `ParameterNotHonouredWarning` | `UnsupportedParameterError` |
| A gender that a language with genders does not have | `UndefinedGrammaticalGender` | `UndefinedGrammaticalGender` |
| A hint at an offset where no span starts | `HintWarning` | `InvalidHintError` |
| A lexicon value that contains a readable form | `InvalidLexiconError` | `InvalidLexiconError` |
| A tokenizer result that is not a sequence of tokens that match the text | `TokenizerError` | `TokenizerError` |

```python
from text2spoken import NormalizationParams, UnreadFormError, normalize

normalize("The run took 1:23:45.", "en-GB")
# 'The run took 1:23:45.'
try:
    normalize("The run took 1:23:45.", "en-GB", NormalizationParams(strict=True))
except UnreadFormError as error:
    unread = error.unread
# unread: ('1:23:45.',)
```

`UnreadFormError.unread` holds each run that stays as written.

A param value that the language cannot produce is a problem of the call, not of the text. So the library reports it with the Python `warnings` module, and a caller can turn it into an error with a warnings filter. `effective_params` shows the value that applies:

```python
import warnings

from text2spoken import ParameterNotHonouredWarning

with warnings.catch_warnings():
    warnings.simplefilter("error", ParameterNotHonouredWarning)
    try:
        normalize("Às 14:30.", "pt-PT", NormalizationParams(clock="12h"))
    except ParameterNotHonouredWarning as warning:
        message = str(warning)
# message: "'pt-PT' cannot produce clock='12h'; '24h' applies"
```

An option that changes nothing in a language, which `supports(lang).not_applicable` lists, has no effect and gives no warning.

## Genders

A language with genders raises `UndefinedGrammaticalGender` for a gender that it does not have, in both modes, because a substitute gender would change the words of the sentence. The error names the language, the value and the genders that the language has:

```python
from text2spoken import FrozenMap, GrammaticalGender, UndefinedGrammaticalGender

try:
    normalize("Comprei 1.", "pt-PT", NormalizationParams(default_gender=FrozenMap({"pt": GrammaticalGender.NEUTER})))
except UndefinedGrammaticalGender as error:
    message = str(error)
# message: "'pt-PT' does not define 'neuter'; it defines ['feminine', 'masculine']"
```

A language with no genders ignores a gender in a hint or in `default_gender`. English, Basque and every language with no file have no genders.

## When a reading stays as written

The library declines a reading that it cannot give for sure. A speller or a verbalizer that cannot read a span that the library found raises `DeclinedReading`. The span then stays as written, and the library logs one WARNING that names the form, the span and the reason. In strict mode, `UnreadFormError` replaces the warning, chained to the cause. A digit or a symbol of a form in `forms` that stays in the output gets the same treatment.

```python
normalize("Hay 10000000000000000000000000001 granos.", "es-ES")
# 'Hay 10000000000000000000000000001 granos.'
```

The Spanish file reads no number from 10^28 up, so this number stays as written, and the log line is `unread cardinal span '10000000000000000000000000001' at 4: 29 digits reach 10**28, which this file leaves as written`.

The logger is `logging.getLogger("text2spoken")`. A log warning names the form and the text, so a reader can tell a gap in a language file from a bug.

## The error classes

Every error in this page is a subclass of `Text2SpokenError`, and so of `ValueError`. `ArgumentTypeError` is also a subclass of `TypeError`. `UndefinedGrammaticalGender` is a subclass of `UnsupportedParameterError`. Every warning is a subclass of `Text2SpokenWarning`, which is a `UserWarning`. A defect in a speller or a verbalizer raises its own error, with a note that names the language, the form and the text.

---
[← API](api.md) · [Home](index.md) · [Arabic →](languages/ar.md)
