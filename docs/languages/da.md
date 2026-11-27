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

A number with no word after it ends in `en`, the form of counting. A number before a word ends in `et`, the neuter. The file reads no noun gender, so 1 before a common-gender noun reads `et` too. The option `default_gender` changes nothing.

| Written | Tag | Spoken |
| --- | --- | --- |
| `1` | `da-DK` | en |
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
| English Wiktionary, "nul" | The Danish example "nul komma fem" |
| numtag | The words of each cardinal |

The docstring of [`da.py`](../../text2spoken/lang/da.py) quotes each source. Each row in `tests/data/da.tsv` cites a source. No native speaker has checked the rows.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Hun kom ind på en 3. plads.` | `da-DK` | stays as written | An ordinal stays as written. |
| `20%` | `da-DK` | stays as written | A percentage stays as written, as in a language with no file. |
| `5 €` | `da-DK` | stays as written | A sum of money stays as written. |
| `25/12/2024` | `da-DK` | stays as written | A numeric date stays as written. |
| `1 bil` | `da-DK` | et bil | The file reads no noun gender, so 1 before a common-gender noun reads `et`, not `en`. |

---
[← Catalan](ca.md) · [Home](../index.md) · [German →](de.md)
