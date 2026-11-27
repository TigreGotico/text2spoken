# Hindi

<!-- agent-hint
covers: what the Hindi file reads, its varieties, options, sources and limits.
source: text2spoken/lang/hi.py, tests/data/hi.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/hi.md`
see: ja.md, ../how-it-reads.md
-->

The file `text2spoken/lang/hi.py` reads Hindi. It needs no extra, because its number words come from numtag and from the CLDR spell-out rules, which the base install holds.

## What it reads

The file reads cardinals, decimals, a minus before them and lexicon entries. A number reads in Latin digits and in Devanagari digits, with the comma as the group mark in the Indian grouping. The decimal mark reads दशमलव, and each digit after the mark reads alone.

| Written | Tag | Spoken |
| --- | --- | --- |
| `21` | `hi-IN` | इक्कीस |
| `२१` | `hi-IN` | इक्कीस |
| `99` | `hi-IN` | निन्यानवे |
| `१,००,०००` | `hi-IN` | एक लाख |
| `12,34,567` | `hi-IN` | बारह लाख चौंतीस हज़ार पाँच सौ सड़सठ |
| `1000000000` | `hi-IN` | एक अरब |
| `-5` | `hi-IN` | ऋण पाँच |
| `2.75` | `hi-IN` | दो दशमलव सात पाँच |
| `उसकी उम्र ९९ साल है।` | `hi-IN` | उसकी उम्र निन्यानवे साल है। |

A say-as `ordinal` reads the masculine ordinal by default, as तीसरा for `3`. With `default_gender` set to the feminine, it reads तीसरी.

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `hi-IN` (the default variety) | Full stop | Comma |

## Options

| Option | Values | Default (`hi-IN`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | `feminine`, `masculine` | `masculine` |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

`default_gender` sets the gender of a say-as ordinal. Cardinals have no gender in Hindi.

## Sources

| Source | What it gives |
| --- | --- |
| Kendriya Hindi Nideshalaya, *Devanagari Lipi tatha Hindi Vartani ka Manakikaran* (2016), section 5.1, pp. 52 to 53 | The standard words of 1 to 100, as निन्यानवे for 99, and the scale words हज़ार, लाख, करोड़ and अरब |
| CLDR RBNF rule sets of `hi` | The minus word ऋण, the decimal word दशमलव, the digit words, and the masculine and feminine ordinals |
| numtag | The words of each cardinal |

The docstring of [`hi.py`](../../text2spoken/lang/hi.py) quotes each source. Each row in `tests/data/hi.tsv` cites a source. No native speaker has checked the rows.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `3rd` | `hi-IN` | stays as written | An ordinal in plain text stays as written. Only a say-as `ordinal` reads it. |
| `20%` | `hi-IN` | stays as written | A percentage stays as written, as in a language with no file. |
| `5 kg` | `hi-IN` | stays as written | A measure stays as written. |
| `25/12/2024` | `hi-IN` | stays as written | A numeric date stays as written. |
| `1/2` | `hi-IN` | stays as written | A fraction stays as written. |

A say-as ordinal of 99 reads निन्यानबेवाँ, the CLDR word, and not the standard निन्यानवे with the suffix.

---
[← French](fr.md) · [Home](../index.md) · [Italian →](it.md)
