# Danish

<!-- agent-hint
covers: what the Danish file reads, its variety, options, sources and limits.
source: text2spoken/lang/da.py, tests/data/da.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/da.md`
see: bn.md, ../how-it-reads.md
-->

The file `text2spoken/lang/da.py` reads Danish. It needs no extra, because its number words come from numtag, which the base install holds.

## What it reads

The file reads cardinals, decimals and lexicon entries. The decimal mark is the comma and the group mark is the full stop. A number under 100 is one word, and a number over 100 is two or more words.

| Written | Tag | Spoken |
| --- | --- | --- |
| `50` | `da-DK` | halvtreds |
| `85` | `da-DK` | femogfirs |
| `27` | `da-DK` | syvogtyve |
| `100` | `da-DK` | hundrede |
| `200` | `da-DK` | to hundrede |
| `4.393` | `da-DK` | fire tusind tre hundrede og treoghalvfems |
| `1001` | `da-DK` | tusind og en |
| `10,11` | `da-DK` | ti komma en en |
| `100,0` | `da-DK` | hundrede komma nul |
| `-5` | `da-DK` | minus fem |
| `Klassen har 27 elever.` | `da-DK` | Klassen har syvogtyve elever. |

## Gender

A number that ends in 1 takes the gender of the noun after it. Before a neuter noun it ends in `et`. Before a common-gender noun, before a word that is no noun, and with no word after it, it ends in `en`. The neuter nouns come from the list `text2spoken/data/wiktionary/da_noun_genders.json`. A noun that is not in the list reads `en`, because the list holds about three common-gender nouns for each neuter noun. The option `default_gender` changes nothing.

| Written | Tag | Spoken |
| --- | --- | --- |
| `1` | `da-DK` | en |
| `1 bil` | `da-DK` | en bil |
| `101 bil` | `da-DK` | hundrede og en bil |
| `1 hus` | `da-DK` | et hus |
| `1001 hus` | `da-DK` | tusind og et hus |
| `1 element` | `da-DK` | et element |
| `101 år` | `da-DK` | hundrede og et år |

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `da-DK` (the default variety) | Comma | Full stop |

## Options

| Option | Values | Default (`da-DK`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

## Sources

| Source | What it gives |
| --- | --- |
| sproget.dk (Dansk Sprognævn and DSL), "Et eller flere ord", section "Talord" | A number under 100 is one word, as "halvtreds" and "femogfirs". A number over 100 is two or more words, as "to hundred(e)" |
| sproget.dk, "Den 101. dalmatiner" | The forms "hundrede" and "hundred" of 100, and the two forms "én/ét" of 1 |
| da.wikipedia, "Betydende cifre" | The decimals digit by digit after "komma": "10,11 (ti komma en en)", "100,0 (Et hundrede komma nul)". The counting form "en": "1.001 (et tusinde og en)" |
| andlo, native Danish answers on text2spoken issue 709 | The form of 1 follows the noun: "en bil", "hundrede og en bil", but "et hus", "tusind og et hus", and "en" with no noun. The readings "en komma fem", "tusind og en" and "tusind" |
| English Wiktionary, "Danish common-gender nouns", "Danish neuter nouns" and "Danish nouns with multiple genders" (CC BY-SA 4.0) | The gender of each noun in `da_noun_genders.json`: 10,682 common-gender and 3,417 neuter category members |
| English Wiktionary, "nul" | The Danish example "nul komma fem" |
| numtag | The words of each cardinal |

The docstring of [`da.py`](../../text2spoken/lang/da.py) quotes each source. Each row in `tests/data/da.tsv` cites a source. A native speaker, andlo, checked the rows of the gender of 1, of `1,5`, of `1001` and of `1000`.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Hun kom ind på en 3. plads.` | `da-DK` | stays as written | An ordinal stays as written. |
| `20%` | `da-DK` | stays as written | A percentage stays as written, as in a language with no file. |
| `5 €` | `da-DK` | stays as written | A sum of money stays as written. |
| `25/12/2024` | `da-DK` | stays as written | A numeric date stays as written. |
| `1 postkontor` | `da-DK` | en postkontor | A neuter noun that is not in the noun list, as the compound "postkontor", reads `en`, not `et`. |

---
[← Catalan](ca.md) · [Home](../index.md) · [German →](de.md)
