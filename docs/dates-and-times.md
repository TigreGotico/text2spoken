# Dates and times

This page shows how text2spoken reads dates, clock times and years, and the options that change the reading.

## Dates

| Written | Tag | Spoken |
| --- | --- | --- |
| `Due 12/03/2024.` | `en-GB` | Due the twelfth of March twenty twenty-four. |
| `Due 12/03/2024.` | `en-US` | Due December third twenty twenty-four. |
| `Due 2024-03-12.` | `en-GB` | Due the twelfth of March twenty twenty-four. |
| `On 14 March 2024.` | `en-GB` | On the fourteenth of March twenty twenty-four. |
| `Book it for the 3rd of May.` | `en-GB` | Book it for the third of May. |
| `Chega a 12/03/2024.` | `pt-PT` | Chega a doze de março de dois mil e vinte e quatro. |
| `Chega a 15 de maio de 2025.` | `pt-PT` | Chega a quinze de maio de dois mil e vinte e cinco. |
| `Am 12.03.2024.` | `de-DE` | Am zwölften März zweitausendvierundzwanzig. |
| `Он родился 12 марта.` | `ru-RU` | Он родился двенадцатого марта. |

An English day-first reading starts with "the". When the text writes "the" right before the date, the reading uses that word and adds no second one.

A date with the year last is ambiguous when both other fields are 12 or below. The `date_order` option decides it, and its default comes from the variety. A field above 12 is always the day:

| Written | Spoken (`en-GB`) | Spoken (`en-GB`, `date_order="MDY"`) |
| --- | --- | --- |
| `Due 12/03/2024.` | Due the twelfth of March twenty twenty-four. | Due the third of December twenty twenty-four. |
| `Due 13/03/2024.` | Due the thirteenth of March twenty twenty-four. | Due the thirteenth of March twenty twenty-four. |

A date that does not exist stays as written:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `On 13/13/2024 nothing happened.` | stays as written |

## Clock times

| Written | Tag | Spoken |
| --- | --- | --- |
| `Meet at 7:30 pm.` | `en-US` | Meet at seven thirty PM. |
| `Meet at 9am.` | `en-GB` | Meet at nine AM. |
| `Meet at 14:30.` | `en-GB` | Meet at two thirty PM. |
| `Encontro às 14:30.` | `pt-PT` | Encontro às catorze e trinta. |
| `Encontro às 14h30.` | `pt-PT` | Encontro às catorze horas e trinta minutos. |
| `Chego à 0:00.` | `pt-PT` | Chego à meia-noite. |

A time needs evidence that it is a time: a time word before it, such as `at` or `às`, a day period such as `pm`, or a mark that only a time has, such as the `h` of `14h30`. With no evidence, the text stays as written, because `16:9` is a ratio and `3:16` is a verse:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `The ratio is 16:9 here.` | stays as written |
| `Read John 3:16 again.` | stays as written |
| `The run took 1:23:45.` | stays as written |

The `clock` option chooses the 12-hour or the 24-hour reading, and `minute_style` chooses between a number and a phrase for the minutes:

| Written | Spoken (`en-GB`) | Spoken (`en-GB`, `clock="24h"`) | Spoken (`en-GB`, `minute_style="phrase"`) |
| --- | --- | --- | --- |
| `Meet at 14:30.` | Meet at two thirty PM. | Meet at fourteen thirty. | Meet at half past two PM. |
| `Meet at 2:30.` | Meet at two thirty. | Meet at two thirty. | Meet at half past two. |

A language reads only the values that it can produce. A value that it cannot produce gives a warning, and the default applies. [Errors and warnings](errors.md#a-param-value-that-the-language-cannot-produce) shows the case.

## Years

German, English and Russian read a year when a word or a suffix marks it. A number with no such mark reads as a cardinal:

| Written | Tag | Spoken |
| --- | --- | --- |
| `It happened in 1999.` | `en-GB` | It happened in nineteen ninety-nine. |
| `Das war im Jahr 1999.` | `de-DE` | Das war im Jahr neunzehnhundertneunundneunzig. |
| `Er wurde 1999 geboren.` | `de-DE` | Er wurde eintausendneunhundertneunundneunzig geboren. |

---
[← Numbers](numbers.md) · [Home](index.md) · [Money, units and symbols →](money-units-and-symbols.md)
