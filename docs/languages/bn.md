# Bengali

<!-- agent-hint
covers: what the Bengali file reads, its varieties, options, sources and limits.
source: text2spoken/lang/bn.py, tests/data/bn.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/bn.md`
see: ja.md, ../how-it-reads.md
-->

The file `text2spoken/lang/bn.py` reads Bengali. It needs no extra, because its number words come from numtag, which the base install holds.

## What it reads

The file reads cardinals and lexicon entries. A number reads in Latin digits and in Bengali digits, with the comma as the group mark in the Indian grouping. A numeral classifier joined to the number (টি, টা, জন, খানা, খানি) reads as one word with the cardinal. দুই takes the joined forms দুটি, দুটা and দুটো. The allomorphs টো and টে read only in দুটো, তিনটে and চারটে.

| Written | Tag | Spoken |
| --- | --- | --- |
| `21` | `bn-BD` | একুশ |
| `২১` | `bn-BD` | একুশ |
| `৬৭` | `bn-BD` | সাতষট্টি |
| `99` | `bn-BD` | নিরানব্বই |
| `১০০` | `bn-BD` | এক শ |
| `1000` | `bn-BD` | এক হাজার |
| `১,০০,০০০` | `bn-BD` | এক লাখ |
| `1234567` | `bn-IN` | বারো লাখ চৌত্রিশ হাজার পাঁচ শ সাতষট্টি |
| `১২,৩৪,৫৬৭` | `bn-IN` | বারো লাখ চৌত্রিশ হাজার পাঁচ শ সাতষট্টি |
| `ক্লাসে ২১ জন ছাত্র আছে।` | `bn-BD` | ক্লাসে একুশ জন ছাত্র আছে। |
| `আমার ২১টি বই আছে।` | `bn-BD` | আমার একুশটি বই আছে। |
| `আমি 3টি আপেল কিনেছি।` | `bn-BD` | আমি তিনটি আপেল কিনেছি। |
| `2টি` | `bn-BD` | দুটি |
| `2টো` | `bn-BD` | দুটো |
| `4টে` | `bn-BD` | চারটে |
| `5জন` | `bn-BD` | পাঁচজন |

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `bn-BD` (the default variety) | Full stop | Comma |
| `bn-IN` | Full stop | Comma |

The two varieties read the same words.

## Options

| Option | Values | Default (`bn-BD`) |
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
| English Wiktionary, "Appendix:Bengali numerals" (oldid 95460450) | The words of 0 to 100, and the scale words হাজার, লাখ and কোটি |
| Hanne-Ruth Thompson, *Bengali* (2012), Appendices | The numbers in Roman letters, with the hundred apart: "100 ek so", "200 du so", "1000 ek hajar" |
| Hanne-Ruth Thompson, *Bengali* (2012), sections 5.2.4 to 5.2.5.5 | The classifiers ta, ti, jon, khana and khani after numbers; the allomorphs "duto two, tinte three, carte four"; gulo and guli "never to numbers" |
| Bangla Academy, *Adhunik Bangla Abhidhan* (2016) | The Bengali script of টি, জন, একটা, দুটা, দুটি, দুটো, চারটে and তিনটে |
| numtag | The words of each cardinal |

The docstring of [`bn.py`](../../text2spoken/lang/bn.py) quotes each source. Each row in `tests/data/bn.tsv` cites a source. No native speaker has checked the rows.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `3.5` | `bn-BD` | stays as written | numtag reads no Bengali decimal. |
| `-5` | `bn-BD` | stays as written | numtag reads no Bengali minus sign. |
| `5টে` | `bn-BD` | stays as written | The sources give টো and টে only after 2, 3 and 4. |
| `১০০টি` | `bn-BD` | stays as written | No source gives a classifier after a cardinal of two words, as এক শ. |
| `3টিতে` | `bn-BD` | stays as written | A classifier with a case ending after it stays as written. |
| `20%` | `bn-BD` | stays as written | A percentage stays as written, as in a language with no file. |
| `25/12/2024` | `bn-BD` | stays as written | A numeric date stays as written. |

---
[← Arabic](ar.md) · [Home](../index.md) · [Catalan →](ca.md)
