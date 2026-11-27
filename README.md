# text2spoken

<!-- agent-hint
covers: what text2spoken does, how to install and call it, and where it sits in the speech stack.
source: text2spoken/__init__.py, pyproject.toml, text2spoken/lang/
generated: no
verify: `python scripts/check_doc_page.py README.md`
see: docs/index.md, docs/quickstart.md, docs/coverage.md, AGENTS.md
-->

text2spoken rewrites written text into the words that a person says when they read it aloud. It reads numbers, dates, times, money, measures, percentages, telephone numbers, colours, abbreviations, and e-mail and web addresses. The rest of the text stays as it is, character for character. It uses no network and no model.

## Quickstart

```bash
uv pip install --prerelease=allow text2spoken
```

```python
>>> from text2spoken import normalize
>>> normalize("Dr Smith paid £3.50 for 2 tickets on 14 March 2024.", "en-GB")
'Doctor Smith paid three pounds and fifty pence for two tickets on the fourteenth of March twenty twenty-four.'
>>> normalize("Meet on 03/04/2025 at 7:30 pm.", "en-US")
'Meet on March fourth twenty twenty-five at seven thirty PM.'
>>> normalize("O Dr. Silva pagou 2,50 € às 14:30.", "pt-PT")
'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

The second argument is a BCP 47 tag. It selects the language file and the variety. The library needs Python 3.11 or later. Every language reads with the base install. Portuguese takes the `pt` extra for the gender of nouns and names, from `tugalex`.

## Where this fits

Alone: rewrite one string for one language tag with `from text2spoken import normalize`.
In the stack: the normalisation stage before a phonemizer or a voice. The phonemizers tugaphone and euskaphone, the voice library phoonnx and the scriptconv `TextFrontend` call `normalize(text, lang)`. It calls numtag for the numbers of Portuguese, and ovos-number-parser, ovos-date-parser, unicode-rbnf, linguatag and quebra-frases.
Through scriptconv: `uv pip install --prerelease=allow "scriptconv[normalize]"`.

## Find your answer

| You want to | Read |
| --- | --- |
| Install it and make a first call | [Quickstart](docs/quickstart.md) |
| Turn a form off or on, or add your own words | [Usage](docs/usage.md) |
| Read a form that SSML `say-as` markup names | [API, say_as](docs/api.md#say_as) |
| Know why a text reads as it does | [How it reads text](docs/how-it-reads.md) |
| See which forms each language reads | [Languages at a glance](docs/coverage.md) |
| See how a text goes through the library, and what a call costs | [How it works](docs/how-it-works.md) |
| Add your language, step by step | [Adding a language](docs/adding-a-language.md) |
| Look up a function, a param or an error | [API](docs/api.md), [Errors and warnings](docs/errors.md) |
| Know which installed versions write the output of a language | [API, revision](docs/api.md#revision) |
| Run the tests | [Development](docs/development.md) |

The [docs index](docs/index.md) lists every page in reading order. A contributor reads [AGENTS.md](AGENTS.md) for the map of the repository and the rules that a pull request must meet.

## Languages

Each language page gives what the language reads, its varieties, its options, its sources and its limits. `supports(lang)` gives the same facts from code.

| Language | Varieties |
| --- | --- |
| [Arabic](docs/languages/ar.md) | `ar-001`, the regional `ar-*` tags, and the spoken lects of ISO 639-3, such as `arz` |
| [Bengali](docs/languages/bn.md) | `bn-BD`, `bn-IN` |
| [Catalan](docs/languages/ca.md) | `ca-ES`, `ca-AD`, `ca-ES-valencia` |
| [German](docs/languages/de.md) | `de-DE`, `de-AT`, `de-CH` |
| [Greek](docs/languages/el.md) | `el-GR` |
| [English](docs/languages/en.md) | `en-GB`, `en-US` |
| [Spanish](docs/languages/es.md) | `es-ES`, `es-419` and the American varieties, such as `es-MX` |
| [Basque](docs/languages/eu.md) | `eu-ES` |
| [French](docs/languages/fr.md) | `fr-FR`, `fr-CA`, `fr-CH`, and each other `fr-*` tag with the number words of its CLDR locale |
| [Hindi](docs/languages/hi.md) | `hi-IN` |
| [Italian](docs/languages/it.md) | `it-IT`, `it-CH`, `it-SM` |
| [Japanese](docs/languages/ja.md) | `ja-JP` |
| [Korean](docs/languages/ko.md) | `ko-KR` |
| [Dutch](docs/languages/nl.md) | `nl-NL`, `nl-BE`, `nl-SR` |
| [Portuguese](docs/languages/pt.md) | `pt-PT`, `pt-BR` |
| [Russian](docs/languages/ru.md) | `ru-RU` |
| [Tetun Dili](docs/languages/tdt.md) | `tdt-TL` |
| [Chinese](docs/languages/zh.md) | `zh-CN`, `zh-TW`, and `cmn` |

A tag with no language file reads cardinal numbers, decimals and a minus, with the words of ovos-number-parser or of the CLDR spell-out rules, in the decimal and group marks of CLDR for the locale. The page [How it reads text](docs/how-it-reads.md#a-language-with-no-file) gives the rules.

## Licence

Apache-2.0, in [LICENSE](LICENSE). The CLDR data in `text2spoken/data/cldr/` ships under the [Unicode License v3](text2spoken/data/cldr/LICENSE). [CHANGELOG.md](CHANGELOG.md) lists the changes of each release.
