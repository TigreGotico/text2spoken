# Kabyle

<!-- agent-hint
covers: what the Kabyle file reads, its variety, options, sources and limits.
source: text2spoken/lang/kab.py, tests/data/kab.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/kab.md`
see: bn.md, ../how-it-reads.md
-->

The file `text2spoken/lang/kab.py` reads Kabyle. It needs no extra, because its number words come from numtag, which the base install holds.

## What it reads

The file reads cardinals and lexicon entries. The numbers 1 and 2 are Berber words, and the numbers from 3 are Arabic words. The group mark is the no-break space.

| Written | Tag | Spoken |
| --- | --- | --- |
| `2` | `kab-DZ` | sin |
| `7` | `kab-DZ` | sebɛa |
| `10` | `kab-DZ` | ɛecṛa |
| `21` | `kab-DZ` | waḥed u ɛecrin |
| `99` | `kab-DZ` | tesɛa u tesɛin |
| `100` | `kab-DZ` | mya |
| `400` | `kab-DZ` | ṛebɛ-mya |
| `900` | `kab-DZ` | tesɛ-mya |
| `2000` | `kab-DZ` | alfin |
| `1000000` | `kab-DZ` | amelyun |
| `Ẓriɣ 2 n yirgazen.` | `kab-DZ` | Ẓriɣ sin n yirgazen. |

## Gender

The file reads no noun, so 1 and 2 read in the masculine, `yiwen` and `sin`, before a noun of each gender. The option `default_gender` changes nothing.

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `kab-DZ` (the default variety) | Comma | No-break space |

## Options

| Option | Values | Default (`kab-DZ`) |
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
| French Wiktionary, "Modèle:cardinaux/kab" (oldid 39522335) | The words of 0 to 99, the hundreds, the thousands to 9000, and "amelyun" |
| English Wikipedia, "Kabyle grammar" (oldid 1383353682), section Numerotation | The Berber 1 and 2 with their feminines "yiwet" and "snat", and "sin n yirgazen" |
| Mokraoui (2026), answers of the Kabyle native reviewer on Kabyle numbers | The hundreds without a final "a" ("ṛebɛ-mya", "tesɛ-mya") |
| Dallet (1982), *Dictionnaire kabyle-français*, p. 446 | "alfin" for 2000 |
| numtag | The words of each cardinal |

The docstring of [`kab.py`](../../text2spoken/lang/kab.py) quotes each source. Each row in `tests/data/kab.tsv` cites a source. The Kabyle native reviewer gave the forms of 400 and 900. No native speaker has checked the other rows.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `3,5` | `kab-DZ` | stays as written | numtag reads no Kabyle decimal. |
| `-5` | `kab-DZ` | stays as written | numtag reads no Kabyle minus sign. |
| `Nekk 3. deg tazwara.` | `kab-DZ` | stays as written | An ordinal stays as written. |
| `20%` | `kab-DZ` | stays as written | A percentage stays as written, as in a language with no file. |
| `25/12/2024` | `kab-DZ` | stays as written | A numeric date stays as written. |

---
[← Japanese](ja.md) · [Home](../index.md) · [Korean →](ko.md)
