# text2spoken

text2spoken rewrites written text into the words that a person says when they read it aloud. It reads numbers, dates, times, money, measures, percentages, telephone numbers, colours, abbreviations, and e-mail and web addresses. The rest of the text stays as it is, character for character.

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Dr Smith paid £3.50 for 2 tickets on 14 March 2024.` | Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four. |

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

The library needs Python 3.11 or later. It uses no network and loads no model. English and German need no extra. The other languages take their number words from an extra:

```bash
uv pip install --prerelease=allow "text2spoken[pt]"   # also ar, es, eu, ru
```

## Quickstart

```python
from text2spoken import normalize

normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
# 'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
# 'Meet on March fourth twenty twenty-five at seven thirty PM.'
```

The second argument is a BCP 47 language tag. It selects the language and the variety, so `en-US` reads `03/04/2025` as month, day, year, and `en-GB` reads it as day, month, year.

## Where this fits

Alone: rewrite text into spoken words before a voice, a phonemizer or a word error rate score reads it, with `from text2spoken import normalize`.

In the stack: the normalisation stage. A phonemizer library or a TTS frontend calls `normalize` first and phonemizes its output. text2spoken calls no phonemizer and no model.

Through scriptconv: `uv pip install --prerelease=allow "scriptconv[normalize]"`.

## Languages

Each language is one file in `text2spoken/lang/`. A tag with no file reads cardinal numbers from the CLDR spell-out rules, where CLDR has rules for that language.

| Language | Varieties | Extra |
| --- | --- | --- |
| [Arabic](docs/languages/ar.md) | `ar-001` and ten regional tags. 25 Arabic varieties of ISO 639-3, such as `arz` and `ary`, read as `ar` | `ar` |
| [German](docs/languages/de.md) | `de-DE`, `de-AT`, `de-CH` | none |
| [English](docs/languages/en.md) | `en-GB`, `en-US` | none |
| [Spanish](docs/languages/es.md) | `es-ES`, `es-419`, `es-MX`, `es-AR`, `es-US` and eight other American varieties | `es` |
| [Basque](docs/languages/eu.md) | `eu-ES` | `eu` |
| [Portuguese](docs/languages/pt.md) | `pt-PT`, `pt-BR` | `pt` |
| [Russian](docs/languages/ru.md) | `ru-RU` | `ru` |

## Documentation

| Page | What it tells you |
| --- | --- |
| [Docs index](docs/index.md) | The map of the docs |
| [Quickstart](docs/quickstart.md) | Install, the first call, and how to see what a tag reads |
| [Usage](docs/usage.md) | Text to speech, phonemizers and word error rate, with examples |
| [How it reads text](docs/how-it-reads.md) | Each written form, what it reads, and which forms are off by default |
| [API](docs/api.md) | `normalize`, `analyze`, `render`, `supports`, `effective_params`, the params, hints and tokenizers |
| [Errors and warnings](docs/errors.md) | Each error and warning, strict mode, and when a reading stays as written |
| [Adding a language](docs/adding-a-language.md) | The contract of a language file |
| [Development](docs/development.md) | The tests, the row files and CI |

## Licence

Apache-2.0. See [LICENSE](LICENSE). The CLDR data in `text2spoken/data/cldr/` ships under the Unicode License v3, in [its own licence file](text2spoken/data/cldr/LICENSE).

The changes of each release are in [CHANGELOG.md](CHANGELOG.md).
