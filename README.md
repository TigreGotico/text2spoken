# text2spoken

<!-- agent-hint
covers: what text2spoken does, how to install and call it, and where each other fact is.
source: text2spoken/__init__.py, pyproject.toml, text2spoken/lang/
generated: no
verify: `python scripts/check_doc_page.py README.md`
see: docs/index.md, docs/quickstart.md, docs/how-it-works.md, AGENTS.md
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

## Find your answer

| You want to | Read |
| --- | --- |
| Install it and make a first call | [Quickstart](docs/quickstart.md) |
| Try it in the browser, with examples for each language | [Hugging Face Space](https://huggingface.co/spaces/TigreGotico/text2spoken) |
| Turn a form off or on, or add your own words | [Usage](docs/usage.md) |
| Read a form that SSML `say-as` markup names | [API, say_as](docs/api.md#say_as) |
| Know why a text reads as it does | [How it reads text](docs/how-it-reads.md) |
| See which forms each language reads | [Languages at a glance](docs/coverage.md) |
| See how a text goes through the library, and what a call costs | [How it works](docs/how-it-works.md) |
| Add your language, step by step | [Adding a language](docs/adding-a-language.md) |
| Look up a function, a param or an error | [API](docs/api.md), [Errors and warnings](docs/errors.md) |
| Know which installed versions write the output of a language | [API, revision](docs/api.md#revision) |
| Use it before a phonemizer, a voice or a word error rate score | [How it works, where it fits](docs/how-it-works.md#where-it-fits), [Usage](docs/usage.md#text-to-speech) |
| See the languages and their varieties | [Docs index, languages](docs/index.md#languages) |
| Run the tests | [Development](docs/development.md) |

The [docs index](docs/index.md) lists every page in reading order. A contributor reads [AGENTS.md](AGENTS.md) for the map of the repository and the rules that a pull request must meet.

## Licence

Apache-2.0, in [LICENSE](LICENSE). The CLDR data in `text2spoken/data/cldr/` ships under the [Unicode License v3](text2spoken/data/cldr/LICENSE).
