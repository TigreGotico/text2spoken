# Usage

<!-- agent-hint
covers: how to turn forms off and on, pick a variety, add lexicon entries and keep text as written.
source: text2spoken/params.py:NormalizationParams, text2spoken/core/language.py:lexicon_entries, text2spoken/core/tokens.py:protect_blocks
generated: no
verify: pytest tests/test_docs_examples.py -k usage.md
see: how-it-reads.md, api.md
-->

This page shows how to tune the reading: turn a form off or on, pick a variety, add your own words, and keep text as written. It then shows the reading for a voice, a phonemizer and a word error rate score.

## Turn a form off or on

Each written form has a `Form` value, and `NormalizationParams` holds the forms to read. Every form except `LETTERS` and `EMOJI` is on by default. `without` turns one form off, `plus` turns one on, and `only` keeps the forms that you name:

```python
>>> from text2spoken import Form, NormalizationParams, normalize
>>> normalize("Go → left at 9am.", "en-GB", NormalizationParams().without(Form.SYMBOL))
'Go → left at nine AM.'
>>> normalize("The BBC at 9am.", "en-GB", NormalizationParams().plus(Form.LETTERS))
'The bee bee see at nine a em.'
>>> normalize("Pay $5 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
'Pay $5 for three items.'
```

[How it reads text](how-it-reads.md#the-forms) lists every form.

## Pick a language variety

The language tag selects the language file and the variety. The variety sets the defaults, such as the order of a date:

| Written | Spoken (`en-US`) | Spoken (`en-GB`) |
| --- | --- | --- |
| `Meet on 03/04/2025 at 7:30 pm.` | Meet on March fourth twenty twenty-five at seven thirty PM. | Meet on the third of April twenty twenty-five at seven thirty PM. |

`en-US` reads `03/04/2025` as month, day, year, and `en-GB` reads it as day, month, year. Each option of `NormalizationParams` overrides the default of the variety for one call:

```python
>>> normalize("Meet on 03/04/2025.", "en-GB", NormalizationParams(date_order="MDY"))
'Meet on the fourth of March twenty twenty-five.'
>>> normalize("Meet at 14:30.", "en-GB", NormalizationParams(clock="24h"))
'Meet at fourteen thirty.'
```

The language pages give the options of each language and their defaults. [API](api.md#params) gives each field.

## Add your own words

A lexicon entry reads a written form your way. The lexicon maps a language tag to a map of written forms to spoken words:

```python
>>> from text2spoken import FrozenMap
>>> params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"NHS": "N H S"})}))
>>> normalize("Ask the NHS today.", "en-GB", params)
'Ask the N H S today.'
```

An entry matches a whole written form, with its case. The character before the match and the character after it must not be a letter, a digit or a combining mark. An apostrophe counts as a limit, so `ACME` matches in `ACME's` and in `l'ACME`. When two keys match at one position, the longer key wins. The library takes the entries of the primary language subtag, then the entries of the full tag, which replace them key by key. `without(Form.LEXICON)` turns the lexicon off for one call.

A lexicon value that holds a form that the library reads raises `InvalidLexiconError`, because a second pass would read it. An entry that keeps its key, such as `{"MIX": "MIX"}`, is allowed.

## Keep text as written

Text inside `[[` and `]]` passes through byte for byte, and no form reads it:

```python
>>> normalize("Keep [[£5]] but pay £5.", "en-GB")
'Keep [[£5]] but pay five pounds.'
```

## Text to speech

A voice speaks words, not digits or symbols. Normalise the text before you send it to the voice:

```python
>>> normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
'Meet on March fourth twenty twenty-five at seven thirty PM.'
```

## Phonemizers

A grapheme-to-phoneme model or a rule set expects words. A digit or a symbol has no pronunciation of its own, so the phonemizer drops it or spells it wrongly. Normalise first, then phonemize:

```python
>>> words = normalize("It is 5 km away.", "en-GB")
>>> words
'It is five kilometres away.'
```

## Word error rate

An ASR system writes "ten thirty" where a reference transcript writes "10:30". The two texts say the same thing, but a word error rate counts each difference as an error. Normalise the reference and the hypothesis with the same tag and the same params:

```python
>>> normalize("The train leaves at 10:30 on 3 May from platform 2.", "en-GB")
'The train leaves at ten thirty on the third of May from platform two.'
>>> normalize("the train leaves at ten thirty on the third of may from platform two", "en-GB")
'the train leaves at ten thirty on the third of may from platform two'
```

Text that is already in words does not change. The library does not change case or punctuation, so lowercase both texts and remove punctuation before you score them.

## One set of params for a pipeline

A pipeline that takes a `Callable[[str, str], str]` gets its params through `functools.partial`. One params value serves every language, because the language is a separate argument:

```python
>>> from functools import partial
>>> speak = partial(normalize, params=NormalizationParams(clock="24h").without(Form.TELEPHONE))
>>> speak("Meet at 14:30.", "en-GB")
'Meet at fourteen thirty.'
```

scriptconv has such a hook. `uv pip install --prerelease=allow "scriptconv[normalize]"` installs text2spoken, and `scriptconv.frontend.spoken_normalizer()` returns `normalize` for the `normalizer` field of its `FrontendConfig`.

---
[← Quickstart](quickstart.md) · [Home](index.md) · [How it reads text →](how-it-reads.md)
