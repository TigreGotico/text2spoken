# text2spoken

text2spoken rewrites written text into the words that a person says when they read it aloud. It reads numbers, dates, times, money, measures, percentages, telephone numbers, colours, abbreviations, and e-mail and web addresses. The rest of the text stays as it is, character for character.

## Install

```bash
uv pip install --prerelease=allow text2spoken
```

It needs Python 3.11 or later, and uses no network and no model. Each language except English, German and Greek takes an extra, such as `text2spoken[pt]`.

## Example

```python
>>> from text2spoken import normalize
>>> normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
>>> normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
'Meet on March fourth twenty twenty-five at seven thirty PM.'
>>> normalize("O Dr. Silva pagou 2,50 € às 14:30.", "pt-PT")
'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

The second argument is a BCP 47 tag. It selects the language and the variety.

## Find your answer

| You want to | Read |
| --- | --- |
| Install it and make a first call | [Quickstart](docs/quickstart.md) |
| Turn a form off or on, or add your own words | [Usage](docs/usage.md) |
| Know why a text reads as it does | [How it reads text](docs/how-it-reads.md) |
| Add your language, step by step | [Adding a language](docs/adding-a-language.md) |
| Look up a function, a param or an error | [API](docs/api.md), [Errors and warnings](docs/errors.md) |
| Run the tests | [Development](docs/development.md) |

The [docs index](docs/index.md) lists every page.

## Languages

A tag with no language file reads cardinal numbers from the CLDR spell-out rules.

| Language | Varieties | Extra |
| --- | --- | --- |
| [Arabic](docs/languages/ar.md) | `ar-001`, ten regional tags, and 25 ISO 639-3 varieties such as `arz` | `ar` |
| [German](docs/languages/de.md) | `de-DE`, `de-AT`, `de-CH` | none |
| [Greek](docs/languages/el.md) | `el-GR` | none |
| [English](docs/languages/en.md) | `en-GB`, `en-US` | none |
| [Spanish](docs/languages/es.md) | `es-ES`, `es-419` and eleven American varieties | `es` |
| [Basque](docs/languages/eu.md) | `eu-ES` | `eu` |
| [French](docs/languages/fr.md) | `fr-FR`, `fr-CA`, `fr-CH`. Every other `fr-*` tag reads as `fr-FR` | `fr` |
| [Dutch](docs/languages/nl.md) | `nl-NL`, `nl-BE`, `nl-SR` | `nl` |
| [Portuguese](docs/languages/pt.md) | `pt-PT`, `pt-BR` | `pt` |
| [Russian](docs/languages/ru.md) | `ru-RU` | `ru` |

## Where this fits

text2spoken is the normalisation stage: a voice, a phonemizer or a word error rate score calls `normalize` first. scriptconv uses it through an extra: `uv pip install --prerelease=allow "scriptconv[normalize]"`.

## Licence

Apache-2.0, in [LICENSE](LICENSE). The CLDR data in `text2spoken/data/cldr/` ships under the [Unicode License v3](text2spoken/data/cldr/LICENSE). [CHANGELOG.md](CHANGELOG.md) lists the changes of each release.
