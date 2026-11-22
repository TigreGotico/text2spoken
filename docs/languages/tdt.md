# Tetun Dili

<!-- agent-hint
covers: what the Tetun Dili file reads, its varieties, options, sources and limits.
source: text2spoken/lang/tdt.py, tests/data/tdt.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/tdt.md`
see: pt.md, ../how-it-reads.md
-->

The file `text2spoken/lang/tdt.py` reads Tetun Dili, the Tetun of Dili and Timor-Leste. It needs no extra, because its date words come from `ovos-date-parser`, which the base install holds.

## What it reads

The file reads numeric dates and lexicon entries. Tetun Dili speakers use three sets of numerals: Tetun, Portuguese and Indonesian. A date reads in Portuguese numerals, with the Portuguese date words of `ovos-date-parser` for `pt-PT`. The day comes before the month.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Room 3 on 12/11/2025.` | `tdt-TL` | Room 3 on doze de novembro de dois mil e vinte e cinco. |
| `Hau moris iha Zumalai iha 10/04/1973.` | `tdt-TL` | Hau moris iha Zumalai iha dez de abril de mil novecentos e setenta e três. |
| `Maun moris iha 23/05/1990.` | `tdt-TL` | Maun moris iha vinte e três de maio de mil novecentos e noventa. |
| `20/05/2002` | `tdt-TL` | vinte de maio de dois mil e dois |
| `2025-11-12` | `tdt-TL` | doze de novembro de dois mil e vinte e cinco |

The words have the Portuguese spelling, which the espeak `pt` voice of the speech stack reads. Written Tetun spells a Portuguese numeral in Tetun spelling, as "déz de Abril".

## Varieties

| Tag | Date order |
| --- | --- |
| `tdt-TL` (the default variety) | Day, month, year |

`tdt` serves every Tetun Dili tag. It does not serve `tet`, Tetun Terik, a separate language.

## Options

| Option | Values | Default (`tdt-TL`) |
| --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

## Sources

The rules come from Catharina Williams-van Klinken and John Hajek, "Mixing numeral systems in Timor-Leste", NUSA 64 (2018), [doi:10.5281/zenodo.1450774](https://doi.org/10.5281/zenodo.1450774). Section 10.1 gives the numerals for a text that a voice reads aloud: "the voiceover for written announcements on television make overwhelming use of Portuguese for items such as telephone numbers, dates and prices." CLDR 48 gives the date order of Timor-Leste: the `pt-TL` date `dd/MM/y`. The docstring of [`tdt.py`](../../text2spoken/lang/tdt.py) quotes each source.

Each of the 16 rows in `tests/data/tdt.tsv` cites a source. No native speaker has checked the rows.

## Limits

The file reads no cardinals, times, percentages, money or telephone numbers. The source gives each of them more than one reading, and the written text does not choose one. A cardinal after a noun reads in Tetun when it counts, as `kaixa 7` "kaixa hitu" (seven boxes), and in Portuguese or Indonesian when it labels, as "rejiaun ún" (region one). A time reads in any of the three numeral sets, and Indonesian is the most common. A price and a telephone number read in Portuguese in a voiceover and in Indonesian in everyday speech.

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Ami tama 8:00, sai 12:30.` | `tdt-TL` | stays as written | A time reads in Tetun, Portuguese or Indonesian. |
| `Iha kaixa 7.` | `tdt-TL` | stays as written | A cardinal reads in Tetun when it counts and in Portuguese when it labels. |
| `Sae ba 90%.` | `tdt-TL` | stays as written | A percentage reads in any of the three numeral sets. |
| `Mina nee, litru ida $1.` | `tdt-TL` | stays as written | Money stays as written. |
| `Hau nia númeru telefone 7731 2345.` | `tdt-TL` | stays as written | A telephone number stays as written. |
| `Data 13/13/2024 la iha.` | `tdt-TL` | stays as written | Month 13 is no date. |

---
[← Russian](ru.md) · [Home](../index.md) · [Chinese →](zh.md)
