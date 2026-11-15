# Usage

text2spoken has three main uses: text for a voice, text for a phonemizer, and text for a word error rate score. Each use calls `normalize` with a language tag.

## Text to speech

A voice speaks words, not digits or symbols. Normalise the text before you send it to the voice:

```python
from text2spoken import normalize

normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
# 'Meet on March fourth twenty twenty-five at seven thirty PM.'
```

The language tag selects the reading. `en-US` reads `03/04/2025` as month, day, year. `en-GB` reads it as day, month, year.

## Phonemizers

A grapheme-to-phoneme model or a rule set expects words. A digit or a symbol has no pronunciation of its own, so the phonemizer drops it or spells it wrongly. Normalise first, then phonemize:

```python
words = normalize("It is 5 km away.", "en-GB")
# words: 'It is five kilometres away.'
# phonemes = my_phonemizer(words)
```

## Word error rate

An ASR system writes "ten thirty" where a reference transcript writes "10:30". The two texts say the same thing, but a word error rate counts each difference as an error. Normalise the reference and the hypothesis with the same tag and the same params:

```python
ref = normalize("The train leaves at 10:30 on 3 May from platform 2.", "en-GB")
hyp = normalize("the train leaves at ten thirty on the third of may from platform two", "en-GB")
# ref: 'The train leaves at ten thirty on the third of May from platform two.'
# hyp: 'the train leaves at ten thirty on the third of may from platform two'
```

Text that is already in words does not change. The library does not change case or punctuation, so lowercase both texts and remove punctuation before you score them.

## One set of params for a pipeline

A pipeline that takes a `Callable[[str, str], str]` gets its params through `functools.partial`. One params value serves every language, because the language is a separate argument:

```python
from functools import partial

from text2spoken import Form, NormalizationParams

speak = partial(normalize, params=NormalizationParams(clock="24h").without(Form.TELEPHONE))
speak("Meet at 14:30.", "en-GB")
# 'Meet at fourteen thirty.'
```

scriptconv has such a hook. `uv pip install --prerelease=allow "scriptconv[normalize]"` installs text2spoken, and `scriptconv.frontend.spoken_normalizer()` returns `normalize` for the `normalizer` field of its `FrontendConfig`.

## Text that must stay as written

Text inside `[[` and `]]` passes through byte for byte, and no form reads it:

```python
normalize("Keep [[£5]] but pay £5.", "en-GB")
# 'Keep [[£5]] but pay five pounds.'
```

---
[← Quickstart](quickstart.md) · [Home](index.md) · [How it reads text →](how-it-reads.md)
