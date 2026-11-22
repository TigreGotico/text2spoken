# Tetun Dili

<!-- agent-hint
covers: what the Tetun Dili file reads, its varieties, options, sources and limits.
source: text2spoken/lang/tdt.py, tests/data/tdt.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/tdt.md`
see: pt.md, ../how-it-reads.md
-->

The file `text2spoken/lang/tdt.py` reads Tetun Dili, the Tetun of Dili and Timor-Leste. It needs no extra. Its Portuguese words come from the `pt-PT` reading of the Portuguese file and from `ovos-date-parser`, which the base install holds.

## What it reads

The file reads numeric dates, times, money amounts, telephone numbers, percentages, measures and lexicon entries. Tetun Dili speakers use three sets of numerals: Tetun, Portuguese and Indonesian. Each of these forms reads in Portuguese numerals, with the words of `pt-PT`. The day of a date comes before the month.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Room 3 on 12/11/2025.` | `tdt-TL` | Room 3 on doze de novembro de dois mil e vinte e cinco. |
| `Hau moris iha Zumalai iha 10/04/1973.` | `tdt-TL` | Hau moris iha Zumalai iha dez de abril de mil novecentos e setenta e três. |
| `2025-11-12` | `tdt-TL` | doze de novembro de dois mil e vinte e cinco |
| `Foos kilo ida folin $5.` | `tdt-TL` | Foos kilo ida folin cinco dólares. |
| `Kafé ida folin US$ 1,50.` | `tdt-TL` | Kafé ida folin um dólar e cinquenta centavos. |
| `Folin 5 €.` | `tdt-TL` | Folin cinco euros. |
| `Governu fó US$ 10 milhoens.` | `tdt-TL` | Governu fó dez milhões de dólares. |
| `Telefone +670 7723 4567.` | `tdt-TL` | Telefone mais seis sete zero sete sete dois três quatro cinco seis sete. |
| `Telefone 331 2345.` | `tdt-TL` | Telefone três três um dois três quatro cinco. |
| `Sorumutu hahú tuku 15:30.` | `tdt-TL` | Sorumutu hahú tuku quinze e trinta. |
| `Sorumutu hahú 9h30.` | `tdt-TL` | Sorumutu hahú nove horas e trinta minutos. |
| `Sae ba 50%.` | `tdt-TL` | Sae ba cinquenta por cento. |
| `Dalan naruk 5 km.` | `tdt-TL` | Dalan naruk cinco quilómetros. |

The words have the Portuguese spelling, which the espeak `pt` voice of the speech stack reads. Written Tetun spells a Portuguese numeral in Tetun spelling, as "déz de Abril".

Timor-Leste uses the US dollar, so `$` and `US$` read "dólares". The minor unit is the centavo of the Banco Central de Timor-Leste, where `pt-PT` says "cêntimos". A time with a colon reads after the Tetun time word `tuku`. Without a time word, `16:9` could be a ratio and `3:16` a verse. A time with `h`, as `9h30`, needs no time word. The Tetun spellings of the Portuguese scale word, `milhaun`, `milhoens` and `milloens`, read as `milhão` and `milhões`. The scale words of `pt-PT`, as `mil`, also read. An amount before any other scale word stays as written. These words are the Tetun and Indonesian `atus`, `ratus`, `rihun`, `ribu`, `tokon` and `juta`, and each word that starts with `mil`, `míl`, `bil` or `tril`, in any case. Tetun writes the words for ‘million’ and ‘billion’ in many spellings, as `millaun`, `milloes`, `mill`, `biliaun` and `billioens`, and the text does not show which value the word has. An amount right after one of these words also stays as written. In Tetun word order, a number after a scale word counts it: `tokon $20` is 20 million dollars. These rules hold for money only, so a time, a percentage or a measure next to such a word still reads.

## Varieties

| Tag | Date order |
| --- | --- |
| `tdt-TL` (the default variety) | Day, month, year |

`tdt` serves every Tetun Dili tag. `tet` (Tetum, ISO 639-3) does not route to this file. The SIL ISO 639-3 code table names [`tdt`](https://iso639-3.sil.org/code/tdt) "Tetun Dili" and [`tet`](https://iso639-3.sil.org/code/tet) "Tetum", two individual languages.

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

The rules come from Catharina Williams-van Klinken and John Hajek, "Mixing numeral systems in Timor-Leste", NUSA 64 (2018), [doi:10.5281/zenodo.1450774](https://doi.org/10.5281/zenodo.1450774). Section 10.1 gives the numerals for a text that a voice reads aloud: "the voiceover for written announcements on television make overwhelming use of Portuguese for items such as telephone numbers, dates and prices." The same section says: "In formal contexts, Indonesian numerals are normally avoided". The date, price and telephone rows cite these quotes.

The time, percentage and measure rows are the reading of the project, and no quote gives it. Section 7.1 names the forms that take a borrowed numeral: "Indonesian and Portuguese are used for prices, time and date, phone numbers, measurements, sequence, mathematics and sports scores [...]." The formal register avoids Indonesian, which leaves Portuguese. The paper also gives Tetun for these forms: in formal speech, a percentage takes a Tetun numeral as often as a Portuguese one (section 7.6.4). Weights and measures in oral texts take Tetun most often: "50% are in Tetun, and the rest spread between Portuguese and Indonesian" (section 7.7.4).

CLDR 48 gives the date order of Timor-Leste: the `pt-TL` date `dd/MM/y`. CLDR 49 `currencyData.json` gives Timor-Leste the US dollar. The Banco Central de Timor-Leste names its coins "centavos". The docstring of [`tdt.py`](../../text2spoken/lang/tdt.py) quotes each source.

Each of the 62 rows in `tests/data/tdt.tsv` cites a source. No native speaker has checked the rows.

## Gaps

The file does not read a date with a written month, as `10 Abril 1973`, yet. For a voice that reads written text, the source gives it one reading, in Portuguese. The reading needs a table of the Tetun month names, and no source of the file gives one.

The file does not read a number before a Portuguese noun, as `5 dólares`, yet. Section 7.1 gives it one reading: "if the number quantifies a following head noun, it must be read in the language of that noun." The reading needs a list of the Portuguese nouns of Tetun Dili.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Hau moris iha 10 Abril 1973.` | `tdt-TL` | stays as written |
| `Folin 5 dólares.` | `tdt-TL` | stays as written |

## Limits

The file reads no cardinals. The source gives a cardinal more than one reading, and the written text does not choose one. A cardinal after a noun reads in Tetun when it counts, as `kaixa 7` "kaixa hitu" (seven boxes), and in Portuguese or Indonesian when it labels, as "rejiaun ún" (region one). In television reporting, "Tetun numerals are favoured over Portuguese" (section 10.1).

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Iha kaixa 7.` | `tdt-TL` | stays as written | A cardinal after a noun reads in Tetun when it counts and in a borrowed numeral when it labels. |
| `Iha ema 150.` | `tdt-TL` | stays as written | A cardinal reads in any of the three numeral sets. |
| `Ami tama 8:00, sai 12:30.` | `tdt-TL` | stays as written | No time word stands before the times. |
| `Folin $5 rihun.` | `tdt-TL` | stays as written | A Tetun scale word, as `rihun` (thousand), takes a Tetun numeral. |
| `Orsamentu US$ 2 bilhoens.` | `tdt-TL` | stays as written | `pt-PT` reads no word for ‘billion’ after an amount. |
| `Orsamentu $ 100 mill.` | `tdt-TL` | stays as written | A word that starts with `mil` can mean a thousand, a million or a billion. |
| `Orsamentu tokon $20.` | `tdt-TL` | stays as written | A number after a scale word counts it, and the Portuguese reading of the number alone loses the scale. |
| `Folin $ 3 Milhoens.` | `tdt-TL` | stays as written | A scale word in capitals that `pt-PT` does not list keeps the amount as written. |
| `Data 13/13/2024 la iha.` | `tdt-TL` | stays as written | Month 13 is no date. |

---
[← Russian](ru.md) · [Home](../index.md) · [Chinese →](zh.md)
